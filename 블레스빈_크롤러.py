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
    }
    words = process.split()
    for word in words:
        if word in word_mapping:
            return word_mapping[word]
    return process  # 매핑이 없으면 원본 반환

chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.blessbean.co.kr/shop/item_one_click.php'
driver.get(url)

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.ca_box tr'))
)

data = []
rows = driver.find_elements(By.CSS_SELECTOR, 'tbody.ca_box tr.it_list')
for row in rows:
    # 품절 상품 제외
    class_attr = row.get_attribute('class')
    if not class_attr:
        class_attr = ''
    if 'soldout' in class_attr:
        continue
    try:
        # 커피 이름 (it_name의 value)
        it_name_input = row.find_element(By.CSS_SELECTOR, 'input[name^="it_name"]')
        coffee_name_raw = it_name_input.get_attribute('value')
        if not coffee_name_raw:
            continue
        coffee_name_raw = coffee_name_raw.strip()
        
        # 대괄호로 묶인 내용 제거 및 국가명 설정
        bracket_match = re.match(r'^\s*\[(.*?)\](.*)', coffee_name_raw)
        if bracket_match:
            # 대괄호 뒤의 텍스트에서 첫 단어를 국가명으로 설정
            after_bracket = bracket_match.group(2).strip()
            country = after_bracket.split()[0] if after_bracket else ''
            # 커피 이름은 대괄호를 제거한 전체 텍스트
            coffee_name = after_bracket
        else:
            # 대괄호가 없는 경우 기존 로직 유지
            country = coffee_name_raw.split()[0] if coffee_name_raw else ''
            coffee_name = coffee_name_raw

        # 가공방식: td.process(클래스 포함) 텍스트에서 주요 키워드만 추출
        process_td = row.find_element(By.CSS_SELECTOR, 'td.process')
        process_text = process_td.text.strip() if process_td.text else ''
        process_kr = process_to_korean(process_text)
        # 1kg 가격: td.order_price의 value
        price_input = row.find_element(By.CSS_SELECTOR, 'input[name^="it_price"]')
        price_1kg = price_input.get_attribute('value')
        if not price_1kg:
            continue
        price_1kg = price_1kg.strip()
        # 제품 url: td.it_name > a의 href
        it_name_td = row.find_element(By.CSS_SELECTOR, 'td.it_name a')
        product_link = it_name_td.get_attribute('href')
        # 수입사명
        importer = '블레스빈'
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
with pd.ExcelWriter('블레스빈_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 