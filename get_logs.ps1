# 1. 터미널 환경 변수(PATH)에 Google Cloud SDK 경로를 추가합니다.
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# 2. 작업할 GCP 프로젝트를 설정합니다.
gcloud config set project coffee-crawler-463802

# 3. 마지막으로 실패한 작업의 상세 로그를 다른 형식(JSON)으로 조회합니다.
Write-Host "--- Logs for execution hrhxf (jsonPayload) ---"
gcloud logging read "resource.type='cloud_run_job' AND resource.labels.job_name='coffee-crawler-job' AND labels.'run.googleapis.com/execution_name'='coffee-crawler-job-hrhxf'" --format="json" --limit=10

Write-Host "`n--- Logs for execution jcxsb (textPayload) ---"
gcloud logging read "resource.type='cloud_run_job' AND resource.labels.job_name='coffee-crawler-job' AND labels.'run.googleapis.com/execution_name'='coffee-crawler-job-jcxsb'" --format="value(textPayload)" --limit=10 