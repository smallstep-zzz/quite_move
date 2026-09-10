"""Quiet Move Simulator — 정적 사이트 생성기

두 섹션의 마크다운을 HTML로 렌더링해 docs/ (GitHub Pages 최상위)에 생성합니다.
    python build_site.py

섹션:
  v1 = output/      일상 시뮬레이션 (A~Q 산출물)
  v2 = output_v2/   취미·여가 심층 리서치 (Domain 01~06)

생성 후 docs/ 를 커밋하고 GitHub Pages 소스를 /docs 로 설정하면 바로 게시됩니다.
"""

import os
import re
import shutil

import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(BASE_DIR, "docs")

V1_TITLE = {
    1: "World State", 2: "Persona Matrix", 3: "Persona State",
    4: "Daily Simulation Trace", 5: "Mental State Timeline",
    6: "Memory Accumulation", 7: "Turning Points", 8: "Interaction Loops",
    9: "Deep Causal Chains", 10: "Branch Map", 11: "Friction Map",
    12: "Quiet Moves", 13: "Minimal Products", 14: "Counterfactual Results",
    15: "Cross-Persona Validation", 16: "Cross-Region Validation",
    17: "Assumptions / Unknowns",
}
V1_CODE = {n: chr(64 + n) for n in range(1, 18)}  # 1->A ... 17->Q
V1_DESC = {
    1: "살아가는 세계의 조건", 2: "대표 페르소나 15", 3: "시작 시점 정신 상태",
    4: "7일 일상 트레이스", 5: "감정·기분 타임라인", 6: "기억 누적과 재활성화",
    7: "행동 전환점", 8: "자기강화 루프", 9: "깊은 인과 사슬", 10: "인과 분기 지도",
    11: "행동·감정·사회 비용", 12: "작은 개입점 6개", 13: "최소 제품 명세",
    14: "개입 전후 비교", 15: "페르소나 재현성", 16: "지역 차이", 17: "사실·가정·한계",
}
V2_DESC = {
    1: "강한 수집 욕구 + 투자(시세)", 2: "실시간 경쟁(복기 루프)",
    3: "현장 활동(출조 준비)", 4: "반복 구매(사이즈·위시)",
    5: "자기계발(기록·크루)", 6: "Quiet Move 교차 비교 + Quietness Score",
}
V2_CODE = {n: f"{n:02d}" for n in range(1, 7)}

SECTIONS = [
    {
        "dir": os.path.join(BASE_DIR, "output"),
        "name": "v1",
        "label": "v1 · 일상 시뮬레이션 (A~Q)",
        "desc": V1_DESC, "code": V1_CODE, "title": V1_TITLE,
    },
    {
        "dir": os.path.join(BASE_DIR, "output_v2"),
        "name": "v2",
        "label": "v2 · 취미·여가 심층 리서치",
        "desc": V2_DESC, "code": V2_CODE, "title": {},
    },
]

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]
)


def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


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


def section_docs(sec) -> list:
    docs = []
    for fn in sorted(os.listdir(sec["dir"]), key=natural_key):
        if not fn.endswith(".md") or fn == "00_index.md":
            continue
        number = int(fn.split("_", 1)[0])
        page = fn[:-3]
        docs.append({
            "file": fn, "page": page, "number": number,
            "code": sec["code"].get(number, f"{number:02d}"),
            "title": extract_title(os.path.join(sec["dir"], fn)),
        })
    return docs


def section_cards(sec) -> str:
    cards = []
    for d in section_docs(sec):
        cards.append(
            f'<a class="card" href="{d["page"]}.html">'
            f'<span class="code">{d["code"]}</span>'
            f'<div class="tt">{d["title"]}</div>'
            f'<div class="ds">{sec["desc"].get(d["number"], "")}</div></a>'
        )
    return f'<div class="grid">{"".join(cards)}</div>'


def build_sidebar(sections, current_page=None) -> str:
    items = ['<a class="home" href="index.html"><span class="code">🏠</span> 홈 · 두 섹션 보기</a>']
    for sec in sections:
        items.append(f'<div class="sec-label">{sec["label"]}</div>')
        for d in section_docs(sec):
            cls = "active" if d["page"] == current_page else ""
            items.append(
                f'<a class="{cls}" href="{d["page"]}.html">'
                f'<span class="code">{d["code"]}</span> {d["title"]}</a>'
            )
    return "\n".join(items)


def build_pager(sec, current_page) -> str:
    docs = section_docs(sec)
    idx = next((i for i, d in enumerate(docs) if d["page"] == current_page), None)
    if idx is None:
        return ""
    out = []
    if idx > 0:
        p = docs[idx - 1]
        out.append(f'<a class="prev" href="{p["page"]}.html">'
                   f'<span class="cap">‹ {(sec["label"].split("·")[0]).strip()}</span> {p["title"]}</a>')
    if idx < len(docs) - 1:
        n = docs[idx + 1]
        out.append(f'<a class="next" href="{n["page"]}.html">'
                   f'<span class="cap">다음 ›</span> {n["title"]}</a>')
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
    <small>대한민국 2026 · 시뮬레이션 + 심층 리서치</small>
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
    __TOOLBAR__
    <article class="article" id="article">__CONTENT__</article>
    __PAGER__
  </main>
</div>
<script src="app.js"></script>
</body>
</html>
"""

TOOLBAR = """<div class="toolbar">
  <button onclick="window.print()">인쇄 / PDF</button>
  <button onclick="toggleCode()">코드 블록 줄바꿈</button>
  <a href="__RAW__" download><button>원본 MD</button></a>
</div>"""

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

aside { width:290px; flex:0 0 290px; background:#0f1b2d; color:#c9d4e3;
        position:sticky; top:0; height:100vh; overflow-y:auto; padding:18px 14px 40px; }
aside .brand { display:flex; align-items:center; gap:8px; font-weight:700; font-size:15px; }
aside .brand .dot { width:10px; height:10px; border-radius:50%; background:#63d3a8; }
aside .brand a { color:#fff; }
aside > small { display:block; color:#7e8ea6; font-size:11px; margin:4px 0 12px; }
.search { width:100%; margin:0 0 8px; padding:8px 10px; border-radius:8px; border:1px solid #2a3b55;
          background:#16233a; color:#e6ecf5; font-size:13px; outline:none; }
aside nav a, aside nav a.home { display:block; padding:6px 9px; border-radius:7px; color:#b9c6d8;
          font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-bottom:1px; }
aside nav a:hover, aside nav a.home:hover { background:#1b2b46; color:#fff; text-decoration:none; }
aside nav a.active { background:#274b7c; color:#fff; font-weight:600; }
aside nav a .code { display:inline-block; min-width:36px; color:#7fa6d0; font-size:11px; font-weight:700; }
aside nav a.active .code { color:#bfd8f2; }
aside .sec-label { margin:14px 0 4px; font-size:11px; letter-spacing:.06em; color:#6f829c;
                   text-transform:uppercase; border-top:1px solid #22334d; padding-top:10px; }
aside .sec-label:first-of-type { margin-top:6px; }
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
.article + .article { margin-top:28px; }
.section-tag { display:inline-block; background:#0f1b2d; color:#fff; padding:6px 14px;
               border-radius:999px; font-size:13px; font-weight:600; margin-bottom:16px; }
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

.grid { margin:22px 0 0; display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:12px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:11px; padding:13px 15px; display:block; }
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
    const match = a.textContent.toLowerCase().includes(q);
    a.style.display = match ? '' : 'none';
    if (/^sec/.test(a.className)) return;
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


def page_html(sec, d, raw_md) -> str:
    src = os.path.join(sec["dir"], d["file"])
    raw = open(src, encoding="utf-8").read()
    title = d["title"]
    content = render_markdown(raw)
    if sec["name"] == "v1":
        nav_title = f"출력 {d['code']} · {sec['title'][d['number']]}"
        meta = f"출력 {d['code']} ({sec['title'][d['number']]}) · 대한민국 2026 · 수능 D-66"
        tab = f"{d['code']} · {title}"
    else:
        nav_title = f"v2 · Domain {d['number']:02d}"
        meta = f"v2 심층 리서치 · {title} · WORLD FACT / REFLECTION 태그"
        tab = f"Domain {d['number']:02d} · {title}"

    html = LAYOUT
    html = html.replace("__TITLE__", tab + " — Quiet Move Simulator")
    html = html.replace("__DESC__", title)
    html = html.replace("__NAV_TITLE__", nav_title)
    html = html.replace("__H1__", title)
    html = html.replace("__META__", meta)
    html = html.replace("__NAV__", build_sidebar(SECTIONS, current_page=d["page"]))
    html = html.replace("__TOOLBAR__", TOOLBAR.replace("__RAW__", raw_md))
    html = html.replace("__CONTENT__", fix_links(content))
    html = html.replace("__PAGER__", build_pager(sec, d["page"]))
    return html


def main():
    os.makedirs(SITE_DIR, exist_ok=True)
    with open(os.path.join(SITE_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(STYLE)
    with open(os.path.join(SITE_DIR, "app.js"), "w", encoding="utf-8") as f:
        f.write(SCRIPT)

    built = []
    for sec in SECTIONS:
        for d in section_docs(sec):
            html = page_html(sec, d, d["file"])
            with open(os.path.join(SITE_DIR, f"{d['page']}.html"), "w", encoding="utf-8") as f:
                f.write(html)
            built.append(f"{d['page']}.html")
        for fn in os.listdir(sec["dir"]):
            if fn.endswith(".md"):
                shutil.copy(os.path.join(sec["dir"], fn), os.path.join(SITE_DIR, fn))

    # 홈페이지: 두 섹션 인덱스(00_index.md) + 카드
    blocks = []
    for sec in SECTIONS:
        content = render_markdown(open(os.path.join(sec["dir"], "00_index.md"), encoding="utf-8").read())
        blocks.append(
            f'<div class="section-tag">{sec["label"]}</div>'
            f'{fix_links(content)}'
            f'{section_cards(sec)}'
        )
    home_content = f'<article class="article" id="article">' + "".join(blocks) + "</article>"

    home = LAYOUT
    home = home.replace("__TITLE__", "Quiet Move Simulator — 홈")
    home = home.replace("__DESC__", "v1 일상 시뮬레이션 + v2 취미·여가 심층 리서치")
    home = home.replace("__NAV_TITLE__", "Home")
    home = home.replace("__H1__", "Quiet Move Simulator")
    home = home.replace("__META__", "두 섹션 · v1 시뮬레이션 A~Q / v2 취미·여가 심층 Domain 01~06")
    home = home.replace("__NAV__", build_sidebar(SECTIONS))
    home = home.replace("__TOOLBAR__", "")
    home = home.replace("__CONTENT__", home_content)
    home = home.replace("__PAGER__", "")
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(home)
    built.append("index.html")

    print(f"생성 완료: docs/ ({len(built)} 페이지)")
    for b in built:
        print("  -", b)


if __name__ == "__main__":
    main()