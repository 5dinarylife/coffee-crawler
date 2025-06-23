# 1. 터미널 환경 변수(PATH)에 Docker 경로를 추가합니다.
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"

# 2. 현재 디렉토리의 Dockerfile을 사용하여 'coffee-crawler-local' 이미지를 빌드합니다.
docker build -t coffee-crawler-local . 