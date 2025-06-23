// 모모스 크롤러 (Puppeteer 기반)
// 기존 모모스_크롤러.py의 데이터 추출 규칙/HTML 구조를 그대로 반영

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

// 커피 이름 정제 함수
function cleanCoffeeName(name) {
  name = name.replace(/^\[생두\]\s*/, '');
  // 영문을 한글 음으로 변환하는 매핑
  const englishToKorean = {
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
    'La': '라', 'Guadua': '과두아', 'CVM': 'CVM',
    'Hacienda': '하시엔다', 'hacienda': '하시엔다',
    'Luciana': '루시아나', 'Estrella': '에스트렐라', 'Paraiso': '파라이소',
    'Quebrada': '케브라다', 'Grande': '그란데', 'Kenia': '케니아',
    'Wessi': '웨시', 'Tima': '티마', 'Kangocho': '캉고초',
    'Ziwa': '지와', 'Alo': '알로', 'Coffee': '커피',
    'Mosto': '모스토', 'Yirgacheffe': '예가체프', 'Idido': '이디도',
    'Edido': '에디도', 'Banko': '반코', 'Chelchele': '첼첼레',
    'Bookkisa': '부키사', 'Pink': '핑크', 'White': '화이트'
  };
  name = name.replace(/^\[([^\]]+)\]\s*/, '$1 ');
  name = name.replace(/\[[^\]]*\]/g, '');
  name = name.replace(/\s+/g, ' ').trim();
  for (const [english, korean] of Object.entries(englishToKorean)) {
    const regex = new RegExp(`\\b${english}\\b`, 'gi');
    name = name.replace(regex, korean);
  }
  return name;
}

// 국가명 추출
function extractCountry(name) {
  const words = name.split(' ');
  return words[0] || '';
}

// 페이지 이동 함수
async function goToPage(page, pageNum) {
  const pageUrl = `https://momos.co.kr/custom/sub/product_category/green_bean_all_shop.html?cate_no=64&page=${pageNum}`;
  await page.goto(pageUrl, { waitUntil: 'networkidle2' });
  await page.waitForSelector('li.xans-record-');
  await new Promise(r => setTimeout(r, 3000));
}

(async () => {
  const startTime = Date.now();
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://momos.co.kr/custom/sub/product_category/green_bean_all_shop.html?cate_no=64', { waitUntil: 'networkidle2' });
  await page.waitForSelector('li.xans-record-');
  await new Promise(r => setTimeout(r, 3000));

  // 총 페이지 수 추출
  let totalPages = 1;
  try {
    const lastPageHref = await page.$eval('a.last', el => el.getAttribute('href'));
    const match = lastPageHref && lastPageHref.match(/page=(\d+)/);
    if (match) {
      totalPages = parseInt(match[1], 10);
    } else {
      // 백업: 페이지네이션 숫자 중 최대값
      const pageNums = await page.$$eval('.ec-base-paginate ol li a', els => els.map(e => parseInt(e.textContent.trim(), 10)).filter(Number.isInteger));
      if (pageNums.length > 0) totalPages = Math.max(...pageNums);
    }
  } catch (e) {
    // 페이지네이션이 없으면 1페이지
  }
  console.log('총 페이지 수:', totalPages);

  const data = [];
  let pageNum = 1;
  let stop = false;

  while (pageNum <= totalPages && !stop) {
    console.log(`페이지 ${pageNum}/${totalPages} 크롤링 중...`);
    await goToPage(page, pageNum);
    const items = await page.$$('ul.prdList.prdList01.grid4 li.xans-record-');
    let pageSoldoutCount = 0;
    let pageValidCount = 0;
    for (const item of items) {
      try {
        // 품절 상품 체크
        const soldoutSpan = await item.$('div.thumbnail div.prdImg a span.soldout');
        if (soldoutSpan) {
          const soldoutClasses = await page.evaluate(el => el.getAttribute('class'), soldoutSpan);
          if (soldoutClasses && !soldoutClasses.includes('displaynone')) {
            pageSoldoutCount++;
            continue;
          }
        }
        // 커피 이름
        let coffeeNameRaw = '';
        const nameSpan = await item.$('div.description div.name a span');
        if (nameSpan) {
          coffeeNameRaw = await page.evaluate(el => el.textContent.trim(), nameSpan);
        } else {
          const nameA = await item.$('div.description div.name a');
          if (nameA) coffeeNameRaw = await page.evaluate(el => el.textContent.trim(), nameA);
        }
        if (!coffeeNameRaw) continue;
        const coffeeNameCleaned = cleanCoffeeName(coffeeNameRaw);
        const country = extractCountry(coffeeNameCleaned);
        // 가격
        const priceSpan = await item.$('li[data-title="판매가"] span');
        let price1kg = '';
        if (priceSpan) {
          let priceText = await page.evaluate(el => el.textContent.trim(), priceSpan);
          price1kg = priceText.replace(/,|원/g, '');
        }
        if (!price1kg) continue;
        // 제품 링크
        const linkA = await item.$('div.description div.name a');
        let productLink = '';
        if (linkA) {
          productLink = await page.evaluate(el => el.getAttribute('href'), linkA);
          if (productLink && !productLink.startsWith('http')) productLink = 'https://momos.co.kr' + productLink;
        }
        // 가공방식 추출
        const processKeywords = ['워시드', '내추럴', '허니', '에네로빅', '카보닉', '마세레이션'];
        let processKr = '';
        for (const keyword of processKeywords) {
          if (coffeeNameCleaned.includes(keyword)) {
            processKr = keyword;
            break;
          }
        }
        // 수입사명
        const importer = '모모스';
        // (추가) 커피 이름 현지 발음 변환은 생략(복잡한 규칙, 필요시 추가)
        data.push({
          '국가': country,
          '커피 이름': coffeeNameCleaned,
          '가공방식': processKr,
          '1kg 단가': price1kg,
          '수입사명': importer,
          '제품 링크': productLink
        });
        pageValidCount++;
      } catch (e) {
        continue;
      }
    }
    console.log(`  - 페이지 ${pageNum} 결과: 정상상품 ${pageValidCount}개, 품절상품 ${pageSoldoutCount}개`);
    if (pageSoldoutCount > 0) {
      console.log('  - 품절 상품이 발견됨. 크롤링 중단.');
      break;
    }
    pageNum++;
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
    xlsx.utils.book_append_sheet(wb, ws, '모모스');
    xlsx.writeFile(wb, '모모스_원두.xlsx');
    console.log('엑셀 파일 저장 완료: 모모스_원두.xlsx');
  } else {
    console.log('수집된 데이터가 없습니다.');
  }
})(); 