# Quiet Move Simulator — 정적 웹 사이트

대한민국(수도권) 2026년 가을, 수능 D-66 한 주간을 simulate했던
**Quiet Move Simulator**(A~Q 17개 산출물)를 마크다운 라이브러리로 렌더링하는
**정적 웹 사이트**입니다. Flask 없이 GitHub Pages에 바로 게시할 수 있습니다.

## 구조

```
output/*.md                 산출물 원본 (A~Q 17개 + 00_index)
build_site.py               정적 사이트 생성기
docs/                       생성된 정적 사이트 (GitHub Pages 소스)
requirements.txt            markdown (빌드용)
```

## 사이트 생성

```powershell
pip install -r requirements.txt
python build_site.py
```

`docs/`에 `index.html` + `01_world_state.html` ~ `17_assumptions_unknowns.html`
(+ `style.css`, `app.js`, 원본 MD 복사본)이 생성됩니다.
원본 마크다운을 수정한 뒤 다시 실행하면 덮어씁니다.

## 로컬 확인

```powershell
python -m http.server 8080 -d docs
# http://127.0.0.1:8080
```

## GitHub Pages 배포

1. 생성된 `docs/` 폴더를 포함해 커밋·푸시합니다.
2. 저장소 **Settings → Pages** → **Build and deployment → Source: "Deploy from a branch"**
3. **Branch: `main` / folder: `/docs`** 로 설정 → 저장
4. `https://<사용자>.github.io/<저장소>/` 로 게시됩니다.

### (선택) GitHub Actions로 자동 빌드

워크플로가 필요하면 다음 파일을 `.github/workflows/pages.yml`로 두고
Pages Source를 "GitHub Actions"로 설정하면 푸시 시 자동 빌드·배포됩니다.

```yaml
name: Deploy static site to Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python build_site.py
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

## 페이지 기능

- 좌측: 문서 목록(검색) + 문서 내 목차(스크롤 스파이)
- 상단: 인쇄/PDF, 코드 블록 줄바꿈, 원본 MD 다운로드
- 하단: 이전/다음 문서 이동
- `/`(index.html): 출력 카드 목록

## 참고

- 출력 내용은 웹 리서치(World State)를 배경으로 한 시뮬레이션 결과입니다.
  실제 사용자 수요·통계로 해석하거나 마케팅 근거로 사용하면 안 됩니다(출력 Q 참고).