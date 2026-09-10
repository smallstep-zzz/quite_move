"""Quiet Move Simulator — 정적 사이트 생성기

output/*.md 를 HTML로 렌더링해 docs/ (GitHub Pages 최상위)에 생성합니다.
    python build_site.py
생성 후 docs/ 를 커밋하고 GitHub Pages 소스를 /docs 로 설정하면 바로 게시됩니다.
"""

import os
import re

import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SITE_DIR = os.path.join(BASE_DIR, "docs")

COLUMNS = {
    1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H",
    9: "I", 10: "J", 11: "K", 12: "L", 13: "M", 14: "N", 15: "O",
    16: "P", 17: "Q",
}
DESC = {
    1: "살아가는 세계의 조건", 2: "대표 페르소나 15", 3: "시작 시점 정신 상태",
    4: "7일 일상 트레이스", 5: "감정·기분 타임라인", 6: "기억 누적과 재활성화",
    7: "행동 전환점", 8: "자기강화 루프", 9: "깊은 인과 사슬", 10: "인과 분기 지도",
    11: "행동·감정·사회 비용", 12: "작은 개입점 6개", 13: "최소 제품 명세",
    14: "개입 전후 비교", 15: "페르소나 재현성", 16: "지역 차이", 17: "사실·가정·한계",
}
SECTION_TITLE = {
    1: "World State", 2: "Persona Matrix", 3: "Persona State",
    4: "Daily Simulation Trace", 5: "Mental State Timeline",
    6: "Memory Accumulation", 7: "Turning Points", 8: "Interaction Loops",
    9: "Deep Causal Chains", 10: "Branch Map", 11: "Friction Map",
    12: "Quiet Moves", 13: "Minimal Products", 14: "Counterfactual Results",
    15: "Cross-Persona Validation", 16: "Cross-Region Validation",
    17: "Assumptions / Unknowns",
}

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]
)


def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def list_docs():
    docs = []
    for fn in sorted(os.listdir(OUTPUT_DIR), key=natural_key):
        if fn.endswith(".md"):
            docs.append(fn)
    return docs


def extract_title(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return os.path.basename(path)


def render_markdown(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def fix_links(html: str) -> str:
    def repl(m):
        target = m.group(1)
        if target.endswith(".md"):
            page = target[:-3]
            if page == "00_index":
                page = "index"
            return f'href="{page}.html"'
        return m.group(0)

    return re.sub(r'href="([^"]+)"', repl, html)


def build_sidebar(files, current_page):
    items = []
    for fn in files:
        code, page = nav_of(fn)
        cls = "active" if page == current_page else ""
        title = extract_title(os.path.join(OUTPUT_DIR, fn))
        items.append(
            f'<a class="{cls}" href="{page}.html">'
            f'<span class="code">{code}</span> {title}</a>'
        )
    return "\n".join(items)


def nav_of(fn: str) -> tuple:
    """('A', '01_world_state') 형태를 반환 (index는 ('–','index'))."""
    number = fn.split("_", 1)[0]
    if number == "00":
        return "–", "index"
    return COLUMNS.get(int(number), number), fn[:-3]


def build_pager(files, current_page):
    pages = [(nav_of(f), n) for n, f in enumerate(files)]
    idx = next((i for i, (_, f) in enumerate(pages) if _[1] == current_page), None)
    out = []
    if idx and idx > 0:
        prev = files[idx - 1]
        out.append(
            f'<a class="prev" href="{prev[:-3]}.html"><span class="cap">‹ 이전</span> '
            f'{extract_title(os.path.join(OUTPUT_DIR, prev))}</a>'
        )
    if idx is not None and idx < len(files) - 1:
        nxt = files[idx + 1]
        out.append(
            f'<a class="next" href="{nxt[:-3]}.html"><span class="cap">다음 ›</span> '
            f'{extract_title(os.path.join(OUTPUT_DIR, nxt))}</a>'
        )
    return f'<div class="pager">{"".join(out)}</div>' if out else ""


LAYOUT = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — Quiet Move Simulator</title>
<meta name="description" content="__DESC__">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="layout">
  <aside>
    <div class="brand"><span class="dot"></span><span><a href="index.html">Quiet Move Simulator</a></span></div>
    <small>대한민국 2026 · 수능 D-66</small>
    <input class="search" type="search" placeholder="문서 검색…" oninput="filterDocs(this.value)">
    <nav id="doc-nav">__NAV__</nav>
    <div class="toc"><h4>이 문서 목차</h4><ul id="toc"></ul></div>
  </aside>
  <main>
    <div class="doc-head">
      <div class="crumbs">Quiet Move Simulator / __NAV_TITLE__</div>
      <h1>__H1__</h1>
      <div class="meta">__META__</div>
    </div>
    <div class="toolbar">
      <button onclick="window.print()">인쇄 / PDF</button>
      <button onclick="toggleCode()">코드 블록 줄바꿈</button>
      <a href="__RAW__" download><button>원본 MD</button></a>
    </div>
    <article class="article" id="article">__CONTENT__</article>
    __PAGER__
  </main>
</div>
<script src="app.js"></script>
</body>
</html>
"""

STYLE = """
:root { --ink:#233; --muted:#6b7785; --line:#e4e8ee; --bg:#f6f8fa; --card:#fff;
        --accent:#3b6ea5; --accent2:#7a5cb8; --code-bg:#f0f2f5; }
* { box-sizing:border-box; }
html,body { margin:0; padding:0; }
body { font-family:"Apple SD Gothic Neo","Malgun Gothic",-apple-system,"Segoe UI",Roboto,sans-serif;
       color:var(--ink); background:var(--bg); line-height:1.7; font-size:15px; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.layout { display:flex; min-height:100vh; }

aside { width:280px; flex:0 0 280px; background:#0f1b2d; color:#c9d4e3;
        position:sticky; top:0; height:100vh; overflow-y:auto; padding:18px 14px 40px; }
aside .brand { display:flex; align-items:center; gap:8px; font-weight:700; font-size:15px; }
aside .brand .dot { width:10px; height:10px; border-radius:50%; background:#63d3a8; }
aside .brand a { color:#fff; }
aside > small { display:block; color:#7e8ea6; font-size:11px; margin:4px 0 12px; }
.search { width:100%; margin:0 0 8px; padding:8px 10px; border-radius:8px; border:1px solid #2a3b55;
          background:#16233a; color:#e6ecf5; font-size:13px; outline:none; }
aside nav a { display:block; padding:6px 9px; border-radius:7px; color:#b9c6d8; font-size:13px;
              white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-bottom:1px; }
aside nav a:hover { background:#1b2b46; color:#fff; text-decoration:none; }
aside nav a.active { background:#274b7c; color:#fff; font-weight:600; }
aside nav a .code { display:inline-block; min-width:36px; color:#7fa6d0; font-size:11px; font-weight:700; }
aside .toc { margin-top:16px; border-top:1px solid #22334d; padding-top:12px; }
aside .toc h4 { margin:0 0 8px; font-size:11px; letter-spacing:.08em; color:#7e8ea6; text-transform:uppercase; }
aside .toc ul { list-style:none; margin:0; padding:0; }
aside .toc li a { display:block; font-size:12.5px; padding:3px 8px; color:#9fb0c6; border-left:2px solid transparent; }
aside .toc li a:hover { color:#fff; }
aside .toc li.l2 a { color:#7e8ea6; font-size:12px; padding-left:20px; }
aside .toc a.current { color:#fff; border-left-color:#63d3a8; background:#1b2b46; border-radius:4px; }

main { flex:1; min-width:0; padding:34px 48px 80px; }
.doc-head { max-width:880px; margin:0 auto 20px; }
.doc-head .crumbs { font-size:12px; color:var(--muted); }
.doc-head h1 { font-size:28px; margin:6px 0 2px; line-height:1.25; }
.doc-head .meta { font-size:12.5px; color:var(--muted); }

.article { max-width:880px; margin:0 auto; background:var(--card); padding:34px 42px;
           border-radius:12px; border:1px solid var(--line); box-shadow:0 1px 2px rgba(16,32,64,.05); }
.article h1 { font-size:24px; border-bottom:3px solid var(--accent); padding-bottom:8px; margin:10px 0 18px; }
.article h2 { font-size:20px; margin-top:34px; padding-bottom:6px; border-bottom:1px solid var(--line); }
.article h3 { font-size:16.5px; margin-top:26px; }
.article h4 { font-size:14.5px; margin-top:20px; color:#33455c; }
.article p { margin:12px 0; }
.article ul,.article ol { padding-left:24px; }
.article li { margin:5px 0; }
.article blockquote { background:#f0f6fd; border-left:4px solid var(--accent); margin:14px 0;
                      padding:10px 16px; color:#3a4a5e; border-radius:0 8px 8px 0; font-size:14px; }
.article pre { background:var(--code-bg); padding:14px 16px; border-radius:8px; overflow-x:auto;
               border:1px solid var(--line); font-size:13px; line-height:1.55; }
.article pre.expand { white-space:pre-wrap; word-break:break-word; }
.article code { font-family:"Cascadia Code",Consolas,monospace; background:var(--code-bg);
                padding:1px 5px; border-radius:4px; font-size:13px; color:#b5487a; }
.article pre code { background:none; padding:0; color:var(--ink); }
.article table { border-collapse:collapse; width:100%; margin:16px 0; font-size:13.5px;
                 display:block; overflow-x:auto; }
.article th { background:#eef2f7; text-align:left; font-weight:600; }
.article th,.article td { border:1px solid var(--line); padding:7px 10px; vertical-align:top; }
.article tr:nth-child(even) td { background:#fafbfd; }
.article img { max-width:100%; }
.article hr { border:none; border-top:1px solid var(--line); margin:26px 0; }

.toolbar { max-width:880px; margin:0 auto 14px; display:flex; gap:8px; justify-content:flex-end; }
.toolbar button { font-size:12.5px; padding:6px 12px; border-radius:7px; cursor:pointer;
                  border:1px solid var(--line); background:var(--card); color:var(--ink); }
.toolbar button:hover { border-color:var(--accent); }
.toolbar a { text-decoration:none; }

.pager { max-width:880px; margin:24px auto 0; display:flex; gap:10px; }
.pager a { flex:1; background:var(--card); border:1px solid var(--line); border-radius:10px;
           padding:12px 16px; font-size:13.5px; }
.pager a:hover { border-color:var(--accent); text-decoration:none; }
.pager .next { text-align:right; }
.pager .cap { display:block; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; }

.grid { max-width:880px; margin:24px auto 0; display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:12px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:11px; padding:13px 15px; }
.card:hover { border-color:var(--accent); text-decoration:none; }
.card .code { font-weight:700; color:var(--accent2); font-size:12px; }
.card .tt { font-weight:600; font-size:14px; margin:3px 0; color:var(--ink); }
.card .ds { font-size:12px; color:var(--muted); }

@media print { aside,.pager,.toolbar { display:none !important; } body { background:#fff; }
               main { padding:0; } .article { border:none; box-shadow:none; } }
"""

SCRIPT = """(() => {
function filterDocs(q) {
  q = q.toLowerCase();
  document.querySelectorAll('#doc-nav a').forEach(a => {
    a.style.display = a.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}
window.filterDocs = filterDocs;
function toggleCode() {
  document.querySelectorAll('.article pre').forEach(p => p.classList.toggle('expand'));
}
window.toggleCode = toggleCode;

const toc = document.getElementById('toc');
const art = document.getElementById('article');
if (toc && art) {
  const hs = Array.prototype.slice.call(art.querySelectorAll('h2, h3'));
  hs.forEach((h, i) => {
    if (!h.id) h.id = 'h-' + i;
    const li = document.createElement('li');
    li.className = h.tagName === 'H3' ? 'l2' : 'l1';
    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent;
    li.appendChild(a);
    toc.appendChild(li);
  });
  function active() {
    let cur = hs[0];
    hs.forEach(h => { if (h.getBoundingClientRect().top <= 90) cur = h; });
    const c = toc.querySelector('a.current');
    if (c) c.classList.remove('current');
    hs.forEach(h => { if (h === cur) { const l = toc.querySelector('a[href="#' + h.id + '"]'); if (l) l.classList.add('current'); } });
  }
  window.addEventListener('scroll', active, { passive: true });
  active();
}
})();
"""


def shell(title, desc, nav_title, h1, meta, content, pager, raw_link, files, current_page):
    html = LAYOUT
    html = html.replace("__TITLE__", title)
    html = html.replace("__DESC__", desc)
    html = html.replace("__NAV_TITLE__", nav_title)
    html = html.replace("__H1__", h1)
    html = html.replace("__META__", meta)
    html = html.replace("__NAV__", build_sidebar(files, current_page))
    html = html.replace("__CONTENT__", fix_links(content))
    html = html.replace("__PAGER__", build_pager(files, current_page))
    html = html.replace("__RAW__", raw_link)
    return html


def write_cards(files) -> str:
    cards = []
    for fn in files:
        if fn == "00_index.md":
            continue
        number = int(fn.split("_", 1)[0])
        cards.append(
            f'<a class="card" href="{fn[:-3]}.html"><span class="code">{COLUMNS[number]}</span>'
            f'<div class="tt">{extract_title(os.path.join(OUTPUT_DIR, fn))}</div>'
            f'<div class="ds">{DESC.get(number, "")}</div></a>'
        )
    return f'<div class="grid">{"".join(cards)}</div>'


def main():
    files = list_docs()
    os.makedirs(SITE_DIR, exist_ok=True)

    with open(os.path.join(SITE_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(STYLE)
    with open(os.path.join(SITE_DIR, "app.js"), "w", encoding="utf-8") as f:
        f.write(SCRIPT)

    built = []
    for fn in files:
        src = os.path.join(OUTPUT_DIR, fn)
        raw = open(src, encoding="utf-8").read()
        title = extract_title(src)
        number = fn.split("_", 1)[0]
        if fn == "00_index.md":
            page, nav_title = "index", "Index"
            content = render_markdown(raw) + write_cards(files)
            h1, meta = "Quiet Move Simulator", \
                "Simulation Outputs A~Q · 7일 트레이스 · 15 페르소나"
            html = shell("Quiet Move Simulator — 인덱스", title, nav_title, h1, meta,
                         content, "", "00_index.md", files, "index")
        else:
            code = int(number)
            page = fn[:-3]
            content = render_markdown(raw)
            h1 = title
            nav_title = f"출력 {COLUMNS[code]} · {SECTION_TITLE[code]}"
            meta = f"출력 {COLUMNS[code]} ({SECTION_TITLE[code]}) · 대한민국 2026 · 수능 D-66"
            html = shell(f"{COLUMNS[code]} · {title}", title, nav_title, h1, meta,
                         content, build_pager(files, page), fn, files, page)

        with open(os.path.join(SITE_DIR, f"{page}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        built.append(f"{page}.html")

    # 원본 MD도 docs/에 복사 (원본 MD 버튼용, 링크 상대경로 유지)
    import shutil
    for fn in files:
        shutil.copy(os.path.join(OUTPUT_DIR, fn), os.path.join(SITE_DIR, fn))

    print(f"생성 완료: docs/ ({len(built)} 페이지)")
    for b in built:
        print("  -", b)


if __name__ == "__main__":
    main()