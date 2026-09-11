"""v3 파트3 — 소프트웨어 기업 재무·사업 스크리닝 데이터 수집

소스:
  - DART OpenAPI (인증키 env DART_KEY 또는 아래 KEY 상수)
  - 혁신의숲(InnoForest) 기업 페이지 (사업영역·키워드)
산출: output_v3/_data/companies.json

실행: python tools/fetch_company_data.py
"""
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(BASE_DIR, "tools", "_cache")
os.makedirs(CACHE, exist_ok=True)

KEY = os.environ.get("DART_KEY", "25e75b5398dcf6ac796362ed301a8b6aadd9e946")
UA = {"User-Agent": "Mozilla/5.0 (compatible; research/1.0)"}

# 업종(sector) → [(이름, 종목코드, 업종명)]
UNIVERSE = {
    "플랫폼": [
        ("네이버", "035420", "포털·플랫폼(광고·커머스)"),
        ("카카오", "035720", "플랫폼(모빌리티·커머스·웹툰)"),
    ],
    "게임": [
        ("크래프톤", "259960", "게임(배틀로얄·PC/콘솔)"),
        ("넥슨게임즈", "225570", "게임(모바일 RPG)"),
        ("펄어비스", "263750", "게임(오픈월드 MMORPG)"),
        ("위메이드", "112040", "게임·블록체인(Web3)"),
        ("컴투스", "078340", "게임(모바일)"),
        ("NHN", "181710", "게임·결제·클라우드(IT서비스)"),
    ],
    "소프트웨어/SaaS": [
        ("더존비즈온", "012510", "회계·ERP SaaS"),
        ("한글과컴퓨터", "030520", "오피스·문서 SW"),
        ("가비아", "079940", "클라우드·호스팅·IDC"),
        ("다우기술", "023590", "그룹웨어·메신저·IT서비스"),
        ("유비온", "084440", "LMS·스마트교육 SW"),
    ],
    "금융SW/결제": [
        ("나이스정보통신", "036800", "신용카드 VAN·결제"),
        ("코나아이", "052400", "결제·주민번호·핀테크"),
        ("한국사이버결제", "060250", "전자결제(PG)"),
    ],
    "보안": [
        ("안랩", "053800", "백신·엔드포인트 보안"),
        ("파수", "150900", "DRM·데이터 보안(SaaS)"),
        ("지니언스", "263860", "NAC·네트워크 보안"),
        ("케이사인", "192250", "전자서명·인증"),
    ],
    "AI·IT서비스": [
        ("삼성SDS", "018260", "IT서비스·클라우드·글로벌 SI"),
        ("포스코DX", "022100", "스마트팩토리·IT서비스"),
        ("셀바스AI", "108860", "음성·AI 솔루션"),
        ("플리토", "300080", "AI 번역·로컬라이제이션"),
    ],
}

CORP_ZIP_URL = "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=" + KEY
SITEMAP_MAIN = [
    "corp-sitemap-main-1.xml",
    "corp-sitemap-main-2.xml",
    "corp-sitemap-main-3.xml",
    "corp-sitemap-main-4.xml",
    "corp-sitemap-main-5.xml",
    "corp-sitemap-main-6.xml",
    "corp-sitemap-main-7.xml",
    "corp-sitemap-main-8.xml",
    "corp-sitemap-main-9.xml",
]


def http_get(url, timeout=40, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "ignore")


def dart_api(path, params):
    params["crtfc_key"] = KEY
    url = "https://opendart.fss.or.kr/api/" + path + "?" + urllib.parse.urlencode(params)
    return json.loads(http_get(url))


def norm(n):
    n = n.replace("(주)", "").replace("(유)", "").replace("주식회사", "").strip()
    return re.sub(r"\s+", "", n).upper()


def load_corps():
    zpath = os.path.join(CACHE, "CORPCODE.zip")
    if not os.path.exists(zpath):
        print("download CORPCODE.zip ...")
        data = http_get(CORP_ZIP_URL, binary=True)
        open(zpath, "wb").write(data)
    corps = []
    with zipfile.ZipFile(zpath) as z:
        xml = z.read("CORPCODE.xml").decode("utf-8")
        for m in re.finditer(r"<list>(.*?)</list>", xml, re.S):
            b = m.group(1)
            corps.append({
                "corp_code": re.search(r"<corp_code>(.*?)</corp_code>", b).group(1),
                "corp_name": re.search(r"<corp_name>(.*?)</corp_name>", b).group(1),
                "stock_code": re.search(r"<stock_code>(.*?)</stock_code>", b).group(1),
            })
    by_t = {c["stock_code"]: c for c in corps if c["stock_code"]}
    by_n = {norm(c["corp_name"]): c["corp_code"] for c in corps}
    return by_t, by_n


def load_inno_map():
    """sitemap → {norm_name: CP code}"""
    cachef = os.path.join(CACHE, "inno_name_cp.json")
    if os.path.exists(cachef):
        return json.load(open(cachef, encoding="utf-8"))
    mapp = {}
    for sm in SITEMAP_MAIN:
        url = "https://www.innoforest.co.kr/sitemaps/" + sm
        try:
            xml = http_get(url)
        except Exception as e:
            print("sitemap fail", sm, e)
            continue
        for loc in re.findall(r"<loc>(.*?)</loc>", xml):
            m = re.search(r"/company/(CP\d+)/([^/]+)/?$", loc)
            if not m:
                continue
            cp, enc = m.group(1), m.group(2)
            name = urllib.parse.unquote(enc)
            mapp.setdefault(norm(name), cp)
        print("sitemap ok", sm, len(mapp))
    json.dump(mapp, open(cachef, "w", encoding="utf-8"), ensure_ascii=False)
    return mapp


def inno_fetch(cp):
    """혁신의숲 기업 페이지 → 사업영역 요약 추출"""
    try:
        html = http_get(f"https://www.innoforest.co.kr/company/{cp}/")
    except Exception as e:
        return None
    txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    txt = re.sub(r"<(br|/p|/div|/li|/h[1-6]|/tr|/td|/th)[^>]*>", "\n", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    out = {"intro": "", "keywords": "", "categories": ""}
    kw, cat, intro = [], [], []
    for i, l in enumerate(lines):
        if i > 0 and lines[i - 1] == "기업 대표 키워드" and not out["keywords"]:
            out["keywords"] = l
        if i > 0 and lines[i - 1] == "카테고리" and not out["categories"]:
            out["categories"] = l
        if l.startswith("기업소개"):
            intro.append(l.replace("기업소개", "").strip())
    m = re.search(r'property="og:description" content="([^"]+)"', html)
    if m and not intro:
        intro.append(m.group(1))
    out["intro"] = " ".join(intro)[:260]
    return out


def fetch_fin(corp_code, year="2025", code="11011"):
    d = dart_api("fnlttSinglAcnt.json", {
        "corp_code": corp_code, "bsns_year": year,
        "reprt_code": code, "fs_div": "CFS"})
    if d.get("status") != "000":
        return None
    rows = d["list"]
    ordered_keys = []
    for row in rows:
        if row["account_nm"] == "자산총계" and row["thstrm_amount"] not in ordered_keys:
            ordered_keys.append(row["thstrm_amount"])
    conn_key = None
    for row in rows:
        if row["account_nm"] == "자산총계" and row.get("fs_nm") == "연결재무제표":
            conn_key = row["thstrm_amount"]
            break
    if conn_key is None:
        conn_key = (ordered_keys[0] if len(ordered_keys) == 1
                    else max(ordered_keys, key=lambda k: int(k.replace(",", "")) or 0))
    note = ""
    if len(ordered_keys) >= 2:
        mx = sorted(ordered_keys, key=lambda k: int(k.replace(",", "")) or 0, reverse=True)
        try:
            ratio = int(mx[0].replace(",", "")) / int(mx[1].replace(",", ""))
        except ZeroDivisionError:
            ratio = 0
        if ratio >= 10:
            note = (f"연결 자산총계가 별도 대비 {ratio:.0f}배 — 금융/투자성 자회사 연계 의심. "
                    f"연결 재무 해석 시 매출 구조 확인 필요.")
    fin = {"note": note}
    set_key = None
    for row in rows:
        nm = row["account_nm"]
        if nm == "자산총계":
            set_key = row["thstrm_amount"]
            if set_key != conn_key:
                continue
        elif set_key != conn_key:
            continue
        th = (row["thstrm_amount"] or "0").replace(",", "")
        fr = (row["frmtrm_amount"] or "0").replace(",", "")
        th = int(th) if th not in ("", "-") else None
        fr = int(fr) if fr not in ("", "-") else None
        if nm == "자산총계":
            fin["자산총계"] = th
        elif nm == "부채총계":
            fin["부채총계"] = th
        elif nm == "매출액":
            fin["매출"] = th; fin["매출_전기"] = fr
        elif nm == "영업이익":
            fin["영업이익"] = th
        elif "당기순이익" in nm:
            fin["당기순이익"] = th
    fin["rcept_no"] = rows[0]["rcept_no"]
    return fin


def ceo_of(corp_code):
    d = dart_api("company.json", {"corp_code": corp_code})
    if d.get("status") != "000":
        return "?", "?", "?"
    return (d.get("ceo_nm") or "?"), (d.get("corp_name") or ""), (d.get("corp_cls") or "")


def main():
    print("load corps / inno map …")
    by_t, by_n = load_corps()
    inno_map = load_inno_map()
    records = []
    for sector, companies in UNIVERSE.items():
        for name, ticker, sub in companies:
            c = by_t.get(ticker)
            if not c:
                print(f"[skip] {name} ({ticker}) 미등록")
                continue
            corp_code = c["corp_code"]
            print(f"== {name} {ticker} {corp_code}")
            fin = fetch_fin(corp_code)
            time.sleep(0.25)
            ceo, dname, cls = ceo_of(corp_code)
            time.sleep(0.25)
            cp = inno_map.get(norm(dname)) or inno_map.get(norm(name))
            if not cp:
                print("   (InnoForest CP 미발견)", dname, "|", name)
            inno = inno_fetch(cp) if cp else None
            if cp:
                time.sleep(0.4)
            records.append({
                "name": name, "ticker": ticker, "corp_code": corp_code,
                "sector": sector, "sub": sub,
                "dart_name": dname, "ceo": ceo, "corp_cls": cls,
                "cp": cp or "",
                "inno": inno or {},
                "fin": fin or {},
            })
    out = os.path.join(BASE_DIR, "output_v3", "_data", "companies.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(records, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n저장 {out} (기업 {len(records)}개)")


if __name__ == "__main__":
    main()