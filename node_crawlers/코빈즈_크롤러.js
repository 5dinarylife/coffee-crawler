// 코빈즈 크롤러 (Puppeteer 기반)
// 기존 코빈즈_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

const puppeteer = require('puppeteer');
const xlsx = require('xlsx');

// 가공방식 영어→한글 변환 딕셔너리
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
  await page.goto('https://www.cobeans.com/content/content.php?cont=simple_order', { waitUntil: 'networkidle2' });
  await page.waitForSelector('ul.order_prd_list.simpleOrderProductList li.productLi');

  const items = await page.$$('ul.order_prd_list.simpleOrderProductList li.productLi');
  const data = [];
  for (const item of items) {
    try {
      // 커피 이름
      const nameA = await item.$('h4.name a');
      let coffeeNameRaw = '';
      if (nameA) coffeeNameRaw = await page.evaluate(el => el.textContent.trim(), nameA);
      if (!coffeeNameRaw) continue;
      // 앞의 두 자리 숫자 추출 및 커피 이름 재구성
      const match = coffeeNameRaw.match(/^(\d{2})\s+(.+)/);
      let country = '', coffeeName = '';
      if (match) {
        const number = match[1];
        const nameWithoutNumber = match[2];
        country = nameWithoutNumber.split(' ')[0] || '';
        coffeeName = `${nameWithoutNumber} ${number}`;
      } else {
        country = coffeeNameRaw.split(' ')[0] || '';
        coffeeName = coffeeNameRaw;
      }
      // 가공방식: p.info > 첫 번째 span
      const processSpan = await item.$('p.info span');
      let processText = '';
      if (processSpan) processText = await page.evaluate(el => el.textContent.trim(), processSpan);
      const processKr = processToKorean(processText);
      // 1kg 단가: p.prc > span
      const priceSpan = await item.$('p.prc span');
      let price1kg = '';
      if (priceSpan) price1kg = await page.evaluate(el => el.textContent.trim(), priceSpan);
      price1kg = price1kg.replace(/,/g, '');
      if (!price1kg) continue;
      // 제품 url: h4.name a의 href
      let productLink = '';
      if (nameA) productLink = await page.evaluate(el => el.getAttribute('href'), nameA);
      // 수입사명
      const importer = '코빈즈';
      data.push({
        '국가': country,
        '커피 이름': coffeeName,
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
    xlsx.utils.book_append_sheet(wb, ws, '코빈즈');
    xlsx.writeFile(wb, '코빈즈_원두.xlsx');
    console.log('엑셀 파일 저장 완료: 코빈즈_원두.xlsx');
  } else {
    console.log('수집된 데이터가 없습니다.');
  }
})(); 