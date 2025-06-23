# Node.js 기반 크롤러 소스 폴더

이 폴더는 기존 파이썬 크롤러(.py) 파일들을 참고하여,
Puppeteer(또는 Playwright) 기반 Node.js 크롤러를 개발하는 공간입니다.

- HTML 구조, CSS Selector, 데이터 추출 규칙 등은 기존 파이썬 소스를 그대로 반영
- 커피 이름, 가공방식 등 텍스트 처리/정규식도 Python → JS로 변환
- 각 크롤러별로 별도 JS 파일로 구현 예정

> 예시: 엠아이커피_크롤러.js, 모모스_크롤러.js, ...

---

## 개발/운영 안내
- Node.js 20+ 권장
- puppeteer, xlsx 등 주요 라이브러리 사용
- 데이터 저장 포맷: JSON/CSV/XLSX 등 