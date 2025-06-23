import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

start_time = time.time()  # 크롤링 시작 시각

def process_to_korean(process):
    word_mapping = {
        'NATURAL': '내추럴', 'Natural': '내추럴', 'natural': '내추럴',
        'WASHED': '워시드', 'Washed': '워시드', 'washed': '워시드',
        'HONEY': '허니', 'Honey': '허니', 'honey': '허니',
        'ANAEROBIC': '에네로빅', 'Anaerobic': '에네로빅', 'anaerobic': '에네로빅',
        'FULLY': '풀리', 'Fully': '풀리', 'fully': '풀리',
        'SEMI': '세미', 'Semi': '세미', 'semi': '세미',
        'BLACK': '블랙', 'Black': '블랙', 'black': '블랙',
        'YELLOW': '옐로우', 'Yellow': '옐로우', 'yellow': '옐로우',
        'RED': '레드', 'Red': '레드', 'red': '레드',
        'LIGHT': '라이트', 'Light': '라이트', 'light': '라이트',
        'DOUBLE': '더블', 'Double': '더블', 'double': '더블',
        'WET': '웻', 'Wet': '웻', 'wet': '웻',
        'DRY': '드라이', 'Dry': '드라이', 'dry': '드라이',
        'PULPED': '펄프드', 'Pulped': '펄프드', 'pulped': '펄프드',
        'FERMENTATION': '퍼먼테이션', 'Fermentation': '퍼먼테이션', 'fermentation': '퍼먼테이션',
        'CARBONIC': '카보닉', 'Carbonic': '카보닉', 'carbonic': '카보닉',
        'MACERATION': '마세레이션', 'Maceration': '마세레이션', 'maceration': '마세레이션',
        'MECERATION': '마세레이션', 'Meceration': '마세레이션', 'meceration': '마세레이션',
        'POLISH': '폴리시', 'Polish': '폴리시', 'polish': '폴리시',
        'DECAF': '디카페인', 'Decaf': '디카페인', 'decaf': '디카페인',
        'SUGARCANE': '슈가케인', 'Sugarcane': '슈가케인', 'sugarcane': '슈가케인',
        'SW': '스위스워터', 'Sw': '스위스워터', 'sw': '스위스워터',
        '애너러빅': '에네로빅',  # 혹시 한글로 들어오는 경우도 대비
    }
    # 쉼표 뒤에 공백 추가
    process = re.sub(r',\s*', ', ', process)
    # '애너러빅'을 '에네로빅'으로 치환
    process = process.replace('애너러빅', '에네로빅')
    words = process.split()
    for word in words:
        if word in word_mapping:
            return word_mapping[word]
    return process  # 매핑이 없으면 원본 반환

# 셀레니움 옵션 설정 (브라우저 창 안 띄우기)
chrome_options = Options()
# 아래 옵션들은 Streamlit Cloud 서버에서 안정적으로 실행하기 위한 필수 옵션들입니다.
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# user-agent 설정은 유지합니다.
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.cobeans.com/content/content.php?cont=simple_order'
driver.get(url)

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.order_prd_list.simpleOrderProductList li.productLi'))
)

data = []
items = driver.find_elements(By.CSS_SELECTOR, 'ul.order_prd_list.simpleOrderProductList li.productLi')
for item in items:
    try:
        # 커피 이름
        name_a = item.find_element(By.CSS_SELECTOR, 'h4.name a')
        coffee_name_raw = name_a.text.strip()
        if not coffee_name_raw:
            continue

        # 앞의 두 자리 숫자 추출 및 커피 이름 재구성
        match = re.match(r'^(\d{2})\s+(.+)', coffee_name_raw)
        if match:
            number = match.group(1)
            name_without_number = match.group(2)
            # 국가명: 숫자 다음 첫 단어
            country = name_without_number.split()[0] if name_without_number else ''
            coffee_name = f"{name_without_number} {number}"
        else:
            # 숫자가 없으면 기존 방식
            country = coffee_name_raw.split()[0] if coffee_name_raw else ''
            coffee_name = coffee_name_raw

        # 가공방식: p.info > 첫 번째 span
        process_span = item.find_element(By.CSS_SELECTOR, 'p.info span')
        process_text = process_span.text.strip() if process_span.text else ''
        process_kr = process_to_korean(process_text)

        # 1kg 단가: p.prc > span
        price_span = item.find_element(By.CSS_SELECTOR, 'p.prc span')
        price_1kg = price_span.text.strip().replace(',', '')
        if not price_1kg:
            continue

        # 제품 url: h4.name a의 href
        product_link = name_a.get_attribute('href')

        # 수입사명
        importer = '코빈즈'

        data.append({
            '국가': country,
            '커피 이름': coffee_name,
            '가공방식': process_kr,
            '1kg 단가': price_1kg,
            '수입사명': importer,
            '제품 링크': product_link
        })
    except Exception as e:
        print(f'에러: {str(e)}')
        continue

driver.quit()

print('수집된 데이터 개수:', len(data))

df = pd.DataFrame(data)
now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
with pd.ExcelWriter('코빈즈_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 