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

# 가공방식 영어→한글 변환 딕셔너리 (단어 단위)
def process_to_korean(process):
    word_mapping = {
        # 기본 가공 방식
        'NATURAL': '내추럴',
        'Natural': '내추럴',
        'natural': '내추럴',
        'WASHED': '워시드',
        'Washed': '워시드',
        'washed': '워시드',
        'HONEY': '허니',
        'Honey': '허니',
        'honey': '허니',
        'ANAEROBIC': '아나에어로빅',
        'Anaerobic': '아나에어로빅',
        'anaerobic': '아나에어로빅',
        
        # 수식어
        'FULLY': '풀리',
        'Fully': '풀리',
        'fully': '풀리',
        'SEMI': '세미',
        'Semi': '세미',
        'semi': '세미',
        'BLACK': '블랙',
        'Black': '블랙',
        'black': '블랙',
        'YELLOW': '옐로우',
        'Yellow': '옐로우',
        'yellow': '옐로우',
        'RED': '레드',
        'Red': '레드',
        'red': '레드',
        'LIGHT': '라이트',
        'Light': '라이트',
        'light': '라이트',
        'DOUBLE': '더블',
        'Double': '더블',
        'double': '더블',
        'WET': '웻',
        'Wet': '웻',
        'wet': '웻',
        'DRY': '드라이',
        'Dry': '드라이',
        'dry': '드라이',
        
        # 특수 가공 방식
        'PULPED': '펄프드',
        'Pulped': '펄프드',
        'pulped': '펄프드',
        'FERMENTATION': '퍼먼테이션',
        'Fermentation': '퍼먼테이션',
        'fermentation': '퍼먼테이션',
        'CARBONIC': '카보닉',
        'Carbonic': '카보닉',
        'carbonic': '카보닉',
        'MACERATION': '마세레이션',
        'Maceration': '마세레이션',
        'maceration': '마세레이션',
        'MECERATION': '마세레이션',  # 오타 대응
        'Meceration': '마세레이션',
        'meceration': '마세레이션',
        'POLISH': '폴리시',
        'Polish': '폴리시',
        'polish': '폴리시',
        
        # 디카페인 관련
        'DECAF': '디카페인',
        'Decaf': '디카페인',
        'decaf': '디카페인',
        'SUGARCANE': '슈가케인',
        'Sugarcane': '슈가케인',
        'sugarcane': '슈가케인',
        'SW': '스위스워터',
        'Sw': '스위스워터',
        'sw': '스위스워터',
    }
    
    # 입력된 가공방식을 단어 단위로 분리
    words = process.split()
    
    # 각 단어를 한글로 변환
    translated_words = []
    for word in words:
        translated_word = word_mapping.get(word, word)  # 매핑에 없는 단어는 그대로 유지
        translated_words.append(translated_word)
    
    # 변환된 단어들을 공백으로 연결
    return ' '.join(translated_words)

# 셀레니움 옵션 설정 (브라우저 창 안 띄우기)
chrome_options = Options()
chrome_options.add_argument('--headless=new')  # 최신 크롬 기준
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=chrome_options)
url = 'https://micoffee.co.kr/goods/unit_cart.php'  # 크롤링 대상 URL
driver.get(url)

# 페이지 로딩 대기 조건 (30초)
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'table tbody tr'))
)

data = []
# 테이블의 각 row를 선택 (tr)
rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')

# 영어 국가명 → 한글 국가명 변환 딕셔너리
EN_TO_KR_COUNTRY = {
    'BRAZIL': '브라질',
    'MEXICO': '멕시코',
    'COLOMBIA': '콜롬비아',
    'ECUADOR': '에콰도르',
    'BOLIVIA': '볼리비아',
    'PERU': '페루',
    'COSTA RICA': '코스타리카',
    'GUATEMALA': '과테말라',
    'PANAMA': '파나마',
    'HONDURAS': '온두라스',
    'EL SALVADOR': '엘살바도르',
    'MEXICO': '멕시코',
    'ETHIOPIA': '에티오피아',
    'KENYA': '케냐',
    'TANZANIA': '탄자니아',
    'YEMEN': '예멘',
    'INDONESIA': '인도네시아',
    'P.N.G.': '파푸아뉴기니',
    'INDIA': '인도',
    'THAILAND': '태국',
}
KR_COUNTRY_SET = set(EN_TO_KR_COUNTRY.values())

def extract_country_and_name_from_html(name_td):
    # <br> 태그 기준으로 분리
    name_html = name_td.get_attribute('innerHTML')
    if '<br' in name_html:
        # <br> 앞뒤 텍스트 모두 합쳐서 커피 이름으로 사용 (HTML 태그 제거)
        parts = re.split(r'<br.*?>', name_html)
        coffee_name_base = ' '.join([re.sub('<.*?>', '', p).strip() for p in parts if p.strip()])
    else:
        coffee_name_base = name_td.text.strip()
    # 국가명 추출 및 커피 이름 앞 국가명 중복 방지/추가
    bracket_match = re.match(r'^\s*\[(.*?)\]', coffee_name_base)
    if bracket_match:
        bracket_content = bracket_match.group(1).strip()
        after_bracket = coffee_name_base[bracket_match.end():].strip()
        found_kr_country = None
        for en, kr in EN_TO_KR_COUNTRY.items():
            if en in bracket_content.upper():
                found_kr_country = kr
                break
        after_words = after_bracket.split()
        if found_kr_country:
            country = found_kr_country
            # 커피 이름의 첫 단어가 국가명과 다르면 앞에 국가명 추가
            if after_words:
                if after_words[0] == found_kr_country:
                    coffee_name = after_bracket
                else:
                    coffee_name = found_kr_country + ' ' + after_bracket
            else:
                coffee_name = found_kr_country
        else:
            country = after_words[0] if after_words else ''
            coffee_name = after_bracket
    else:
        words = coffee_name_base.split()
        country = words[0] if words else ''
        coffee_name = coffee_name_base
    return country, coffee_name

for row in rows:
    # 헤더 row(즉, <th>가 포함된 row)는 건너뜀
    if row.find_elements(By.CSS_SELECTOR, 'th'):
        continue
    try:
        name_td = row.find_element(By.CSS_SELECTOR, 'td.name a')
    except NoSuchElementException:
        continue  # 상품 row가 아니면 건너뜀

    try:
        # 커피 이름 및 국가명 추출 (예외 규칙 적용)
        country, coffee_name = extract_country_and_name_from_html(name_td)

        # 가공방식 (두 번째 또는 세 번째 p_i_view)
        process_tds = row.find_elements(By.CSS_SELECTOR, 'td.p_i_view')
        process_en = ''
        if len(process_tds) >= 2:
            process_en = process_tds[1].text.strip()
        process_kr = process_to_korean(process_en)

        # 1kg 단가: 반드시 10번째(td 인덱스 9) td의 텍스트만 사용
        tds = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(tds) > 9:
            price_text = tds[9].text.split('\n')[0].strip()
            price_1kg = re.sub(r'[^\d,]', '', price_text)
        else:
            continue  # 1kg 가격이 없는 row는 건너뜀
        if not price_1kg:
            continue  # 1kg 단가가 없으면 상품 기록하지 않음

        # 제품 URL: javascript:openGoodsView(숫자)에서 숫자만 추출
        href = name_td.get_attribute('href')
        product_link = ''
        if href:
            product_id_match = re.search(r'openGoodsView\((\d+)\)', href)
            if product_id_match:
                product_id = product_id_match.group(1)
                product_link = f'https://micoffee.co.kr/goods/goods_view.php?goodsNo={product_id}'

        # 수입사명
        importer = '엠아이커피'

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

print('수집된 데이터 개수:', len(data))

# 드라이버 종료
driver.quit()

# DataFrame 생성 및 엑셀 저장
df = pd.DataFrame(data)

# 현재 날짜/시간 문자열
now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")

# 엑셀 첫 행에 날짜/시간 추가하여 저장
with pd.ExcelWriter('엠아이커피_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

# 소요 시간 출력
end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 