# Google Cloud Run 배포 스크립트

Write-Host "Google Cloud Run에 배포를 시작합니다..." -ForegroundColor Green

# 1. Google Cloud에 로그인 (이미 로그인되어 있으면 건너뜀)
Write-Host "Google Cloud 계정 확인 중..." -ForegroundColor Yellow
$currentAccount = gcloud config get-value account 2>$null
if (-not $currentAccount) {
    Write-Host "Google Cloud에 로그인 중..." -ForegroundColor Yellow
    gcloud auth login
} else {
    Write-Host "이미 로그인되어 있습니다: $currentAccount" -ForegroundColor Green
}

# 2. 현재 프로젝트 확인 및 설정
$currentProject = gcloud config get-value project 2>$null
if (-not $currentProject) {
    Write-Host "Google Cloud 프로젝트 ID를 입력하세요:" -ForegroundColor Yellow
    $projectId = Read-Host
    gcloud config set project $projectId
} else {
    Write-Host "현재 프로젝트: $currentProject" -ForegroundColor Green
    $projectId = $currentProject
}

# 3. 필요한 API 활성화
Write-Host "필요한 API를 활성화 중..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 4. Cloud Build로 배포
Write-Host "Cloud Build로 배포 중..." -ForegroundColor Yellow
gcloud builds submit --config cloudbuild.yaml .

Write-Host "배포가 완료되었습니다!" -ForegroundColor Green
Write-Host "서비스 URL을 확인하려면 다음 명령어를 실행하세요:" -ForegroundColor Cyan
Write-Host "gcloud run services describe coffee-crawler --region=asia-northeast3 --format='value(status.url)'" -ForegroundColor White 