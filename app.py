"""Quiet Move Simulator — Flask 뷰어 (v1/v2 섹션 분리)

v1 (output/)   : 일상 시뮬레이션 — 가정·취업·직장 관련 A~Q 산출물
v2 (output_v2/): 특수 분야 심층 — 포켓몬 카드·LOL·낚시·패션·러닝 (A~M×분야)

- /                 : 인덱스 (v1/v2 각각 카드 목록)
- /view/<doc>       : v1 문서 보기 / /v2/<doc>     : v2 문서 보기
- /raw/<doc>        : v1 원문   / /v2/raw/<doc>    : v2 원문
"""

import os
import re

import markdown
from flask import Flask, Response, abort, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
V2_DIR = os.path.join(BASE_DIR, "output_v2")

app = Flask(__name__)

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]
)

GROUPS = [
    {
        "key": "v1",
        "label": "v1 · 일상 시뮬레이션",
        "note": "가정·취업·직장 · A~Q 산출물",
        "dir": OUTPUT_DIR,
        "prefix": "",
        "view_func": "view",
        "desc": {
            "00": "목차", "01": "살아가는 세계의 조건", "02": "대표 페르소나 15",
            "03": "시작 시점 정신 상태", "04": "7일 일상 트레이스", "05": "감정·기분 타임라인",
            "06": "기억 누적과 재활성화", "07": "행동 전환점", "08": "자기강화 루프",
            "09": "깊은 인과 사슬", "10": "인과 분기 지도", "11": "행동·감정·사회 비용",
            "12": "작은 개입점 6개", "13": "최소 제품 명세", "14": "개입 전후 비교",
            "15": "페르소나 재현성", "16": "지역 차이", "17": "사실·가정·한계",
        },
    },
    {
        "key": "v2",
        "label": "v2 · 특수 분야 심층",
        "note": "분야별 A~M · Quiet Move v2",
        "dir": V2_DIR,
        "prefix": "/v2",
        "view_func": "v2_view",
        "desc": {
            "00": "v2 목차·운영 원칙", "01": "포켓몬 카드(수집·시세)",
            "02": "LOL(실시간 경쟁·복기)", "03": "낚시(현장·출조 준비)",
            "04": "패션 쇼핑(반복 구매)", "05": "러닝(자기계발·기록)",
            "06": "교차 비교·Quietness Score",
        },
    },
]


def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def list_docs(directory: str):
    docs = []
    if not os.path.isdir(directory):
        return docs
    for fn in sorted(os.listdir(directory), key=natural_key):
        if fn.endswith(".md"):
            docs.append({"file": fn, "title": extract_title(os.path.join(directory, fn))})
    return docs


def extract_title(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return os.path.basename(path)


def render_markdown(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def read_doc(group_dir: str, doc: str):
    safe = os.path.basename(doc)
    if not safe.endswith(".md") or safe.startswith("."):
        abort(404)
    path = os.path.join(group_dir, safe)
    if not os.path.isfile(path):
        abort(404)
    with open(path, encoding="utf-8") as f:
        return safe, f.read()


STYLE = """
:root { --ink:#233; --muted:#6b7785; --line:#e4e8ee; --bg:#f6f8fa; --card:#fff;
        --accent:#3b6ea5; --accent2:#7a5cb8; --v2:#b06500; --code-bg:#f0f2f5; }
* { box-sizing:border-box; }
html,body { margin:0; padding:0; }
body { font-family:"Apple SD Gothic Neo","Malgun Gothic",-apple-system,"Segoe UI",Roboto,sans-serif;
       color:var(--ink); background:var(--bg); line-height:1.7; font-size:15px; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.layout { display:flex; min-height:100vh; }

aside { width:290px; flex:0 0 290px; background:#0f1b2d; color:#c9d4e3;
        position:sticky; top:0; height:100vh; overflow-y:auto; padding:18px 14px 40px; }
aside .brand { display:flex; align-items:center; gap:8px; color:#fff; font-weight:700; font-size:15px; }
aside .brand .dot { width:10px; height:10px; border-radius:50%; background:#63d3a8; }
aside > small { display:block; color:#7e8ea6; font-size:11px; margin:4px 0 12px; }
.search { width:100%; margin:0 0 10px; padding:8px 10px; border-radius:8px; border:1px solid #2a3b55;
          background:#16233a; color:#e6ecf5; font-size:13px; outline:none; }
.grp-head { display:flex; flex-direction:column; padding:8px 6px 4px; margin-top:8px;
            color:#e8eef7; font-size:12px; font-weight:700; letter-spacing:.02em;
            border-bottom:1px solid #22334d; }
.grp-head small { color:#7e8ea6; font-weight:400; font-size:10.5px; margin-top:2px; }
.grp-head .tag { font-size:10px; border-radius:4px; padding:1px 6px; margin-right:6px; }
.tag-v1 { background:#274b7c; color:#bcd2ee; }
.tag-v2 { background:#7a4a12; color:#f0c58a; }
#doc-nav a { display:block; padding:6px 9px; border-radius:7px; color:#b9c6d8; font-size:13px;
             white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-bottom:1px; }
#doc-nav a:hover { background:#1b2b46; color:#fff; text-decoration:none; }
#doc-nav a.active { background:#274b7c; color:#fff; font-weight:600; }
#doc-nav a.active-v2 { background:#7a4a12; color:#fff; font-weight:600; }
#doc-nav a .code { display:inline-block; min-width:36px; color:#7fa6d0; font-size:11px; font-weight:700; }
#doc-nav a.active .code, #doc-nav a.active-v2 .code { color:#fff; }
aside .toc { margin-top:14px; border-top:1px solid #22334d; padding-top:12px; }
aside .toc h4 { margin:0 0 8px; font-size:11px; letter-spacing:.08em; color:#7e8ea6; text-transform:uppercase; }
aside .toc ul { list-style:none; margin:0; padding:0; }
aside .toc li a { display:block; font-size:12.5px; padding:3px 8px; color:#9fb0c6; border-left:2px solid transparent; }
aside .toc li a:hover { color:#fff; }
aside .toc li.l2 a { color:#7e8ea6; font-size:12px; padding-left:20px; }
aside .toc a.current { color:#fff; border-left-color:#63d3a8; background:#1b2b46; border-radius:4px; }

main { flex:1; min-width:0; padding:34px 48px 80px; }
.doc-head { max-width:880px; margin:0 auto 20px; }
.doc-head .crumbs { font-size:12px; color:var(--muted); }
.doc-head .chrome { display:inline-block; font-size:10px; font-weight:700; border-radius:5px;
                    padding:2px 8px; margin-right:6px; vertical-align:2px; }
.chrome-v1 { background:#274b7c; color:#fff; }
.chrome-v2 { background:#b06500; color:#fff; }
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

.section-block { max-width:880px; margin:0 auto 26px; }
.section-block h2 { font-size:18px; display:flex; align-items:center; gap:8px; margin:0 0 4px; }
.section-block h2 .tag { font-size:12px; border-radius:6px; padding:2px 8px; }
.section-block .note { font-size:12px; color:var(--muted); margin:0 0 12px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:12px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:11px; padding:13px 15px; }
.card:hover { border-color:var(--accent); text-decoration:none; }
.card .code { font-weight:700; color:var(--accent2); font-size:12px; }
.card.v2 .code { color:var(--v2); }
.card .tt { font-weight:600; font-size:14px; margin:3px 0; color:var(--ink); }
.card .ds { font-size:12px; color:var(--muted); }

@media print { aside,.pager,.toolbar { display:none !important; } body { background:#fff; }
               main { padding:0; } .article { border:none; box-shadow:none; } }
"""

LAYOUT = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — Quiet Move Simulator</title>
<style>__STYLE__</style>
</head>
<body>
<div class="layout">
  <aside>
    <div class="brand"><span class="dot"></span><span>Quiet Move Simulator</span></div>
    <small>대한민국 2026 · 수능 D-66 · 분야 심층</small>
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
<script>
function filterDocs(q){q=q.toLowerCase();
  document.querySelectorAll('#doc-nav a').forEach(a=>{
    a.style.display=a.textContent.toLowerCase().includes(q)?'':'none';});}
function toggleCode(){document.querySelectorAll('.article pre').forEach(p=>
  p.classList.toggle('expand'));}
(function(){
  var toc=document.getElementById('toc');
  var art=document.getElementById('article');
  if(!toc||!art)return;
  var hs=arr(art.querySelectorAll('h2,h3'));
  hs.forEach(function(h,i){ if(!h.id){h.id='h-'+i;}
    var li=document.createElement('li');
    li.className=(h.tagName==='H3')?'l2':'l1';
    var a=document.createElement('a');
    a.href='#'+h.id; a.textContent=h.textContent;
    li.appendChild(a); toc.appendChild(li); });
  function active(){ var cur=hs[0];
    hs.forEach(function(h){ if(h.getBoundingClientRect().top<=90){cur=h;} });
    var c=toc.querySelector('a.current'); if(c){c.classList.remove('current');}
    hs.forEach(function(h){ if(h===cur){ toc.querySelector('a[href="#'+h.id+'"]').classList.add('current'); } });
  }
  window.addEventListener('scroll',active,{passive:true}); active();
})();
function arr(nl){return Array.prototype.slice.call(nl);}
</script>
</body>
</html>"""


def build_sidebar(active_group_key=None, active_file=None):
    blocks = []
    for g in GROUPS:
        heads = [f'<div class="grp-head">'
                 f'<span><span class="tag tag-{g["key"]}">{g["key"]}</span>{g["label"]}</span>'
                 f'<small>{g["note"]}</small></div>']
        for d in list_docs(g["dir"]):
            cls = "active" if (g["key"] == active_group_key and d["file"] == active_file) else ""
            if active_group_key == g["key"] and d["file"] == active_file:
                cls = "active-v2" if g["key"] == "v2" else "active"
            href = url_for(g["view_func"], doc=d["file"])
            code = d["file"].split("_", 1)[0]
            heads.append(
                f'<a class="{cls}" href="{href}">'
                f'<span class="code">{code}</span> {d["title"]}</a>'
            )
        blocks.append("<div class='grp'>" + "".join(heads) + "</div>")
    return "".join(blocks)


def build_pager(group, docs, idx):
    out = []
    if idx > 0:
        p = docs[idx - 1]
        out.append(f'<a class="prev" href="{url_for(group["view_func"], doc=p["file"])}">'
                   f'<span class="cap">‹ 이전</span> {p["title"]}</a>')
    if idx < len(docs) - 1:
        n = docs[idx + 1]
        out.append(f'<a class="next" href="{url_for(group["view_func"], doc=n["file"])}">'
                   f'<span class="cap">다음 ›</span> {n["title"]}</a>')
    return f'<div class="pager">{"".join(out)}</div>' if out else ""


def toolbar_html(raw_url):
    return (f'<div class="toolbar">'
            f'<button onclick="window.print()">인쇄 / PDF</button>'
            f'<button onclick="toggleCode()">코드 블록 줄바꿈</button>'
            f'<a href="{raw_url}"><button>원본 MD</button></a></div>')


def shell(title, nav_title, h1, meta, content, pager, raw_url,
          group_key=None, active_file=None):
    html = LAYOUT
    html = html.replace("__STYLE__", STYLE)
    html = html.replace("__TITLE__", title)
    html = html.replace("__NAV_TITLE__", nav_title)
    html = html.replace("__H1__", h1)
    html = html.replace("__META__", meta)
    html = html.replace("__NAV__", build_sidebar(group_key, active_file))
    html = html.replace("__TOOLBAR__", toolbar_html(raw_url))
    html = html.replace("__CONTENT__", content)
    html = html.replace("__PAGER__", pager)
    return Response(html, mimetype="text/html; charset=utf-8")


def render_group_page(group, doc):
    gdir, gf, gpref = group["dir"], group["view_func"], group["prefix"]
    safe, raw = read_doc(gdir, doc)
    docs = list_docs(gdir)
    idx = next((i for i, d in enumerate(docs) if d["file"] == safe), None)
    if idx is None:
        abort(404)
    d = docs[idx]
    code = safe.split("_", 1)[0]
    chrome = f'<span class="chrome chrome-{group["key"]}">{group["key"]}</span>'
    content = render_markdown(raw)
    meta = (f"{chrome}출력 {code} · {group['label'].split('·')[0].strip()}"
            f" · 대한민국 2026")
    nav_title = f'{group["key"].upper()} / {code}'
    return shell(d["title"], nav_title, d["title"], meta, content,
                 build_pager(group, docs, idx),
                 url_for("raw2", group_name=group["key"], doc=safe),
                 group_key=group["key"], active_file=safe)


def index_content():
    blocks = []
    for g in GROUPS:
        index_md = os.path.join(g["dir"], "00_index.md")
        body = ""
        if os.path.isfile(index_md):
            with open(index_md, encoding="utf-8") as f:
                body = render_markdown(f.read())
        cards = []
        for d in list_docs(g["dir"]):
            if d["file"] == "00_index.md":
                continue
            code = d["file"].split("_", 1)[0]
            cards.append(
                f'<a class="card {("v2 " if g["key"]=="v2" else "")}" '
                f'href="{url_for(g["view_func"], doc=d["file"])}">'
                f'<span class="code">{code}</span><div class="tt">{d["title"]}</div>'
                f'<div class="ds">{g["desc"].get(code, "")}</div></a>'
            )
        blocks.append(
            '<div class="section-block">'
            f'<h2><span class="tag tag-{g["key"]} chrome-{g["key"]}">{g["key"]}</span>{g["label"]}</h2>'
            f'<p class="note">{g["note"]}</p>'
            f'<div>{body}</div>'
            f'<div class="grid">{"".join(cards)}</div>'
            "</div>"
        )
    return "".join(blocks)


@app.route("/")
def index():
    content = index_content()
    return shell("Quiet Move Simulator — 인덱스", "Index", "Quiet Move Simulator",
                 "v1 일상 시뮬레이션 · v2 특수 분야 심층 — 소스: 2026 대한민국",
                 content, "", url_for("raw2", group_name="v1", doc="00_index.md"))


@app.route("/view/<doc>")
def view(doc):
    return render_group_page(GROUPS[0], doc)


@app.route("/v2/<doc>")
def v2_view(doc):
    return render_group_page(GROUPS[1], doc)


@app.route("/raw/<doc>")
def raw(doc):
    safe, raw = read_doc(GROUPS[0]["dir"], doc)
    return Response(raw, mimetype="text/plain; charset=utf-8")


@app.route("/v2/raw/<doc>")
def raw2_group(doc):
    safe, raw = read_doc(GROUPS[1]["dir"], doc)
    return Response(raw, mimetype="text/plain; charset=utf-8")


@app.route("/raw-group/<group_name>/<doc>")
def raw2(group_name, doc):
    group = next((g for g in GROUPS if g["key"] == group_name), None)
    if group is None:
        abort(404)
    safe, raw = read_doc(group["dir"], doc)
    return Response(raw, mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)