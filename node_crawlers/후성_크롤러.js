// 후성 크롤러 (Puppeteer 기반)
// 기존 후성_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

const puppeteer = require('puppeteer');
const xlsx = require('xlsx');

// 커피 이름 정제 함수
function cleanCoffeeName(name) {
  name = name.replace(/[\(\)\[\]]/g, '');
  name = name.replace(/\s+/g, ' ');
  return name.trim();
}

// 가공방식 영어/한글→한글 변환 딕셔너리
const processToKorean = (process) => {
  const wordMapping = {
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
    '애너러빅': '에네로빅',
    // 한글 가공방식
    '내추럴': '내추럴', '워시드': '워시드', '허니': '허니', '에네로빅': '에네로빅',
    '풀리': '풀리', '세미': '세미', '블랙': '블랙', '옐로우': '옐로우', '레드': '레드',
    '라이트': '라이트', '더블': '더블', '웻': '웻', '드라이': '드라이', '펄프드': '펄프드',
    '퍼먼테이션': '퍼먼테이션', '카보닉': '카보닉', '마세레이션': '마세레이션', '폴리시': '폴리시',
    '디카페인': '디카페인', '슈가케인': '슈가케인', '스위스워터': '스위스워터',
    '슈가케인 디카페인': '슈가케인 디카페인', '폴리쉬드': '폴리시드',
  };
  process = process.replace(/,\s*/g, ', ');
  process = process.replace(/애너러빅/g, '에네로빅');
  const words = process.split(' ');
  for (const word of words) {
    if (wordMapping[word]) return wordMapping[word];
  }
  return process;
};

(async () => {
  const startTime = Date.now();
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://www.fscoffee.co.kr/cus_extend_cart/goods_list', { waitUntil: 'networkidle2' });
  await page.waitForSelector('td[data-label="상품명"]');

  const nameTds = await page.$$('td[data-label="상품명"]');
  const data = [];
  for (const nameTd of nameTds) {
    try {
      const nameLinks = await nameTd.$$('span.goods_name a');
      if (!nameLinks || nameLinks.length === 0) continue;
      const nameLink = nameLinks[0];
      let coffeeNameRaw = await page.evaluate(el => el.textContent.trim(), nameLink);
      if (!coffeeNameRaw) continue;
      // 커피 이름 정리 (괄호 제거)
      const coffeeNameCleaned = cleanCoffeeName(coffeeNameRaw);
      // 국가명: 첫 번째 단어
      const country = coffeeNameCleaned.split(' ')[0] || '';
      // 가공방식: 마지막 단어 (예외: 디카페인)
      const words = coffeeNameCleaned.split(' ');
      let process = '';
      if (words.length >= 2 && words[words.length - 1] === '디카페인') {
        process = words[words.length - 2] + ' 디카페인';
      } else {
        process = words[words.length - 1] || '';
      }
      // 딕셔너리 직접 체크
      const wordMapping = {
        '내추럴': '내추럴', '워시드': '워시드', '허니': '허니', '에네로빅': '에네로빅',
        '풀리': '풀리', '세미': '세미', '블랙': '블랙', '옐로우': '옐로우', '레드': '레드',
        '라이트': '라이트', '더블': '더블', '웻': '웻', '드라이': '드라이', '펄프드': '펄프드',
        '퍼먼테이션': '퍼먼테이션', '카보닉': '카보닉', '마세레이션': '마세레이션', '폴리시': '폴리시',
        '디카페인': '디카페인', '슈가케인': '슈가케인', '스위스워터': '스위스워터',
        '슈가케인 디카페인': '슈가케인 디카페인', '폴리쉬드': '폴리시드',
      };
      let processKr = '';
      if (process in wordMapping) {
        processKr = wordMapping[process];
      } else {
        processKr = '';
      }
      // 제품 URL 추출 및 완성
      let productLink = await page.evaluate(el => el.getAttribute('href'), nameLink);
      if (productLink && productLink.startsWith('/')) {
        productLink = 'http://www.fscoffee.co.kr' + productLink;
      }
      // 해당 tr의 부모 요소 찾기
      const trElement = await nameTd.evaluateHandle(el => el.parentElement);
      // 1kg 단가 추출 (같은 tr 내에서)
      const priceTds = await trElement.$$('td[data-label="단가(1kg)"]');
      let price1kg = '';
      if (priceTds && priceTds.length > 0) {
        let priceText = await page.evaluate(el => el.textContent.trim(), priceTds[0]);
        price1kg = priceText.replace(/,|원/g, '').trim();
      }
      // 수입사명
      const importer = '후성커피';
      data.push({
        '국가': country,
        '커피 이름': coffeeNameCleaned,
        '가공방식': processKr,
        '1kg 단가': price1kg,
        '수입사명': importer,
        '제품 링크': productLink
      });
    } catch (e) {
      continue;
    }
  }
  await browser.close();
  console.log('수집된 데이터 개수:', data.length);
  const endTime = Date.now();
  const elapsedSec = ((endTime - startTime) / 1000).toFixed(2);
  console.log('수집 소요 시간:', elapsedSec + '초');
  if (data.length > 0) {
    const nowStr = new Date().toLocaleString('ko-KR', { hour12: false });
    const ws = xlsx.utils.json_to_sheet([{ '크롤링 일시': nowStr }]);
    xlsx.utils.sheet_add_json(ws, data, { origin: -1 });
    const wb = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(wb, ws, '후성커피');
    xlsx.writeFile(wb, '후성_원두.xlsx');
    console.log('엑셀 파일 저장 완료: 후성_원두.xlsx');
  } else {
    console.log('수집된 데이터가 없습니다.');
  }
})(); 