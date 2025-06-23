import time
import re
import pandas as pd
from selenium.webdriver.common.by import By
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
        'INFUSED': '인퓨즈드', 'Infused': '인퓨즈드', 'infused': '인퓨즈드',
        'M/W': '마운틴워터 프로세스', 'm/w': '마운틴워터 프로세스', 'MOUNTAINWATER': '마운틴워터 프로세스',
        'WET-POLISH': '웻 폴리시', 'Wet-Polish': '웻 폴리시', 'wet-polish': '웻 폴리시',
        # 단어별 변환을 위해 Wet, Polish도 이미 포함됨
    }
    # 하이픈(-)이 있는 경우 분리해서 각각 변환
    words = []
    for w in process.split():
        if '-' in w:
            words.extend(w.split('-'))
        else:
            words.append(w)
    return ' '.join([str(word_mapping.get(word, word)) for word in words])

driver = get_chromedriver()
url = 'https://www.mcffee.co.kr/goods/goods_list.php?cateCd=001'

# 1. 첫 페이지에서 마지막 페이지 번호 파싱
driver.get(url)
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.prdList.grid3 li'))
)
# 페이지네이션 영역에서 마지막 페이지 번호 추출
try:
    try:
        paging = driver.find_element(By.CSS_SELECTOR, 'div.xans-product-paging')
    except NoSuchElementException:
        paging = driver.find_element(By.CSS_SELECTOR, 'div.ec-base-paginate')
    page_links = paging.find_elements(By.CSS_SELECTOR, 'a')
    last_page = 1
    for link in page_links:
        try:
            num = int(link.text.strip())
            if num > last_page:
                last_page = num
        except ValueError:
            continue
except Exception as e:
    print('페이지네이션 파싱 실패, 1페이지만 크롤링합니다:', e)
    last_page = 1

data = []
for page in range(1, last_page + 1):
    page_url = f'https://greenbeans.co.kr/product/list.html?cate_no=128&page={page}'
    driver.get(page_url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.prdList.grid3 li'))
        )
        items = driver.find_elements(By.CSS_SELECTOR, 'ul.prdList.grid3 li')
        if not items:
            continue  # 상품 li가 없는 페이지는 건너뜀
        for item in items:
            try:
                # 품절 상품 예외처리: li 내부에 alt="품절"인 img가 있으면 건너뜀
                soldout_imgs = item.find_elements(By.CSS_SELECTOR, 'img[alt="품절"]')
                if soldout_imgs:
                    continue
                # 커피 이름 a 태그가 없는 li는 건너뜀
                try:
                    name_el = item.find_element(By.CSS_SELECTOR, 'div.description strong.name a')
                except NoSuchElementException:
                    continue
                raw_name = name_el.text.strip()
                # [ ... ] 제거
                name_no_bracket = re.sub(r'\[.*?\]', '', raw_name).strip()
                # '_1kg/5kg/20kg' 등 단위 표기 제거
                name_no_unit = re.sub(r'_\d+kg/\d+kg/\d+kg$', '', name_no_bracket).strip()
                # ( ... ) 추출 (가공방식)
                process_match = re.search(r'\((.*?)\)', name_no_unit)
                process_kr = ''
                coffee_name_base = name_no_unit
                if process_match:
                    process_en = process_match.group(1).strip()
                    process_kr = process_to_korean(process_en)
                    # 커피 이름에서 ( ... ) 제거
                    coffee_name_base = re.sub(r'\(.*?\)', '', name_no_unit).strip()
                else:
                    # ( )가 없을 때, 마지막 단어가 영어(가공방식)라면 추출
                    words = coffee_name_base.split()
                    if words and re.match(r'^[A-Za-z/-]+$', words[-1]):
                        process_en = words[-1]
                        process_kr = process_to_korean(process_en)
                        coffee_name_base = ' '.join(words[:-1])
                    else:
                        # 마지막 단어가 한글 가공방식(딕셔너리 값)과 일치하면 가공방식으로 분리하되, 커피 이름에서는 그대로 둔다
                        if words:
                            last_word = words[-1]
                            process_kr_values = set([
                                '내추럴', '워시드', '허니', '에네로빅', '아나에어로빅', '풀리', '세미', '블랙', '옐로우', '레드', '라이트', '더블', '웻', '드라이', '펄프드', '퍼먼테이션', '카보닉', '마세레이션', '폴리시', '디카페인', '슈가케인', '스위스워터', '인퓨즈드', '마운틴워터 프로세스', '웻 폴리시', '레드허니', '블랙허니', '옐로우허니', '화이트허니', '골드허니', '그레이허니', '핑크허니', '오렌지허니', '퍼플허니', '그린허니', '허니프로세스'
                            ])
                            if last_word in process_kr_values:
                                process_kr = last_word
                                # 커피 이름에서는 제거하지 않음
                # 커피 이름 완성
                coffee_name = f'{coffee_name_base} {process_kr}'.strip() if process_kr and process_kr not in coffee_name_base else coffee_name_base
                # 국가명: 커피 이름의 첫 단어
                country = coffee_name_base.split()[0] if coffee_name_base else ''
                # 1kg 단가
                price_1kg = ''
                try:
                    price_el = item.find_element(By.CSS_SELECTOR, 'div.description ul.xans-product-listitem li span[style*="font-size:18px"]')
                    price_1kg = re.sub(r'[^\d]', '', price_el.text)
                except NoSuchElementException:
                    pass
                # 보강: li 내 모든 span에서 '원'이 포함된 첫 번째 span을 찾음
                if not price_1kg:
                    try:
                        price_lis = item.find_elements(By.CSS_SELECTOR, 'div.description ul.xans-product-listitem li')
                        for li in price_lis:
                            spans = li.find_elements(By.TAG_NAME, 'span')
                            for span in spans:
                                if '원' in span.text:
                                    price_1kg = re.sub(r'[^\d]', '', span.text)
                                    break
                            if price_1kg:
                                break
                    except Exception:
                        pass
                # 제품 링크 (절대경로 변환)
                product_link = name_el.get_attribute('href')
                if product_link and product_link.startswith('/'):
                    product_link = 'https://greenbeans.co.kr' + product_link
                importer = '맥널티'
                data.append({
                    '국가': country,
                    '커피 이름': coffee_name,
                    '가공방식': process_kr,
                    '1kg 단가': price_1kg,
                    '수입사명': importer,
                    '제품 링크': product_link
                })
            except Exception as e:
                print(f'상품 파싱 에러: {str(e)}')
                continue
    except Exception as e:
        print(f'페이지 파싱 에러: {str(e)}')
        continue

print('수집된 데이터 개수:', len(data))

df = pd.DataFrame(data)
now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
with pd.ExcelWriter('맥널티_원두.xlsx', engine='openpyxl') as writer:
    pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
    df.to_excel(writer, index=False, startrow=1)

end_time = time.time()
elapsed = end_time - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)
print(f'크롤링 및 엑셀 저장 완료! (소요 시간: {minutes}분 {seconds}초)') 