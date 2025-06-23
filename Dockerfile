# 1. 베이스 이미지 설정: Python 3.11 슬림 버전을 기반으로 합니다.
FROM python:3.11-slim

# 2. 작업 디렉토리 설정: 컨테이너 내에서 명령어가 실행될 기본 경로입니다.
WORKDIR /app

# 3. 시스템 의존성, dos2unix 및 최신 구글 크롬, 최신 ChromeDriver 자동 설치
RUN apt-get update && apt-get install -y \
    dos2unix \
    wget \
    unzip \
    ca-certificates \
    gpg \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libxshmfence1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    xdg-utils \
    libxss1 \
    libgconf-2-4 \
    libu2f-udev \
    --no-install-recommends \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/bin/google-chrome-stable /usr/bin/google-chrome
RUN ls -l /usr/bin/google-chrome* && /usr/bin/google-chrome --version

# 4. Python 라이브러리 설치
#    - 먼저 requirements.txt 파일만 복사하여 라이브러리를 설치합니다.
#    - 이렇게 하면, 소스 코드가 변경될 때마다 라이브러리를 다시 설치하는 비효율을 막을 수 있습니다. (도커의 레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 소스 코드 복사 및 변환
COPY . .
# 윈도우의 줄바꿈 문자(CRLF)를 리눅스(LF)로 변환하고, 실행 권한을 부여합니다.
RUN find . -type f -name "*.py" -exec dos2unix {} \;
RUN find . -type f -name "*.py" -exec chmod +x {} \;

# 6. 컨테이너 실행 명령어 (Flask 웹 서버 실행)
CMD ["python", "-u", "main.py"] 