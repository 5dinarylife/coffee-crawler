# 1. 터미널 환경 변수(PATH)에 Google Cloud SDK 경로를 추가합니다.
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# 2. 작업할 GCP 프로젝트를 설정합니다.
gcloud config set project coffee-crawler-463802

# 3. Cloud Run '작업(Job)'으로 크롤러를 배포합니다.
#    - coffee-crawler-job: 작업의 이름
#    - --source .: 현재 디렉토리의 소스를 사용
#    - --region: 배포할 지역 (서울)
#    - --memory: 할당할 메모리
#    - --task-timeout: 작업의 최대 실행 시간 (1시간)
#    - --cpu: 할당할 CPU 코어 수
#    - --tasks: 동시에 실행할 작업 수
gcloud run jobs deploy coffee-crawler-job --source . --region asia-northeast3 --memory 2Gi --task-timeout 3600 --cpu 2 --tasks 1 