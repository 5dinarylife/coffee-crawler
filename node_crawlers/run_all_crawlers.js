// 모든 커피 크롤러를 순차적으로 실행하는 통합 스크립트
// 각 크롤러 실행 결과/에러를 로그로 출력

import { exec } from 'child_process';

const crawlers = [
  '엠아이커피_크롤러.js',
  '모모스_크롤러.js',
  '블레스빈_크롤러.js',
  '알마씨엘로_크롤러.js',
  '코빈즈_크롤러.js',
  '후성_크롤러.js',
];

function runCrawler(filename) {
  return new Promise((resolve) => {
    console.log(`\n▶️ [실행] ${filename}`);
    exec(`node ${filename}`, { cwd: __dirname }, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ [실패] ${filename}\n${stderr}`);
        resolve(false);
      } else {
        console.log(`✅ [성공] ${filename}\n${stdout}`);
        resolve(true);
      }
    });
  });
}

(async () => {
  for (const crawler of crawlers) {
    await runCrawler(crawler);
  }
  console.log('\n모든 크롤러 실행 완료!');
})(); 