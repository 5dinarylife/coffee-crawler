import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
        '훌링': '헐링',
    }
    if re.search(r'디카페인\s*Co2', process, re.IGNORECASE):
        return 'CO2'
    if '훌링' in process:
        return '헐링'
    words = process.split()
    for word in words:
        if word in word_mapping:
            return word_mapping[word]
    return process

chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=chrome_options)

urls = [
    'https://sopexkorea.com/product/list.html?cate_no=27',
    'https://sopexkorea.com/product/list.html?cate_no=26',
    'https://sopexkorea.com/product/list.html?cate_no=24',
]

data = []
for url in urls:
    driver.get(url)
    # 더보기 버튼이 있으면 모두 클릭 (스크롤 내리기 포함, stealth 옵션 적용)
    while True:
        try:
            # 스크롤을 맨 아래로 내림 (버튼이 화면에 보이도록)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.0)
            more_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.xans-product-listmore.more a.btnMore'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", more_btn)
            time.sleep(0.5)
            if not more_btn.is_displayed() or not more_btn.is_enabled():
                print('버튼이 비활성화 또는 비노출 상태')
                break
            driver.execute_script("arguments[0].click();", more_btn)
            print('view more 버튼 클릭!')
            time.sleep(2.0)
        except Exception as e:
            print('더보기 버튼 없음 또는 클릭 불가:', e)
            break
    products = driver.find_elements(By.CSS_SELECTOR, 'li.prd-item.xans-record-')
    for product in products:
        try:
            # 커피 이름
            name_elem = product.find_element(By.CSS_SELECTOR, 'div.name > a > span')
            coffee_name_raw = name_elem.text.strip()
            # [SALE], [Sale], [sale]로 시작하면 제외
            if re.match(r'^\[(SALE|Sale|sale)\]', coffee_name_raw):
                continue
            # 그 외 [ ... ]는 이름에서 제거
            coffee_name = re.sub(r'^\[.*?\]\s*', '', coffee_name_raw).strip()
            # 국가명
            country = coffee_name.split()[0] if coffee_name else ''
            # 가공방식
            process = coffee_name.split()[-1] if coffee_name else ''
            process_kr = process_to_korean(process)
            # 제품 URL
            url_elem = product.find_element(By.CSS_SELECTOR, 'div.name > a')
            product_url = url_elem.get_attribute('href')
            if product_url is None:
                product_url = ''
            if product_url.startswith('/'):
                product_url = 'https://sopexkorea.com' + product_url
            # 1kg 단가
            price_elem = product.find_element(By.CSS_SELECTOR, 'ul.spec li.price.pSale span[style*="font-size:14px"]')
            price_1kg = re.sub(r'[^0-9]', '', price_elem.text)
            data.append({
                '국가': country,
                '커피 이름': coffee_name,
                '가공방식': process_kr,
                '1kg 단가': price_1kg,
                '수입사명': '소펙스코리아',
                '제품 링크': product_url
            })
        except Exception as e:
            print(f'에러: {str(e)}')
            continue

driver.quit()

print('수집된 데이터 개수:', len(data))

df = pd.DataFrame(data)
now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
with pd.ExcelWriter('소펙스_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 