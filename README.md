# Quiet Move Simulator — 출력 뷰어 (v1 + v2)

간단한 Flask 뷰어입니다. 마크다운 산출물을 두 섹션으로 나누어 렌더링합니다.

- **v1 · 일상 시뮬레이션** (`output/`) — 가정·취업·직장 관련 A~Q 17개 산출물
- **v2 · 특수 분야 심층** (`output_v2/`) — 포켓몬 카드·LOL·낚시·패션·러닝 5개 분야의
  A~M 심층 시뮬레이션(행동·감정·기억·적응·회고) + 교차 비교

## 실행 방법

```powershell
pip install -r requirements.txt
python app.py
```

브라우저에서 열기: http://127.0.0.1:8000

## 기능

- `/` — 인덱스 (v1/v2 각각 문서 카드 목록)
- `/view/<파일명>` — v1 문서 / `/v2/<파일명>` — v2 문서
  (좌측 목차·검색, 이전/다음, 인쇄/PDF, 코드 블록 줄바꿈)
- `/raw/<파일명>` — v1 원문 / `/v2/raw/<파일명>` — v2 원문

## 디렉토리 구성

```
app.py              Flask 서버 (flask + markdown 렌더링)
requirements.txt    flask, markdown
output/             v1 · 일상 시뮬레이션 (A~Q)
output_v2/          v2 · 특수 분야 심층 (A~M × 5분야 + 교차 비교)
```

## 참고

- 출력 내용은 웹 리서치(World State)를 배경으로 한 시뮬레이션 결과입니다.
  실제 사용자 수요·통계로 해석하거나 마케팅 근거로 사용하면 안 됩니다(출력 Q 참고).