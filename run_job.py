import subprocess
import sys
import os
import pandas as pd
from datetime import datetime
import time

# 크롤러 정보
CRAWLERS = {
    'GSC': {'script': 'gsc_crawler.py', 'filename': 'gsc_greenbean.xlsx'},
    '맥널티': {'script': '맥널티_크롤러.py', 'filename': '맥널티_원두.xlsx'},
    '블레스빈': {'script': '블레스빈_크롤러.py', 'filename': '블레스빈_원두.xlsx'},
    '엠아이커피': {'script': '엠아이커피_크롤러.py', 'filename': '엠아이커피_원두.xlsx'},
    '코빈즈': {'script': '코빈즈_크롤러.py', 'filename': '코빈즈_원두.xlsx'},
    '알마씨엘로': {'script': '알마씨엘로_크롤러.py', 'filename': '알마씨엘로_원두.xlsx'},
    '리브레': {'script': '리브레_크롤러.py', 'filename': '리브레_원두.xlsx'},
    '후성': {'script': '후성_크롤러.py', 'filename': '후성_원두.xlsx'},
    '모모스': {'script': '모모스_크롤러.py', 'filename': '모모스_원두.xlsx'}
}

def log_message(message):
    """콘솔에 로그 메시지를 출력합니다."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_single_crawler(crawler_name):
    """단일 크롤러를 실행하고 성공 여부를 반환합니다."""
    try:
        script_name = CRAWLERS[crawler_name]['script']
        log_message(f"--- Executing: {crawler_name} ({script_name}) ---")
        
        # 크롤러 스크립트를 파이썬으로 직접 실행
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=1800  # 30분 타임아웃
        )

        if result.returncode == 0:
            log_message(f"✅ Success: {crawler_name} finished.")
            print(result.stdout) # 크롤러 스크립트의 print문 출력
            return True
        else:
            log_message(f"❌ ERROR: {crawler_name} failed with return code {result.returncode}.")
            print("--- stdout ---")
            print(result.stdout)
            print("--- stderr ---")
            print(result.stderr)
            return False
            
    except Exception as e:
        log_message(f"❌ EXCEPTION during {crawler_name} execution: {e}")
        return False

def merge_excel_files():
    """모든 크롤러의 결과 엑셀 파일을 하나로 통합합니다."""
    log_message("--- Merging all excel files... ---")
    all_data = []
    
    for name, info in CRAWLERS.items():
        filename = info['filename']
        if os.path.exists(filename):
            try:
                df = pd.read_excel(filename, skiprows=1)
                all_data.append(df)
                log_message(f"-> Merged: {filename} ({len(df)} rows)")
            except Exception as e:
                log_message(f"-> Failed to read {filename}: {e}")
                continue
    
    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"통합_생두_데이터_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            now_str = datetime.now().strftime("통합 크롤링 일시: %Y-%m-%d %H:%M:%S")
            pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
            merged_df.to_excel(writer, index=False, startrow=1)
        
        log_message(f"✅ Successfully created 통합 엑셀 파일: {output_filename} ({len(merged_df)} total rows)")
        return output_filename
    else:
        log_message("❌ No data to merge.")
        return None

def main_job():
    """전체 크롤링 작업을 실행하는 메인 함수"""
    log_message("🚀 Starting Daily Green Bean Crawler Job")
    start_time = time.time()
    
    successful_crawlers = 0
    total_crawlers = len(CRAWLERS)
    
    for name in CRAWLERS.keys():
        if run_single_crawler(name):
            successful_crawlers += 1
        # 서버에 부담을 주지 않도록 크롤러 사이에 약간의 딜레이를 둡니다.
        time.sleep(5)
        
    log_message(f"--- Job Summary: {successful_crawlers} out of {total_crawlers} crawlers succeeded. ---")
    
    if successful_crawlers > 0:
        merge_excel_files()
        # 여기에 나중에 통합 파일을 구글 드라이브나 다른 곳에 업로드하는 코드를 추가할 수 있습니다.
    
    end_time = time.time()
    elapsed = end_time - start_time
    log_message(f"🏁 Finished Daily Crawler Job in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main_job() 