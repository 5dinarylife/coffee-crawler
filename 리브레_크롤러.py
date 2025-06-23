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
    return '워시드'  # 매핑이 없으면 기본값으로 '워시드' 반환

def extract_processing_method(coffee_name):
    """커피 이름에서 가공방식을 추출하는 함수"""
    # 가공방식 매핑 (한글)
    processing_methods = {
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
        '스위스워터': '스위스워터'
    }
    
    # 두 단어 조합 가공방식 매핑
    two_word_methods = {
        '무산소 내추럴': '무산소 내추럴',
        '레드 허니': '레드 허니',
        '무산소발효 내추럴': '무산소 내추럴',  # 무산소발효 내추럴을 무산소 내추럴로 통일
        '블랙 허니': '블랙 허니',
        '옐로우 허니': '옐로우 허니',
        '레드 내추럴': '레드 내추럴',
        '블랙 내추럴': '블랙 내추럴',
        '옐로우 내추럴': '옐로우 내추럴',
        '카보닉 마세레이션': '카보닉 마세레이션',
        '웻 허니': '웻 허니',
        '드라이 허니': '드라이 허니',
        '세미 워시드': '세미 워시드',
        '풀리 워시드': '풀리 워시드',
        '더블 펄프드': '더블 펄프드',
        '라이트 로스팅': '라이트 로스팅',
        '다크 로스팅': '다크 로스팅',
        '미디엄 로스팅': '미디엄 로스팅'
    }
    
    # 모든 가공방식 매핑 합치기
    all_methods = {**processing_methods, **two_word_methods}
    
    words = coffee_name.split()
    
    # 1. 괄호가 있는 경우: 괄호 앞의 단어 확인
    if '(' in coffee_name:
        # 괄호 앞 부분만 추출
        before_parenthesis = coffee_name.split('(')[0].strip()
        before_words = before_parenthesis.split()
        if len(before_words) >= 2:
            # 마지막 두 단어 조합 확인
            last_two = ' '.join(before_words[-2:])
            if last_two in two_word_methods:
                return two_word_methods[last_two]
        if before_words:
            last_word = before_words[-1]
            if last_word in all_methods:
                return all_methods[last_word]
    
    # 2. 마지막 두 단어 조합 확인 (우선순위)
    if len(words) >= 2:
        last_two = ' '.join(words[-2:])
        if last_two in two_word_methods:
            return two_word_methods[last_two]
    
    # 3. 마지막 단어가 가공방식인지 확인
    if words:
        last_word = words[-1]
        if last_word in all_methods:
            return all_methods[last_word]
    
    # 4. 마지막에서 두 번째 단어가 가공방식인지 확인 (Lot.2 같은 경우)
    if len(words) >= 2:
        second_last_word = words[-2]
        if second_last_word in all_methods:
            return all_methods[second_last_word]
    
    # 5. 전체 이름에서 가공방식 단어 찾기
    for method in all_methods:
        if method in coffee_name:
            return all_methods[method]
    
    return '워시드'  # 기본값

def clean_coffee_name(name):
    """커피 이름에서 [ ] 안의 내용, <br> 태그, ( ) 안의 내용을 제거하고 정리"""
    # [ ] 안의 내용 제거
    name = re.sub(r'\[.*?\]', '', name)
    # <br> 태그 제거
    name = name.replace('<br>', ' ')
    # ( ) 안의 내용 제거
    name = re.sub(r'\([^)]*\)', '', name)
    # &amp;를 &로 변환
    name = name.replace('&amp;', '&')
    # 순위 표현 제거 (1위~20위까지)
    name = re.sub(r'\d+위', '', name)
    # 연속된 공백을 하나로 치환
    name = re.sub(r'\s+', ' ', name)
    # 앞뒤 공백 제거
    name = name.strip()
    
    # 디카페인이 앞에 오는 경우 뒤로 보내기
    words = name.split()
    if words and words[0] == '디카페인':
        # 디카페인을 제거하고 나머지 단어들만 남기기
        remaining_words = words[1:]
        if remaining_words:
            # 나머지 단어들 + 디카페인 순서로 재구성
            name = ' '.join(remaining_words) + ' 디카페인'
    
    return name

driver = get_chromedriver()
url = 'https://coffeelibre.kr/category/%EC%83%9D%EB%91%90%EC%86%8C%EB%B6%84/57/'
driver.get(url)

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'li.item.xans-record-'))
)

data = []
items = driver.find_elements(By.CSS_SELECTOR, 'li.item.xans-record-')
for item in items:
    try:
        # 커피 이름
        name_a = item.find_element(By.CSS_SELECTOR, 'p.name strong a')
        coffee_name_raw = name_a.get_attribute('innerHTML')
        if not coffee_name_raw:
            continue
        coffee_name_raw = coffee_name_raw.strip()
        if not coffee_name_raw:
            continue

        # 커피 이름 정리
        coffee_name = clean_coffee_name(coffee_name_raw)
        if not coffee_name:
            continue

        # 국가명: 정제된 커피 이름의 첫 번째 단어
        country = coffee_name.split()[0] if coffee_name else ''

        # 가공방식: 새로운 함수로 추출
        process_kr = extract_processing_method(coffee_name)

        # 1kg 단가: span.price > span.displaynonedisplaynone > b
        try:
            price_b = item.find_element(By.CSS_SELECTOR, 'li.price span.displaynonedisplaynone b')
            price_1kg = price_b.text.strip().replace(',', '')
        except NoSuchElementException:
            # SOLDOUT인 경우 건너뛰기
            continue

        if not price_1kg:
            continue

        # 제품 URL: p.name strong a의 href
        product_link = name_a.get_attribute('href')
        if product_link and product_link.startswith('/'):
            product_link = 'https://coffeelibre.kr' + product_link

        # 수입사명
        importer = '커피리브레'

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
with pd.ExcelWriter('리브레_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 