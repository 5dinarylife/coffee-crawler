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
from webdriver_utils import get_chromedriver

start_time = time.time()  # 크롤링 시작 시각

def process_to_korean(process):
    word_mapping = {
        'NATURAL': '내추럴', 'Natural': '내추럴', 'natural': '내추럴',
        'WASHED': '워시드', 'Washed': '워시드', 'washed': '워시드',
        'HONEY': '허니', 'Honey': '허니', 'honey': '허니',
        'ANAEROBIC': '아나에어로빅', 'Anaerobic': '아나에어로빅', 'anaerobic': '아나에어로빅',
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
        '훌링': '헐링',
    }
    # 디카페인Co2, 디카페인 Co2 → CO2
    if re.search(r'디카페인\s*Co2', process, re.IGNORECASE):
        return 'CO2'
    # 훌링 → 헐링
    if '훌링' in process:
        return '헐링'
    words = process.split()
    for word in words:
        if word in word_mapping:
            return word_mapping[word]
    return process  # 매핑이 없으면 원본 반환

driver = get_chromedriver()
url = 'https://www.almacielo.com/content/content.php?cont=simpleorder'
driver.get(url)

# tr.search_item이 로드될 때까지 대기
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.search_item'))
)

data = []
rows = driver.find_elements(By.CSS_SELECTOR, 'tr.search_item')
for row in rows:
    try:
        # 품절 상품 제외 (수급정보에 '일시결품' 또는 '품절' 등 표시)
        tds = row.find_elements(By.TAG_NAME, 'td')
        if not tds or len(tds) < 8:
            continue  # 데이터 행이 아니면 skip

        supply_info = tds[6].text.strip()
        if '품절' in supply_info or '일시결품' in supply_info:
            continue

        # 커피 이름 및 URL
        name_elem = row.find_element(By.CSS_SELECTOR, 'td#prd_name a')
        coffee_name_raw = name_elem.text.strip()
        product_url = name_elem.get_attribute('href')
        # 커피 이름 정제
        coffee_name = re.sub(r'^\s*\[.*?\]\s*', '', coffee_name_raw)
        coffee_name = re.sub(r'\s*\*.*$', '', coffee_name)
        coffee_name = coffee_name.strip()
        # 국가명
        country = coffee_name.split()[0] if coffee_name else ''

        # 1kg 단가
        price_1kg = tds[1].text.strip().replace(',', '').replace('원', '')
        price_1kg = re.sub(r'[^0-9]', '', price_1kg)

        # 가공방식
        process_kr = tds[5].text.strip()
        process_kr = process_to_korean(process_kr)

        # 제품 링크
        link_elem = name_elem

        # 수입사명
        importer = '알마씨엘로'

        data.append({
            '국가': country,
            '커피 이름': coffee_name,
            '가공방식': process_kr,
            '1kg 단가': price_1kg,
            '수입사명': importer,
            '제품 링크': product_url
        })
    except Exception as e:
        print(f'에러: {str(e)}')
        continue

driver.quit()

print('수집된 데이터 개수:', len(data))

df = pd.DataFrame(data)
now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
with pd.ExcelWriter('알마씨엘로_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 