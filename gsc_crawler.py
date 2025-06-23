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
# 아래 옵션들은 Streamlit Cloud 서버에서 안정적으로 실행하기 위한 필수 옵션들입니다.
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# user-agent 설정은 유지합니다.
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# 드라이버 경로는 환경에 맞게 수정 필요
# 예: chromedriver.exe가 PATH에 있으면 경로 지정 필요 없음

driver = webdriver.Chrome(options=chrome_options)
url = 'https://gsc.coffee/goods/beans_select.php'
driver.get(url)

# 페이지 로딩 대기 조건 강화 (30초)
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.goodsItem'))
)

data = []
dl_lists = driver.find_elements(By.CSS_SELECTOR, 'dl.list_cont')
print('list_cont count:', len(dl_lists))

if dl_lists:
    dl = dl_lists[0]
    rows = dl.find_elements(By.CSS_SELECTOR, 'tr.goodsItem')
    for row in rows:
        try:
            name_cell = row.find_element(By.CSS_SELECTOR, 'td.dp_tit')
            a_tag = name_cell.find_element(By.TAG_NAME, 'a')
            coffee_name_raw = a_tag.text.strip()
            # 첫 번째 단어를 국가명으로 사용하고, 대괄호가 있다면 제거
            first_word = coffee_name_raw.split()[0]
            country = first_word.strip('[]')
            # 첫 번째 단어가 대괄호로 감싸져 있었다면 대괄호를 제거
            if first_word.startswith('[') and first_word.endswith(']'):
                coffee_name = coffee_name_raw.replace(first_word, country, 1).strip()
            else:
                coffee_name = coffee_name_raw.strip()
            # ★20KG세일★가 포함된 상품은 제외
            if '★20KG세일★' in coffee_name:
                continue
            # 첫 번째 dp_none에 img 태그가 있고 src에 soldout이 있으면 제외
            dp_nones = row.find_elements(By.CSS_SELECTOR, 'td.dp_none')
            if len(dp_nones) > 0:
                imgs = dp_nones[0].find_elements(By.TAG_NAME, 'img')
                for img in imgs:
                    src = img.get_attribute('src')
                    if src and 'soldout' in src:
                        raise Exception('soldout 상품 제외')
            # 커피 이름에서 모든 ★텍스트★ 패턴 제거
            coffee_name = re.sub(r'★.*?★', '', coffee_name).strip()
            process_en = dp_nones[1].text.strip() if len(dp_nones) > 1 else ''
            process_kr = process_to_korean(process_en)
            price_1kg = row.find_element(By.CSS_SELECTOR, 'td.on.dp_price_txt').text.strip()
            # '원' 텍스트 제거
            price_1kg = price_1kg.replace('원', '').strip()
            product_link = a_tag.get_attribute('href')
            importer = 'GSC'
            data.append({
                '국가': country,
                '커피 이름': coffee_name,
                '가공방식': process_kr,
                '1kg 단가': price_1kg,
                '수입사명': importer,
                '제품 링크': product_link
            })
        except Exception as e:
            continue
print('수집된 데이터 개수:', len(data))

# 드라이버 종료
driver.quit()

# DataFrame 생성 및 엑셀 저장
# 60kg 단가 컬럼 제거, 나머지만 저장
df = pd.DataFrame(data)

# 현재 날짜/시간 문자열
now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")

# 엑셀 첫 행에 날짜/시간 추가하여 저장
with pd.ExcelWriter('gsc_greenbean.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

# 소요 시간 출력
end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 