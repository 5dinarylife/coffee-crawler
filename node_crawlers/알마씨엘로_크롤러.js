// 알마씨엘로 크롤러 (Puppeteer 기반)
// 기존 알마씨엘로_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

const puppeteer = require('puppeteer');
const xlsx = require('xlsx');

// 가공방식 영어→한글 변환 딕셔너리
const processToKorean = (process) => {
  const wordMapping = {
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
  };
  if (/디카페인\s*Co2/i.test(process)) return 'CO2';
  if (process.includes('훌링')) return '헐링';
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
  await page.goto('https://www.almacielo.com/content/content.php?cont=simpleorder', { waitUntil: 'networkidle2' });
  await page.waitForSelector('tr.search_item');

  const rows = await page.$$('tr.search_item');
  const data = [];
  for (const row of rows) {
    try {
      const tds = await row.$$('td');
      if (!tds || tds.length < 8) continue;
      // 품절 상품 제외 (수급정보에 '일시결품' 또는 '품절' 등 표시)
      const supplyInfo = await page.evaluate(el => el.textContent.trim(), tds[6]);
      if (supplyInfo.includes('품절') || supplyInfo.includes('일시결품')) continue;
      // 커피 이름 및 URL
      const nameElem = await row.$('td#prd_name a');
      let coffeeNameRaw = '', productUrl = '';
      if (nameElem) {
        coffeeNameRaw = await page.evaluate(el => el.textContent.trim(), nameElem);
        productUrl = await page.evaluate(el => el.getAttribute('href'), nameElem);
      }
      // 커피 이름 정제
      let coffeeName = coffeeNameRaw.replace(/^\s*\[.*?\]\s*/, '').replace(/\s*\*.*$/, '').trim();
      // 국가명
      const country = coffeeName.split(' ')[0] || '';
      // 1kg 단가
      let price1kg = await page.evaluate(el => el.textContent.trim(), tds[1]);
      price1kg = price1kg.replace(/,|원/g, '');
      price1kg = price1kg.replace(/[^0-9]/g, '');
      // 가공방식
      let processKr = await page.evaluate(el => el.textContent.trim(), tds[5]);
      processKr = processToKorean(processKr);
      // 수입사명
      const importer = '알마씨엘로';
      data.push({
        '국가': country,
        '커피 이름': coffeeName,
        '가공방식': processKr,
        '1kg 단가': price1kg,
        '수입사명': importer,
        '제품 링크': productUrl
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
    xlsx.utils.book_append_sheet(wb, ws, '알마씨엘로');
    xlsx.writeFile(wb, '알마씨엘로_원두.xlsx');
    console.log('엑셀 파일 저장 완료: 알마씨엘로_원두.xlsx');
  } else {
    console.log('수집된 데이터가 없습니다.');
  }
})(); 