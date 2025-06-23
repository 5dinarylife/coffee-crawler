// 리브레 크롤러 (Puppeteer 기반)
// 기존 리브레_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

const puppeteer = require('puppeteer');
const xlsx = require('xlsx');

// 가공방식 한글/영문 매핑
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
  return '워시드';
};

// 커피 이름에서 가공방식 추출
function extractProcessingMethod(coffeeName) {
  const processingMethods = {
    '내추럴': '내추럴', '워시드': '워시드', '허니': '허니', '에네로빅': '에네로빅',
    '풀리': '풀리', '세미': '세미', '블랙': '블랙', '옐로우': '옐로우', '레드': '레드',
    '라이트': '라이트', '더블': '더블', '웻': '웻', '드라이': '드라이', '펄프드': '펄프드',
    '퍼먼테이션': '퍼먼테이션', '카보닉': '카보닉', '마세레이션': '마세레이션', '폴리시': '폴리시',
    '디카페인': '디카페인', '슈가케인': '슈가케인', '스위스워터': '스위스워터'
  };
  const twoWordMethods = {
    '무산소 내추럴': '무산소 내추럴', '레드 허니': '레드 허니', '무산소발효 내추럴': '무산소 내추럴',
    '블랙 허니': '블랙 허니', '옐로우 허니': '옐로우 허니', '레드 내추럴': '레드 내추럴',
    '블랙 내추럴': '블랙 내추럴', '옐로우 내추럴': '옐로우 내추럴', '카보닉 마세레이션': '카보닉 마세레이션',
    '웻 허니': '웻 허니', '드라이 허니': '드라이 허니', '세미 워시드': '세미 워시드',
    '풀리 워시드': '풀리 워시드', '더블 펄프드': '더블 펄프드', '라이트 로스팅': '라이트 로스팅',
    '다크 로스팅': '다크 로스팅', '미디엄 로스팅': '미디엄 로스팅'
  };
  const allMethods = { ...processingMethods, ...twoWordMethods };
  const words = coffeeName.split(' ');
  if (coffeeName.includes('(')) {
    const beforeParenthesis = coffeeName.split('(')[0].trim();
    const beforeWords = beforeParenthesis.split(' ');
    if (beforeWords.length >= 2) {
      const lastTwo = beforeWords.slice(-2).join(' ');
      if (twoWordMethods[lastTwo]) return twoWordMethods[lastTwo];
    }
    if (beforeWords.length) {
      const lastWord = beforeWords[beforeWords.length - 1];
      if (allMethods[lastWord]) return allMethods[lastWord];
    }
  }
  if (words.length >= 2) {
    const lastTwo = words.slice(-2).join(' ');
    if (twoWordMethods[lastTwo]) return twoWordMethods[lastTwo];
  }
  if (words.length) {
    const lastWord = words[words.length - 1];
    if (allMethods[lastWord]) return allMethods[lastWord];
  }
  if (words.length >= 2) {
    const secondLastWord = words[words.length - 2];
    if (allMethods[secondLastWord]) return allMethods[secondLastWord];
  }
  for (const method in allMethods) {
    if (coffeeName.includes(method)) return allMethods[method];
  }
  return '워시드';
}

// 커피 이름 정제
function cleanCoffeeName(name) {
  name = name.replace(/\[.*?\]/g, '');
  name = name.replace(/<br>/g, ' ');
  name = name.replace(/\([^)]*\)/g, '');
  name = name.replace(/&amp;/g, '&');
  name = name.replace(/\d+위/g, '');
  name = name.replace(/\s+/g, ' ');
  name = name.trim();
  const words = name.split(' ');
  if (words[0] === '디카페인') {
    const remainingWords = words.slice(1);
    if (remainingWords.length) name = remainingWords.join(' ') + ' 디카페인';
  }
  return name;
}

(async () => {
  const startTime = Date.now();
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://coffeelibre.kr/category/%EC%83%9D%EB%91%90%EC%86%8C%EB%B6%84/57/', { waitUntil: 'networkidle2' });
  await page.waitForSelector('li.item.xans-record-');

  const items = await page.$$('li.item.xans-record-');
  const data = [];
  for (const item of items) {
    try {
      const nameA = await item.$('p.name strong a');
      let coffeeNameRaw = '';
      if (nameA) coffeeNameRaw = await page.evaluate(el => el.innerHTML.trim(), nameA);
      if (!coffeeNameRaw) continue;
      const coffeeName = cleanCoffeeName(coffeeNameRaw);
      if (!coffeeName) continue;
      const country = coffeeName.split(' ')[0] || '';
      const processKr = extractProcessingMethod(coffeeName);
      // 1kg 단가
      let price1kg = '';
      try {
        const priceB = await item.$('li.price span.displaynonedisplaynone b');
        if (priceB) price1kg = await page.evaluate(el => el.textContent.trim().replace(/,/g, ''), priceB);
      } catch (e) { continue; }
      if (!price1kg) continue;
      // 제품 URL
      let productLink = '';
      if (nameA) {
        productLink = await page.evaluate(el => el.getAttribute('href'), nameA);
        if (productLink && productLink.startsWith('/')) productLink = 'https://coffeelibre.kr' + productLink;
      }
      const importer = '커피리브레';
      data.push({
        '국가': country,
        '커피 이름': coffeeName,
        '가공방식': processKr,
        '1kg 단가': price1kg,
        '수입사명': importer,
        '제품 링크': productLink
      });
    } catch (e) { continue; }
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
    xlsx.utils.book_append_sheet(wb, ws, '커피리브레');
    xlsx.writeFile(wb, '리브레_원두.xlsx');
    console.log('엑셀 파일 저장 완료: 리브레_원두.xlsx');
  } else {
    console.log('수집된 데이터가 없습니다.');
  }
})(); 