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

def clean_coffee_name(name):
    """커피 이름 정제 함수"""
    # [생두] 텍스트 제거
    name = re.sub(r'^\[생두\]\s*', '', name)
    
    # 영문을 한글 음으로 변환하는 매핑
    english_to_korean = {
        'Ecuador': '에콰도르', 'Colombia': '콜롬비아', 'Brazil': '브라질',
        'Ethiopia': '에티오피아', 'Kenya': '케냐', 'Guatemala': '과테말라',
        'Costa Rica': '코스타리카', 'El Salvador': '엘살바도르', 'Honduras': '온두라스',
        'Panama': '파나마', 'Peru': '페루', 'Bolivia': '볼리비아',
        'Yemen': '예멘', 'Indonesia': '인도네시아', 'India': '인도',
        'Geisha': '게이샤', 'Gesha': '게이샤', 'Sidra': '시드라',
        'Bourbon': '부르봉', 'Pacamara': '파카마라', 'Catuai': '카투아이',
        'Caturra': '카투라', 'Typica': '티피카', 'Mundo Novo': '문도 노보',
        'Green': '그린', 'Yellow': '옐로우', 'Red': '레드',
        'Washed': '워시드', 'Natural': '내추럴', 'Honey': '허니',
        'Anaerobic': '에네로빅', 'Carbonic': '카보닉', 'Maceration': '마세레이션',
        'El': '엘', 'Dorado': '도라도', 'Noria': '노리아',
        'Obraje': '오브라헤', 'Villa': '빌라', 'Sol': '솔',
        'San': '산', 'Andres': '안드레스', 'Chorora': '초로라',
        'Yambamine': '얌바민', 'Passion': '패션', 'Flowers': '플라워스',
        'Alasitas': '알라시타스', 'Baba': '바바', 'Blend': '블렌드',
        'La': '라', 'Guadua': '과두아', 'CVM': 'CVM',  # 약자는 그대로 유지
        'Hacienda': '하시엔다', 'hacienda': '하시엔다',  # 하시엔다 추가
        'Luciana': '루시아나', 'Estrella': '에스트렐라', 'Paraiso': '파라이소',
        'Quebrada': '케브라다', 'Grande': '그란데', 'Kenia': '케니아',
        'Wessi': '웨시', 'Tima': '티마', 'Kangocho': '캉고초',
        'Ziwa': '지와', 'Alo': '알로', 'Coffee': '커피',
        'Mosto': '모스토', 'Yirgacheffe': '예가체프', 'Idido': '이디도',
        'Edido': '에디도', 'Banko': '반코', 'Chelchele': '첼첼레',
        'Bookkisa': '부키사', 'Pink': '핑크', 'White': '화이트'
    }
    
    # 첫 번째 [ ] 괄호 제거 (국가명 추출용)
    name = re.sub(r'^\[([^\]]+)\]\s*', r'\1 ', name)
    
    # 나머지 [ ] 괄호와 내용 모두 제거
    name = re.sub(r'\[[^\]]*\]', '', name)
    
    # 공백 정리
    name = re.sub(r'\s+', ' ', name).strip()
    
    # 영문을 한글 음으로 변환
    for english, korean in english_to_korean.items():
        name = re.sub(r'\b' + re.escape(english) + r'\b', korean, name, flags=re.IGNORECASE)
    
    return name

def convert_to_native_pronunciation(name, country):
    """국가별 언어 특성에 맞는 발음 변환"""
    
    # 국가별 언어 매핑
    country_language = {
        '콜롬비아': 'spanish',
        '브라질': 'portuguese', 
        '과테말라': 'spanish',
        '코스타리카': 'spanish',
        '엘살바도르': 'spanish',
        '온두라스': 'spanish',
        '파나마': 'spanish',
        '페루': 'spanish',
        '볼리비아': 'spanish',
        '에콰도르': 'spanish',
        '케냐': 'swahili',
        '에티오피아': 'amharic',
        '예멘': 'arabic',
        '인도네시아': 'indonesian',
        '인도': 'hindi'
    }
    
    language = country_language.get(country, 'english')
    
    if language == 'spanish':
        # 스페인어 발음 규칙
        spanish_rules = {
            'Los Angeles': '로스 앙헬레스',
            'San Jose': '산 호세',
            'Santa Rosa': '산타 로사',
            'El Salvador': '엘 살바도르',
            'Costa Rica': '코스타 리카',
            'Guatemala': '과테말라',
            'Honduras': '온두라스',
            'Panama': '파나마',
            'Peru': '페루',
            'Bolivia': '볼리비아',
            'Ecuador': '에콰도르',
            'Colombia': '콜롬비아',
            'Bourbon': '부르봉',
            'Catuai': '카투아이',
            'Caturra': '카투라',
            'Typica': '티피카',
            'Pacamara': '파카마라',
            'Mundo Novo': '문도 노보',
            'Geisha': '게이샤',
            'Gesha': '게이샤',
            'Sidra': '시드라',
            'Dorado': '도라도',
            'Noria': '노리아',
            'Obraje': '오브라헤',
            'Villa': '빌라',
            'Sol': '솔',
            'San': '산',
            'Andres': '안드레스',
            'Chorora': '초로라',
            'Yambamine': '얌바민',
            'Passion': '패션',
            'Flowers': '플라워스',
            'Alasitas': '알라시타스',
            'Baba': '바바',
            'Blend': '블렌드',
            'La': '라',
            'Guadua': '과두아',
            'Luciana': '루시아나',
            'Estrella': '에스트렐라',
            'Paraiso': '파라이소',
            'Quebrada': '케브라다',
            'Grande': '그란데',
            'Hacienda': '하시엔다',
            'Mosto': '모스토'
        }
        
        for spanish, korean in spanish_rules.items():
            name = re.sub(r'\b' + re.escape(spanish) + r'\b', korean, name, flags=re.IGNORECASE)
    
    elif language == 'portuguese':
        # 포르투갈어 발음 규칙
        portuguese_rules = {
            'Bourbon': '부르봉',
            'Catuai': '카투아이',
            'Caturra': '카투라',
            'Typica': '티피카',
            'Mundo Novo': '문도 노보',
            'Brazil': '브라질',
            'Sao Paulo': '상 파울루',
            'Minas Gerais': '미나스 제라이스',
            'Bahia': '바이아',
            'Espirito Santo': '에스피리투 산투',
            'Rio de Janeiro': '리우 데 자네이로',
            'Parana': '파라나',
            'Santa Catarina': '산타 카타리나',
            'Rio Grande do Sul': '히우 그란지 두 술'
        }
        
        for portuguese, korean in portuguese_rules.items():
            name = re.sub(r'\b' + re.escape(portuguese) + r'\b', korean, name, flags=re.IGNORECASE)
    
    elif language == 'swahili':
        # 스와힐리어/케냐 현지어 발음 규칙
        swahili_rules = {
            'Kivanga': '키방가',
            'Kangocho': '캉고초',
            'Ziwa': '지와',
            'Alo': '알로',
            'Wessi': '웨시',
            'Tima': '티마',
            'Kenia': '케니아',
            'Yirgacheffe': '예가체프',
            'Idido': '이디도',
            'Edido': '에디도',
            'Banko': '반코',
            'Chelchele': '첼첼레',
            'Bookkisa': '부키사'
        }
        
        for swahili, korean in swahili_rules.items():
            name = re.sub(r'\b' + re.escape(swahili) + r'\b', korean, name, flags=re.IGNORECASE)
    
    elif language == 'amharic':
        # 암하라어(에티오피아) 발음 규칙
        amharic_rules = {
            'Yirgacheffe': '예가체프',
            'Sidamo': '시다모',
            'Harrar': '하라르',
            'Limu': '리무',
            'Jimma': '지마',
            'Guji': '구지',
            'Gedeo': '게데오',
            'Kochere': '코체레',
            'Konga': '콩가',
            'Chelchele': '첼첼레',
            'Bookkisa': '부키사',
            'Idido': '이디도',
            'Edido': '에디도',
            'Banko': '반코'
        }
        
        for amharic, korean in amharic_rules.items():
            name = re.sub(r'\b' + re.escape(amharic) + r'\b', korean, name, flags=re.IGNORECASE)
    
    # 추가 예외 처리
    name = name.replace('코스타 리카', '코스타리카')
    
    return name

def extract_country(name):
    """커피 이름에서 국가명 추출"""
    # 첫 번째 단어가 국가명
    words = name.split()
    if words:
        return words[0]
    return ''

def get_total_pages(driver):
    """총 페이지 수를 가져오는 함수"""
    try:
        # 마지막 페이지 링크에서 페이지 번호 추출
        last_page_link = driver.find_element(By.CSS_SELECTOR, 'a.last')
        href = last_page_link.get_attribute('href')
        if href:
            # URL에서 page=숫자 부분 추출
            match = re.search(r'page=(\d+)', href)
            if match:
                total_pages = int(match.group(1))
                print(f'마지막 페이지 링크에서 추출한 총 페이지 수: {total_pages}')
                return total_pages
        
        # 백업 방법: 페이지네이션 영역에서 숫자들 찾기
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, '.ec-base-paginate ol li a')
        max_page = 1
        
        for element in pagination_elements:
            try:
                page_num = int(element.text.strip())
                if page_num > max_page:
                    max_page = page_num
            except ValueError:
                continue
        
        print(f'페이지네이션에서 추출한 최대 페이지 번호: {max_page}')
        return max_page
    except Exception as e:
        print(f'총 페이지 수 확인 중 에러: {str(e)}')
        return 1

def go_to_page(driver, page_num):
    """특정 페이지로 이동하는 함수"""
    try:
        # 페이지 번호로 직접 이동
        page_url = f'https://momos.co.kr/custom/sub/product_category/green_bean_all_shop.html?cate_no=64&page={page_num}'
        print(f'페이지 {page_num}로 이동: {page_url}')
        driver.get(page_url)
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.xans-record-'))
        )
        time.sleep(3)  # 추가 대기
        return True
    except TimeoutException:
        print(f'페이지 {page_num} 로딩 타임아웃')
        return False
    except Exception as e:
        print(f'페이지 {page_num} 이동 중 에러: {str(e)}')
        return False

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
url = 'https://momos.co.kr/custom/sub/product_category/green_bean_all_shop.html?cate_no=64'
driver.get(url)

# 첫 페이지 로딩 대기
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'li.xans-record-'))
    )
    print('첫 페이지 로딩 완료')
except TimeoutException:
    print('첫 페이지 로딩 실패')
    driver.quit()
    exit()

# 총 페이지 수 확인
total_pages = get_total_pages(driver)
print(f'총 페이지 수: {total_pages}')

data = []
page = 1
consecutive_soldout_pages = 0  # 연속 품절 페이지 카운트
max_consecutive_soldout = 2    # 연속 품절 페이지 허용 개수

while page <= total_pages:
    print(f'페이지 {page}/{total_pages} 크롤링 중...')
    
    # 현재 페이지 URL 확인
    current_url = driver.current_url
    print(f'  - 현재 URL: {current_url}')
    
    # 현재 페이지의 상품들 수집 - 현재 페이지에 표시된 상품만 정확히 선택
    # 페이지별로 고유한 컨테이너를 찾기 위해 더 구체적인 선택자 사용
    time.sleep(3)  # 페이지 로딩 대기
    
    # 현재 페이지의 상품 컨테이너를 정확히 찾기
    try:
        # 현재 페이지의 상품 리스트 컨테이너 찾기
        product_container = driver.find_element(By.CSS_SELECTOR, 'ul.prdList.prdList01.grid4')
        
        # 현재 페이지에 표시된 상품들만 선택
        # 현재 페이지의 상품들만 정확히 선택하기 위해 더 구체적인 방법 사용
        all_items = product_container.find_elements(By.CSS_SELECTOR, 'li.xans-record-')
        
        # ID가 있는 상품만 필터링
        items = []
        for item in all_items:
            item_id = item.get_attribute('id')
            if item_id and item_id.startswith('anchorBoxId_'):
                items.append(item)
        
        print(f'  - 전체 발견된 상품 개수: {len(all_items)}')
        print(f'  - ID가 있는 상품 개수: {len(items)}')
        
        # 디버깅: 상품 ID들 확인
        if len(items) > 12:
            print(f'  - 경고: 비정상적으로 많은 상품({len(items)}개)이 선택됨.')
            print(f'  - 상품 ID들:')
            for i, item in enumerate(items[:15]):  # 처음 15개만 출력
                try:
                    item_id = item.get_attribute('id')
                    print(f'    {i+1}: {item_id}')
                except:
                    print(f'    {i+1}: ID 없음')
            
    except NoSuchElementException:
        print(f'  - 상품 컨테이너를 찾을 수 없음. 페이지 로딩 문제일 수 있음.')
        # 다음 페이지로 이동
        if page < total_pages:
            if not go_to_page(driver, page + 1):
                print(f'페이지 {page + 1} 이동 실패, 크롤링 중단')
                break
        page += 1
        continue
    
    page_soldout_count = 0  # 현재 페이지의 품절 상품 개수
    page_valid_count = 0    # 현재 페이지의 정상 상품 개수
    
    for idx, item in enumerate(items, 1):
        try:
            # 품절 상품 체크 - soldout span이 있는 경우만 체크
            try:
                soldout_span = item.find_element(By.CSS_SELECTOR, 'div.thumbnail div.prdImg a span.soldout')
                soldout_classes = soldout_span.get_attribute('class')
                # displaynone이 없으면 품절, 있으면 정상 상품
                if soldout_classes and 'displaynone' not in soldout_classes:
                    page_soldout_count += 1
                    continue
            except NoSuchElementException:
                # soldout span이 없으면 체크하지 않고 다음 단계로 진행
                pass
            
            # 커피 이름 - 더 유연한 선택자 사용
            try:
                # 방법 1: span 태그가 있는 경우
                name_element = item.find_element(By.CSS_SELECTOR, 'div.description div.name a span')
                coffee_name_raw = name_element.text.strip()
            except NoSuchElementException:
                try:
                    # 방법 2: span 태그가 없는 경우, a 태그에서 직접 가져오기
                    name_element = item.find_element(By.CSS_SELECTOR, 'div.description div.name a')
                    coffee_name_raw = name_element.text.strip()
                except NoSuchElementException:
                    continue
            
            if not coffee_name_raw:
                continue
            
            # 커피 이름 정제
            coffee_name_cleaned = clean_coffee_name(coffee_name_raw)
            
            # 국가명 추출
            country = extract_country(coffee_name_cleaned)
            
            # 가격 - 정확한 선택자 사용 (data-title="판매가"인 li의 첫 번째 span)
            price_element = item.find_element(By.CSS_SELECTOR, 'li[data-title="판매가"] span')
            price_text = price_element.text.strip()
            price_1kg = price_text.replace(',', '').replace('원', '')
            if not price_1kg:
                continue
            
            # 제품 링크 - 정확한 선택자 사용
            link_element = item.find_element(By.CSS_SELECTOR, 'div.description div.name a')
            product_link = link_element.get_attribute('href')
            if product_link and not product_link.startswith('http'):
                product_link = 'https://momos.co.kr' + product_link
            
            # 가공방식 추출 (커피 이름에서 추출)
            process_keywords = ['워시드', '내추럴', '허니', '에네로빅', '카보닉', '마세레이션']
            process_kr = ''
            for keyword in process_keywords:
                if keyword in coffee_name_cleaned:
                    process_kr = keyword
                    break
            
            # 수입사명
            importer = '모모스'
            
            # 국가별 언어 특성에 맞는 발음 변환
            coffee_name_native = convert_to_native_pronunciation(coffee_name_cleaned, country)
            
            data.append({
                '국가': country,
                '커피 이름': coffee_name_native,
                '가공방식': process_kr,
                '1kg 단가': price_1kg,
                '수입사명': importer,
                '제품 링크': product_link
            })
            
            page_valid_count += 1
            
        except Exception as e:
            continue
    
    print(f'  - 페이지 {page} 결과: 정상상품 {page_valid_count}개, 품절상품 {page_soldout_count}개')
    
    # 품절 상품이 발견되면 즉시 크롤링 중단
    if page_soldout_count > 0:
        print(f'  - 품절 상품이 발견됨. 크롤링 중단.')
        break
    
    # 다음 페이지로 이동
    if page < total_pages:
        if not go_to_page(driver, page + 1):
            print(f'페이지 {page + 1} 이동 실패, 크롤링 중단')
            break
    
    page += 1

driver.quit()

print(f'수집 완료: 총 {len(data)}개 상품')

if data:
    df = pd.DataFrame(data)
    now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
    
    # 기존 파일명 사용 (덮어쓰기)
    filename = '모모스_원두.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
        df.to_excel(writer, index=False, startrow=1)
    
    print(f'엑셀 파일 저장 완료: {filename}')
else:
    print('수집된 데이터가 없습니다.')

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'소요 시간: {minutes}분 {seconds}초') 