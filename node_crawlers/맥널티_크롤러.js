// 맥널티 크롤러 (Puppeteer 기반)
// 기존 맥널티_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

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
    'INFUSED': '인퓨즈드', 'Infused': '인퓨즈드', 'infused': '인퓨즈드',
    'M/W': '마운틴워터 프로세스', 'm/w': '마운틴워터 프로세스', 'MOUNTAINWATER': '마운틴워터 프로세스',
    'WET-POLISH': '웻 폴리시', 'Wet-Polish': '웻 폴리시', 'wet-polish': '웻 폴리시',
  };
  let words = [];
  for (const w of process.split(' ')) {
    if (w.includes('-')) words = words.concat(w.split('-'));
    else words.push(w);
  }
  return words.map(word => wordMapping[word] || word).join(' ');
};

(async () => {
  const startTime = Date.now();
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://www.mcffee.co.kr/goods/goods_list.php?cateCd=001', { waitUntil: 'networkidle2' });
  await page.waitForSelector('ul.prdList.grid3 li');

  // 페이지네이션에서 마지막 페이지 번호 추출
  let lastPage = 1;
  try {
    let paging = await page.$('div.xans-product-paging') || await page.$('div.ec-base-paginate');
    if (paging) {
      const pageLinks = await paging.$$('a');
      for (const link of pageLinks) {
        const num = parseInt(await page.evaluate(el => el.textContent.trim(), link));
        if (!isNaN(num) && num > lastPage) lastPage = num;
      }
    }
  } catch (e) {
    // 페이지네이션 파싱 실패 시 1페이지만
  }

  const data = [];
  for (let pageNum = 1; pageNum <= lastPage; pageNum++) {
    const pageUrl = `https://greenbeans.co.kr/product/list.html?cate_no=128&page=${pageNum}`;
    await page.goto(pageUrl, { waitUntil: 'networkidle2' });
    await page.waitForSelector('ul.prdList.grid3 li');
    const items = await page.$$('ul.prdList.grid3 li');
    for (const item of items) {
      try {
        // 품절 상품 예외처리
        const soldoutImgs = await item.$$('img[alt="품절"]');
        if (soldoutImgs.length > 0) continue;
        // 커피 이름
        const nameEl = await item.$('div.description strong.name a');
        if (!nameEl) continue;
        let rawName = await page.evaluate(el => el.textContent.trim(), nameEl);
        // [ ... ] 제거
        let nameNoBracket = rawName.replace(/\[.*?\]/g, '').trim();
        // '_1kg/5kg/20kg' 등 단위 표기 제거
        let nameNoUnit = nameNoBracket.replace(/_\d+kg\/\d+kg\/\d+kg$/, '').trim();
        // ( ... ) 추출 (가공방식)
        const processMatch = nameNoUnit.match(/\((.*?)\)/);
        let processKr = '';
        let coffeeNameBase = nameNoUnit;
        if (processMatch) {
          const processEn = processMatch[1].trim();
          processKr = processToKorean(processEn);
          coffeeNameBase = nameNoUnit.replace(/\(.*?\)/, '').trim();
        } else {
          const words = coffeeNameBase.split(' ');
          if (words.length && /^[A-Za-z/-]+$/.test(words[words.length - 1])) {
            const processEn = words[words.length - 1];
            processKr = processToKorean(processEn);
            coffeeNameBase = words.slice(0, -1).join(' ');
          } else {
            if (words.length) {
              const lastWord = words[words.length - 1];
              const processKrValues = new Set([
                '내추럴', '워시드', '허니', '에네로빅', '아나에어로빅', '풀리', '세미', '블랙', '옐로우', '레드', '라이트', '더블', '웻', '드라이', '펄프드', '퍼먼테이션', '카보닉', '마세레이션', '폴리시', '디카페인', '슈가케인', '스위스워터', '인퓨즈드', '마운틴워터 프로세스', '웻 폴리시', '레드허니', '블랙허니', '옐로우허니', '화이트허니', '골드허니', '그레이허니', '핑크허니', '오렌지허니', '퍼플허니', '그린허니', '허니프로세스'
              ]);
              if (processKrValues.has(lastWord)) {
                processKr = lastWord;
              }
            }
          }
        }
        // 커피 이름 완성
        const coffeeName = processKr && !coffeeNameBase.includes(processKr)
          ? `${coffeeNameBase} ${processKr}`.trim()
          : coffeeNameBase;
        // 국가명: 커피 이름의 첫 단어
        const country = coffeeNameBase.split(' ')[0] || '';
        // 1kg 단가
        let price1kg = '';
        try {
          const priceEl = await item.$('div.description ul.xans-product-listitem li span[style*="font-size:18px"]');
          if (priceEl) price1kg = await page.evaluate(el => el.textContent.replace(/[^\d]/g, ''), priceEl);
        } catch (e) {}
        if (!price1kg) {
          try {
            const priceLis = await item.$$('div.description ul.xans-product-listitem li');
            for (const li of priceLis) {
              const spans = await li.$$('span');
              for (const span of spans) {
                const text = await page.evaluate(el => el.textContent, span);
                if (text.includes('원')) {
                  price1kg = text.replace(/[^\d]/g, '');
                  break;
                }
              }
              if (price1kg) break;
            }
          } catch (e) {}
        }
        // 제품 링크
        let productLink = await page.evaluate(el => el.getAttribute('href'), nameEl);
        if (productLink && productLink.startsWith('/')) productLink = 'https://greenbeans.co.kr' + productLink;
        const importer = '맥널티';
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
    xlsx.utils.book_append_sheet(wb, ws, '맥널티');
    xlsx.writeFile(wb, '맥널티_원두.xlsx');
    console.log('엑셀 파일 저장 완료: 맥널티_원두.xlsx');
  } else {
    console.log('수집된 데이터가 없습니다.');
  }
})(); 