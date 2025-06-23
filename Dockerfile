# 1. 베이스 이미지 설정: Python 3.11 슬림 버전을 기반으로 합니다.
FROM python:3.11-slim

# 2. 작업 디렉토리 설정: 컨테이너 내에서 명령어가 실행될 기본 경로입니다.
WORKDIR /app

# 3. 시스템 의존성 및 구글 크롬 설치
#    - apt-get update: 패키지 목록을 최신화합니다.
#    - wget, gnupg: 구글의 GPG 키를 받아오고 등록하기 위해 필요합니다.
#    - google-chrome-stable: 안정적인 최신 버전의 구글 크롬 브라우저를 설치합니다.
#    - --no-install-recommends: 추천 패키지는 제외하여 이미지 용량을 줄입니다.
#    - 마지막에 불필요한 파일들을 정리하여 최종 이미지 크기를 최적화합니다.
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    --no-install-recommends \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends \
    && apt-get purge -y --auto-remove wget gnupg \
    && rm -rf /var/lib/apt/lists/*

# 4. Python 라이브러리 설치
#    - 먼저 requirements.txt 파일만 복사하여 라이브러리를 설치합니다.
#    - 이렇게 하면, 소스 코드가 변경될 때마다 라이브러리를 다시 설치하는 비효율을 막을 수 있습니다. (도커의 레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 소스 코드 복사
#    - 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY . .

# 6. 컨테이너 실행 명령어
#    - 컨테이너가 시작될 때 `run_job.py` 스크립트를 실행합니다.
CMD ["python", "run_job.py"] 