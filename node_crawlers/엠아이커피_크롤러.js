// 엠아이커피 크롤러 (Puppeteer 기반)
// 기존 엠아이커피_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

const puppeteer = require('puppeteer');
const fs = require('fs');
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
  };
  return process.split(' ').map(word => wordMapping[word] || word).join(' ');
};

// 영어 국가명 → 한글 국가명 변환 딕셔너리
const EN_TO_KR_COUNTRY = {
  'BRAZIL': '브라질', 'MEXICO': '멕시코', 'COLOMBIA': '콜롬비아', 'ECUADOR': '에콰도르',
  'BOLIVIA': '볼리비아', 'PERU': '페루', 'COSTA RICA': '코스타리카', 'GUATEMALA': '과테말라',
  'PANAMA': '파나마', 'HONDURAS': '온두라스', 'EL SALVADOR': '엘살바도르', 'ETHIOPIA': '에티오피아',
  'KENYA': '케냐', 'TANZANIA': '탄자니아', 'YEMEN': '예멘', 'INDONESIA': '인도네시아',
  'P.N.G.': '파푸아뉴기니', 'INDIA': '인도', 'THAILAND': '태국',
};

// 커피 이름/국가명 추출 함수 (Python extract_country_and_name_from_html 참고)
function extractCountryAndName(nameHtml, nameText) {
  let coffeeNameBase = '';
  if (nameHtml.includes('<br')) {
    // <br> 앞뒤 텍스트 모두 합쳐서 커피 이름으로 사용 (HTML 태그 제거)
    coffeeNameBase = nameHtml.split(/<br.*?>/).map(p => p.replace(/<.*?>/g, '').trim()).filter(Boolean).join(' ');
  } else {
    coffeeNameBase = nameText.trim();
  }
  // 국가명 추출 및 커피 이름 앞 국가명 중복 방지/추가
  const bracketMatch = coffeeNameBase.match(/^\s*\[(.*?)\]/);
  if (bracketMatch) {
    const bracketContent = bracketMatch[1].trim();
    const afterBracket = coffeeNameBase.slice(bracketMatch[0].length).trim();
    let foundKrCountry = null;
    for (const [en, kr] of Object.entries(EN_TO_KR_COUNTRY)) {
      if (bracketContent.toUpperCase().includes(en)) {
        foundKrCountry = kr;
        break;
      }
    }
    const afterWords = afterBracket.split(' ');
    let country, coffeeName;
    if (foundKrCountry) {
      country = foundKrCountry;
      if (afterWords.length && afterWords[0] === foundKrCountry) {
        coffeeName = afterBracket;
      } else {
        coffeeName = foundKrCountry + ' ' + afterBracket;
      }
    } else {
      country = afterWords[0] || '';
      coffeeName = afterBracket;
    }
    return { country, coffeeName };
  } else {
    const words = coffeeNameBase.split(' ');
    return { country: words[0] || '', coffeeName: coffeeNameBase };
  }
}

(async () => {
  const startTime = Date.now();
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://micoffee.co.kr/goods/unit_cart.php', { waitUntil: 'networkidle2' });

  // 테이블 row 대기
  await page.waitForSelector('table tbody tr');
  const rows = await page.$$('table tbody tr');
  const data = [];

  for (const row of rows) {
    // 헤더 row(즉, <th>가 포함된 row)는 건너뜀
    const ths = await row.$$('th');
    if (ths.length > 0) continue;
    try {
      const nameA = await row.$('td.name a');
      if (!nameA) continue;
      const nameHtml = await page.evaluate(el => el.innerHTML, nameA);
      const nameText = await page.evaluate(el => el.textContent, nameA);
      const { country, coffeeName } = extractCountryAndName(nameHtml, nameText);

      // 가공방식 (두 번째 또는 세 번째 p_i_view)
      const processTds = await row.$$('td.p_i_view');
      let processEn = '';
      if (processTds.length >= 2) {
        processEn = await page.evaluate(el => el.textContent.trim(), processTds[1]);
      }
      const processKr = processToKorean(processEn);

      // 1kg 단가: 반드시 10번째(td 인덱스 9) td의 텍스트만 사용
      const tds = await row.$$('td');
      let price1kg = '';
      if (tds.length > 9) {
        let priceText = await page.evaluate(el => el.textContent, tds[9]);
        priceText = priceText.split('\n')[0].trim();
        price1kg = priceText.replace(/[^\d,]/g, '');
      }
      if (!price1kg) continue;

      // 제품 URL: javascript:openGoodsView(숫자)에서 숫자만 추출
      const href = await page.evaluate(el => el.getAttribute('href'), nameA);
      let productLink = '';
      if (href) {
        const productIdMatch = href.match(/openGoodsView\((\d+)\)/);
        if (productIdMatch) {
          const productId = productIdMatch[1];
          productLink = `https://micoffee.co.kr/goods/goods_view.php?goodsNo=${productId}`;
        }
      }

      // 수입사명
      const importer = '엠아이커피';

      data.push({
        '국가': country,
        '커피 이름': coffeeName,
        '가공방식': processKr,
        '1kg 단가': price1kg,
        '수입사명': importer,
        '제품 링크': productLink
      });
    } catch (e) {
      console.error('에러:', e);
      continue;
    }
  }

  console.log('수집된 데이터 개수:', data.length);
  await browser.close();
  const endTime = Date.now();
  const elapsedSec = ((endTime - startTime) / 1000).toFixed(2);
  console.log('수집 소요 시간:', elapsedSec + '초');

  // 엑셀 저장
  const nowStr = new Date().toLocaleString('ko-KR', { hour12: false });
  const ws = xlsx.utils.json_to_sheet([{ '크롤링 일시': nowStr }]);
  xlsx.utils.sheet_add_json(ws, data, { origin: -1 });
  const wb = xlsx.utils.book_new();
  xlsx.utils.book_append_sheet(wb, ws, '엠아이커피');
  xlsx.writeFile(wb, '엠아이커피_원두.xlsx');
})(); 