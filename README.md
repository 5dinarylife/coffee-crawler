# ☕ 생두 크롤러 웹 시스템

여러 커피 원두 판매 사이트에서 생두 정보를 수집하는 웹 기반 크롤링 시스템입니다.

## 🚀 주요 기능

- **웹 기반 인터페이스**: Streamlit을 사용한 사용자 친화적인 웹 인터페이스
- **다중 크롤러 지원**: 10개 커피 사이트에서 동시에 데이터 수집
- **실시간 모니터링**: 크롤링 진행 상황과 결과를 실시간으로 확인
- **파일 다운로드**: 개별 및 통합 엑셀 파일 다운로드 기능
- **자동 통합**: 여러 크롤러의 결과를 하나의 엑셀 파일로 통합

## 📊 지원하는 크롤러

| 크롤러 | 사이트 | 파일명 |
|--------|--------|--------|
| GSC | GSC Coffee | gsc_greenbean.xlsx |
| 맥널티 | 맥널티 | 맥널티_원두.xlsx |
| 블레스빈 | 블레스빈 | 블레스빈_원두.xlsx |
| 엠아이커피 | 엠아이커피 | 엠아이커피_원두.xlsx |
| 코빈즈 | 코빈즈 | 코빈즈_원두.xlsx |
| 알마씨엘로 | 알마씨엘로 | 알마씨엘로_원두.xlsx |
| 소펙스 | 소펙스 | 소펙스_원두.xlsx |
| 리브레 | 리브레 | 리브레_원두.xlsx |
| 후성 | 후성 | 후성_원두.xlsx |
| 모모스 | 모모스 | 모모스_원두.xlsx |

## 🛠️ 설치 및 실행

### 로컬 실행

1. **저장소 클론**
```bash
git clone [repository-url]
cd [repository-name]
```

2. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

3. **Streamlit 앱 실행**
```bash
streamlit run streamlit_app.py
```

4. **브라우저에서 접속**
```
http://localhost:8501
```

### 온라인 배포

#### 방법 1: Google Cloud Run (권장)

1. **Google Cloud 프로젝트 생성**
   - [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트 생성
   - 프로젝트 ID를 메모해두세요

2. **Google Cloud CLI 설치 및 설정**
```bash
# Windows에서 설치
winget install Google.CloudSDK

# 또는 수동 설치: https://cloud.google.com/sdk/docs/install
```

3. **배포 스크립트 실행**
```bash
# PowerShell에서 실행
.\deploy_gcp.ps1
```

4. **수동 배포 (스크립트 사용 불가 시)**
```bash
# Google Cloud 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project [YOUR_PROJECT_ID]

# 필요한 API 활성화
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 배포
gcloud builds submit --config cloudbuild.yaml .
```

#### 방법 2: Streamlit Cloud (제한적)

1. **GitHub에 코드 업로드**
2. **Streamlit Cloud에서 배포**
   - [share.streamlit.io](https://share.streamlit.io) 접속
   - GitHub 저장소 연결
   - 자동 배포

⚠️ **주의**: Streamlit Cloud에서는 Selenium과 ChromeDriver 사용에 제한이 있을 수 있습니다.

## 📖 사용법

### 1. 개별 크롤러 실행
1. 사이드바에서 원하는 크롤러 선택
2. "실행" 버튼 클릭
3. 크롤링 완료 후 엑셀 파일 다운로드

### 2. 모든 크롤러 일괄 실행
1. "모든 크롤러 실행" 버튼 클릭
2. 진행 상황을 실시간으로 확인
3. 완료 후 통합 엑셀 파일 생성

### 3. 파일 관리
- 생성된 엑셀 파일들을 실시간으로 확인
- 개별 파일 또는 통합 파일 다운로드
- 크롤링 상태 및 결과 모니터링

## 📁 파일 구조

```
├── streamlit_app.py          # 메인 Streamlit 앱
├── requirements.txt          # 필요한 패키지 목록
├── Dockerfile               # Docker 컨테이너 설정
├── cloudbuild.yaml          # Google Cloud Build 설정
├── deploy_gcp.ps1           # Google Cloud 배포 스크립트
├── .streamlit/
│   └── config.toml          # Streamlit 설정
├── gsc_crawler.py           # GSC 크롤러
├── 맥널티_크롤러.py          # 맥널티 크롤러
├── 블레스빈_크롤러.py         # 블레스빈 크롤러
├── 엠아이커피_크롤러.py       # 엠아이커피 크롤러
├── 코빈즈_크롤러.py          # 코빈즈 크롤러
├── 알마씨엘로_크롤러.py       # 알마씨엘로 크롤러
├── 소펙스_크롤러.py          # 소펙스 크롤러
├── 리브레_크롤러.py          # 리브레 크롤러
├── 후성_크롤러.py            # 후성 크롤러
├── 모모스_크롤러.py          # 모모스 크롤러
└── README.md                # 프로젝트 설명서
```

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **Web Scraping**: Selenium, BeautifulSoup
- **Data Processing**: Pandas
- **File Format**: Excel (openpyxl)
- **Container**: Docker
- **Cloud Platform**: Google Cloud Run

## 💰 비용 정보

### Google Cloud Run
- **무료 티어**: 월 200만 요청, 360,000 vCPU-초, 180,000 GiB-초
- **과금**: 무료 티어 초과 시 요청당 $0.0000024, vCPU-초당 $0.00002400
- **예상 월 비용**: 소규모 사용 시 월 $1-5 정도

## ⚠️ 주의사항

- 크롤링 시 각 사이트의 이용약관을 준수해주세요
- 과도한 요청으로 서버에 부하를 주지 않도록 주의하세요
- 수집된 데이터는 개인적인 용도로만 사용해주세요
- Google Cloud Run 배포 시 처음 요청 시 콜드 스타트가 발생할 수 있습니다

## 📝 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**개발자**: AI Assistant  
**최종 업데이트**: 2024년 12월 