"""v3 파트3a — 비상장 초기투자 스타트업 스크리닝 데이터 수집 (2026-09 시점)

대상: 내가 만드는 SW와 같은 영역(12개 도메인)의 **비상장** 초기투자 기업.
회사 풀은 도메인별 큐레이션 후보 → InnoForest 사이트맵으로 CP 해석 → 공개 프로필 수집.
필터: 상장여부(코스피/코스닥 등)·운영여부(폐업) 제외, DART 상장 명단 중복 제외.
재무(매출/순익/사원수)는 공개 데이터 부재 → '-' 로 두고 사업모델·투자 시그널로 판정.

소스:
  - 혁신의숲(InnoForest) 기업 페이지 (사업영역·키워드·설립일자·상장여부·운영여부)
  - DART 기업개황(corpCode) : 상장 제외용
산출: output_v3/_data/startups.json

실행: python tools/fetch_v3_startups.py
"""
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(BASE_DIR, "tools", "_cache")
OUT = os.path.join(BASE_DIR, "output_v3", "_data")
os.makedirs(OUT, exist_ok=True)

KEY = os.environ.get("DART_KEY", "25e75b5398dcf6ac796362ed301a8b6aadd9e946")
UA = {"User-Agent": "Mozilla/5.0 (compatible; research/1.0)"}

# (도메인, [(표시 브랜드, 회사명 후보들, 수익모델 추정)])
CANDIDATES = {
    "회계·세무": [
        ("삼쩜삼", ["자비스앤빌런즈", "삼쩜삼"], "B2C 구독 + 신고 수수료"),
    ],
    "그룹웨어·협업": [
        ("잔디", ["토스랩", "잔디", "JANDI"], "B2B 구독"),
        ("리멤버", ["리멤버앤컴퍼니", "리멤버"], "B2B 구독 + 채용 수수료"),
    ],
    "AI 글쓰기·번역": [
        ("뤼튼", ["뤼튼테크놀로지스", "뤼튼"], "구독"),
        ("포티투마루", ["포티투마루", "마루"], "B2B"),
    ],
    "음성·OCR": [
        ("수퍼톤", ["수퍼톤", "SUPERTON"], "B2B"),
        ("로민", ["로민"], "B2B(건당/구독)"),
    ],
    "결제·포인트": [
        ("포트원", ["코리아포트원", "포트원", "PORTONE", "아임포트"], "PG 중개수수료"),
    ],
    "에듀테크·LMS": [
        ("클래스101", ["클래스101", "CLASS101"], "판매 수수료 + 구독"),
        ("매쓰홀릭", ["매쓰홀릭", "MATHHOLIC"], "B2B(학교·학원) 구독"),
    ],
    "지역·취미·수집": [
        ("당근", ["당근마켓", "당근"], "광고 + 지역생활 중개"),
        ("오늘의집", ["오늘의집", "버킷플레이스", "BUCKETPLACE"], "커머스 중개수수료"),
        ("마이리얼트립", ["마이리얼트립", "투어코드", "MYREALTRIP"], "여행 상품 중개"),
        ("리디", ["리디", "리디북스", "RIDI"], "콘텐츠 판매(B2C)"),
    ],
    "웰니스·건강(의료·정신)": [
        ("힐링페이퍼(강남언니)", ["힐링페이퍼", "강남언니"], "미용의료 정보·예약(중개+광고)"),
        ("위버케어(메디패스·닥터팔레트)", ["위버케어", "메디패스"], "의료정보 통합(클라우드 EMR+환자앱)"),
    ],
    "금융라이트": [
        ("뱅크샐러드", ["레인포", "뱅크샐러드", "RAINFIND"], "중개 수수료 + 데이터"),
        ("핀다", ["핀다", "FINDA"], "대출 중개 수수료"),
    ],
    "마케팅·메시징": [
        ("센드버드", ["센드버드코리아", "센드버드", "SENDBIRD"], "B2B 구독"),
    ],
}


def norm(s):
    s = s.upper()
    s = re.sub(r"[()（）]", "", s)
    s = re.sub(r"\s+", "", s)
    return s.strip()


def load_cp_map():
    p = os.path.join(CACHE, "inno_name_cp.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {}


def load_dart_listed():
    """DART corp zip에서 종목코드 있는(상장) 회사 정규화 이름 집합."""
    z = os.path.join(CACHE, "CORPCODE.zip")
    if not os.path.exists(z):
        return set()
    out = set()
    with zipfile.ZipFile(z) as zf:
        with zf.open("CORPCODE.xml") as f:
            data = f.read().decode("utf-8", "replace")
    for m in re.finditer(r"<corp_code>(\d+)</corp_code>.*?<corp_name>(.*?)</corp_name>.*?<stock_code>(.*?)</stock_code>", data, re.S):
        code, name, stock = m.groups()
        if stock.strip():
            out.add(norm(name))
    return out


def fetch(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5)


def clean_text(h):
    h = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    return re.sub(r"\s+", " ", h)


def parse_profile(h, brand):
    """공개 기업 페이지(SSR)에서 공개 필드만 추출.

    구조: 기업소개 <본문> 기업 대표 키워드 <키워드> 기업 성과 ... 설립일자 <d> 상장여부 <v> 운영여부 <v> 홈페이지 <url> 주소 <addr> (블록 2회 반복)
    푸터에 '주소 : 서울특별시...광고' 오염원이 있으므로 실제 주소는 '설립일자'로 끝나는 블록으로 한정한다.
    """
    txt = clean_text(h)
    meta = re.search(r"<title>(.*?)</title>", h, re.S)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|</title>", "", meta.group(1))).strip() if meta else ""
    prof = {"raw_title": title}
    m = re.search(r"설립일자\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\s+상장여부\s+(\S+)\s+운영여부\s+(\S+)", txt)
    if m:
        prof["설립일자"] = m.group(1)
        prof["상장여부"] = m.group(2)
        prof["운영여부"] = m.group(3)
    m = re.search(r"홈페이지\s+(\S+)", txt)
    if m:
        prof["홈페이지"] = m.group(1).rstrip(",. ")
    addrs = re.findall(r"주소\s+(?![:：])([^\s:：][^설립일자]{2,90}?)(?=\s+설립일자)", txt)
    if addrs:
        prof["주소"] = addrs[0].strip()
    m = re.search(r"기업소개\s+(.*?)\s+기업 대표 키워드", txt)
    if m:
        prof["기업소개"] = re.sub(r"\s+", " ", m.group(1)).strip()[:600]
    m = re.search(r"기업 대표 키워드\s+(.*?)(?:\s+기업 성과|\s+설립일자)", txt)
    if m:
        prof["비즈니스키워드"] = m.group(1).strip()
    return prof


def main():
    cp_map = load_cp_map()
    dart_listed = load_dart_listed()
    print(f"[지표] sitemap 회사 수={len(cp_map)}  DART 상장 수={len(dart_listed)}")

    cp_to_name = {}
    for n, cp in cp_map.items():
        cp_to_name.setdefault(cp, n)

    out = []
    missing = []
    for domain, items in CANDIDATES.items():
        for brand, alias_list, model in items:
            c = {"도메인": domain, "브랜드": brand, "초기후보": alias_list[0], "수익모델추정": model}
            resolved_cp = None
            resolved_alias = None
            for a in alias_list:
                na = norm(a)
                if na in cp_map:
                    resolved_cp = cp_map[na]
                    resolved_alias = a
                    break
            if not resolved_cp:
                missing.append((domain, brand, alias_list))
                c["상태"] = "CP없음"
                out.append(c)
                continue
            c["cp"] = resolved_cp
            c["사이트맵명"] = cp_to_name.get(resolved_cp, resolved_alias)
            page = None
            try:
                page = fetch(f"https://www.innoforest.co.kr/company/{resolved_cp}/")
            except Exception as e:
                c["상태"] = "fetch실패"
                c["오류"] = str(e)[:120]
                out.append(c)
                continue
            prof = parse_profile(page, brand)
            c.update(prof)
            is_listed = norm(prof.get("상장여부", "")) not in ("", "비상장") or norm(c.get("사이트맵명", "")) in dart_listed
            not_operating = "폐업" in str(prof.get("운영여부", ""))
            c["상태"] = "보류(상장)" if is_listed else ("보류(폐업)" if not_operating else "OK")
            c["DART상장매칭"] = norm(c.get("사이트맵명", "")) in dart_listed
            out.append(c)
            print(f"  {domain:14s} | {brand:14s} | {c['상태']:10s} | {resolved_cp} {c.get('사이트맵명','')} | 설립:{prof.get('설립일자','-')} 상장:{prof.get('상장여부','-')} 운영:{prof.get('운영여부','-')}")
            time.sleep(0.4)

    result = {"기준일": "2026-09-11", "주석": "비상장 초기투자 SW 스타트업 스크리닝. 매출/순익/사원수는 공개 데이터 부재 → '-' 로 표기.",
              "기업": out, "CP없음": missing}
    with open(os.path.join(OUT, "startups.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("\n[CP없음] 후보 수:", len(missing))
    for d, b, al in missing:
        print("   ", d, "|", b, "|", ", ".join(al))


if __name__ == "__main__":
    main()