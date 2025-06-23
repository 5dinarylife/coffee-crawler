import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

start_time = time.time()  # 크롤링 시작 시각

def clean_coffee_name(name):
    """커피 이름에서 괄호 제거 및 정리"""
    # ( ) 와 [ ] 제거
    name = re.sub(r'[\(\)\[\]]', '', name)
    # 연속된 공백을 하나로 치환
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

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
        # 한글 가공방식 추가
        '내추럴': '내추럴',
        '워시드': '워시드',
        '허니': '허니',
        '에네로빅': '에네로빅',
        '풀리': '풀리',
        '세미': '세미',
        '블랙': '블랙',
        '옐로우': '옐로우',
        '레드': '레드',
        '라이트': '라이트',
        '더블': '더블',
        '웻': '웻',
        '드라이': '드라이',
        '펄프드': '펄프드',
        '퍼먼테이션': '퍼먼테이션',
        '카보닉': '카보닉',
        '마세레이션': '마세레이션',
        '폴리시': '폴리시',
        '디카페인': '디카페인',
        '슈가케인': '슈가케인',
        '스위스워터': '스위스워터',
        # 복합 가공방식 추가
        '슈가케인 디카페인': '슈가케인 디카페인',
        # 추가 가공방식
        '폴리쉬드': '폴리시드',
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
url = 'http://www.fscoffee.co.kr/cus_extend_cart/goods_list'
driver.get(url)

# 빠른 대기 방식: 요소가 나타나자마자 바로 다음 단계로
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'td[data-label="상품명"]'))
    )
except TimeoutException:
    print("상품명 요소를 찾을 수 없습니다. 페이지 로딩을 확인해주세요.")
    driver.quit()
    exit()

# 상품명이 있는 모든 tr 요소 찾기
name_tds = driver.find_elements(By.CSS_SELECTOR, 'td[data-label="상품명"]')

data = []
for name_td in name_tds:
    try:
        name_links = name_td.find_elements(By.CSS_SELECTOR, 'span.goods_name a')
        if not name_links:
            continue
        name_link = name_links[0]
        coffee_name_raw = name_link.text.strip()
        if not coffee_name_raw:
            continue
        # 커피 이름 정리 (괄호 제거)
        coffee_name_cleaned = clean_coffee_name(coffee_name_raw)
        # 국가명: 첫 번째 단어
        country = coffee_name_cleaned.split()[0] if coffee_name_cleaned else ''
        # 가공방식: 마지막 단어 (예외: 디카페인)
        words = coffee_name_cleaned.split()
        if len(words) >= 2 and words[-1] == '디카페인':
            process = words[-2] + ' 디카페인'
        else:
            process = words[-1] if words else ''
        
        # 딕셔너리 직접 체크
        word_mapping = {
            # 한글 가공방식
            '내추럴': '내추럴',
            '워시드': '워시드',
            '허니': '허니',
            '에네로빅': '에네로빅',
            '풀리': '풀리',
            '세미': '세미',
            '블랙': '블랙',
            '옐로우': '옐로우',
            '레드': '레드',
            '라이트': '라이트',
            '더블': '더블',
            '웻': '웻',
            '드라이': '드라이',
            '펄프드': '펄프드',
            '퍼먼테이션': '퍼먼테이션',
            '카보닉': '카보닉',
            '마세레이션': '마세레이션',
            '폴리시': '폴리시',
            '디카페인': '디카페인',
            '슈가케인': '슈가케인',
            '스위스워터': '스위스워터',
            # 복합 가공방식
            '슈가케인 디카페인': '슈가케인 디카페인',
            # 추가 가공방식
            '폴리쉬드': '폴리시드',
        }
        
        if process in word_mapping:
            process_kr = word_mapping[process]
        else:
            process_kr = ''
        
        # 제품 URL 추출 및 완성
        product_link = name_link.get_attribute('href')
        if product_link and product_link.startswith('/'):
            product_link = 'http://www.fscoffee.co.kr' + product_link
        # 해당 tr의 부모 요소 찾기
        tr_element = name_td.find_element(By.XPATH, './..')
        # 1kg 단가 추출 (같은 tr 내에서)
        price_tds = tr_element.find_elements(By.CSS_SELECTOR, 'td[data-label="단가(1kg)"]')
        if price_tds:
            price_text = price_tds[0].text.strip()
            price_1kg = price_text.replace(',', '').replace('원', '').strip()
        else:
            price_1kg = ''
        # 수입사명
        importer = '후성커피'
        data.append({
            '국가': country,
            '커피 이름': coffee_name_cleaned,
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

if data:
    df = pd.DataFrame(data)
    now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
    with pd.ExcelWriter('후성_원두.xlsx', engine='openpyxl') as writer:
        pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
        df.to_excel(writer, index=False, startrow=1)

    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)')
else:
    print("수집된 데이터가 없습니다.") 