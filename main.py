from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import threading
import time
import os
import json
from datetime import datetime
import tempfile
import zipfile
import io
import pandas as pd

app = Flask(__name__)

# 크롤러 정보 정의
CRAWLERS = {
    'GSC': {'script': 'gsc_crawler.py', 'filename': 'gsc_greenbean.xlsx', 'display_name': 'GSC'},
    '맥널티': {'script': '맥널티_크롤러.py', 'filename': '맥널티_원두.xlsx', 'display_name': '맥널티'},
    '블레스빈': {'script': '블레스빈_크롤러.py', 'filename': '블레스빈_원두.xlsx', 'display_name': '블레스빈'},
    '엠아이커피': {'script': '엠아이커피_크롤러.py', 'filename': '엠아이커피_원두.xlsx', 'display_name': '엠아이커피'},
    '코빈즈': {'script': '코빈즈_크롤러.py', 'filename': '코빈즈_원두.xlsx', 'display_name': '코빈즈'},
    '알마씨엘로': {'script': '알마씨엘로_크롤러.py', 'filename': '알마씨엘로_원두.xlsx', 'display_name': '알마씨엘로'},
    '리브레': {'script': '리브레_크롤러.py', 'filename': '리브레_원두.xlsx', 'display_name': '리브레'},
    '후성': {'script': '후성_크롤러.py', 'filename': '후성_원두.xlsx', 'display_name': '후성'},
    '모모스': {'script': '모모스_크롤러.py', 'filename': '모모스_원두.xlsx', 'display_name': '모모스'}
}

# 전역 변수로 크롤링 상태 관리
crawling_status = {
    'is_running': False,
    'start_time': None,
    'end_time': None,
    'logs': [],
    'progress': 0,
    'total_crawlers': len(CRAWLERS),
    'completed_crawlers': 0,
    'individual_status': {}
}

# 개별 크롤러 상태 초기화
for crawler_name in CRAWLERS.keys():
    crawling_status['individual_status'][crawler_name] = {
        'status': 'idle',  # idle, running, completed, failed
        'start_time': None,
        'end_time': None,
        'duration': None,
        'data_count': 0,
        'logs': [],
        'error': None
    }

def log_message(message, crawler_name=None, level=None):
    """
    로그 메시지를 추가하고 타임스탬프를 포함합니다. level: 'info', 'error', 'warning' 등
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    if level == 'error':
        log_entry = f"[ERROR] {log_entry}"
    elif level == 'warning':
        log_entry = f"[WARN] {log_entry}"
    # 개별 크롤러 로그
    if crawler_name:
        if crawler_name in crawling_status['individual_status']:
            crawling_status['individual_status'][crawler_name]['logs'].append(log_entry)
    else:
        crawling_status['logs'].append(log_entry)
    print(log_entry)

def get_data_count(filename):
    """엑셀 파일의 데이터 행 수를 반환합니다."""
    try:
        if os.path.exists(filename):
            df = pd.read_excel(filename, skiprows=1)
            return len(df)
        return 0
    except Exception as e:
        print(f"데이터 수 계산 오류 ({filename}): {e}")
        return 0

def run_single_crawler(crawler_name):
    """단일 크롤러를 실행하는 함수"""
    global crawling_status
    
    if crawler_name not in CRAWLERS:
        log_message(f"알 수 없는 크롤러: {crawler_name}", crawler_name, level='error')
        return
    
    # 상태 초기화
    status = crawling_status['individual_status'][crawler_name]
    status['status'] = 'running'
    status['start_time'] = datetime.now().isoformat()
    status['end_time'] = None
    status['duration'] = None
    status['data_count'] = 0
    status['logs'] = []
    status['error'] = None
    
    script_name = CRAWLERS[crawler_name]['script']
    filename = CRAWLERS[crawler_name]['filename']
    
    log_message(f"'{crawler_name}' 버튼이 눌렸다.", crawler_name)
    log_message(f"--- {crawler_name} 크롤러 시작 ---", crawler_name)
    
    try:
        start_time = time.time()
        
        # 크롤러 스크립트 실행
        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=1800  # 30분 타임아웃
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            # 성공
            status['status'] = 'completed'
            status['duration'] = round(duration, 2)
            status['data_count'] = get_data_count(filename)
            
            log_message(f"✅ {crawler_name} 크롤링 완료! (소요시간: {duration:.2f}초, 데이터: {status['data_count']}개)", crawler_name)
            
            if result.stdout:
                log_message(f"출력: {result.stdout}", crawler_name)
        else:
            # 실패
            status['status'] = 'failed'
            status['duration'] = round(duration, 2)
            status['error'] = result.stderr
            
            log_message(f"❌ {crawler_name} 크롤링 실패(코드: {result.returncode})", crawler_name, level='error')
            log_message(f"오류: {result.stderr}", crawler_name, level='error')
            # 전체 실행 로그에도 Traceback 남기기
            log_message(f"[{crawler_name}] Traceback:\n{result.stderr}", None, level='error')
            
    except subprocess.TimeoutExpired:
        status['status'] = 'failed'
        status['error'] = '시간 초과 (30분)'
        log_message(f"⏰ {crawler_name} 크롤링 시간 초과", crawler_name, level='error')
    except Exception as e:
        status['status'] = 'failed'
        status['error'] = str(e)
        log_message(f"❌ {crawler_name} 크롤링 중 예외 발생: {str(e)}", crawler_name, level='error')
    finally:
        status['end_time'] = datetime.now().isoformat()
        if status['status'] == 'failed':
            log_message(f"'{crawler_name}' 크롤링 실패({status['error']})", crawler_name, level='error')

def run_all_crawlers():
    """모든 크롤러를 순차적으로 실행하는 함수"""
    global crawling_status
    
    try:
        crawling_status['is_running'] = True
        crawling_status['start_time'] = datetime.now().isoformat()
        crawling_status['logs'] = []
        crawling_status['progress'] = 0
        crawling_status['completed_crawlers'] = 0
        
        log_message("전체 크롤링 버튼이 눌렸다.")
        log_message("🚀 전체 크롤링 작업을 시작합니다...")
        
        total_crawlers = len(CRAWLERS)
        completed = 0
        
        for crawler_name in CRAWLERS.keys():
            if not crawling_status['is_running']:  # 중단 체크
                break
                
            run_single_crawler(crawler_name)
            completed += 1
            crawling_status['completed_crawlers'] = completed
            crawling_status['progress'] = int((completed / total_crawlers) * 100)
            
            # 크롤러 간 딜레이
            time.sleep(2)
        
        if crawling_status['is_running']:
            log_message("✅ 전체 크롤링 작업이 완료되었습니다!")
            crawling_status['progress'] = 100
            
    except Exception as e:
        log_message(f"❌ 전체 크롤링 작업 중 오류 발생: {str(e)}", level='error')
    finally:
        crawling_status['is_running'] = False
        crawling_status['end_time'] = datetime.now().isoformat()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', crawlers=CRAWLERS)

@app.route('/start', methods=['POST'])
def start_crawling():
    """전체 크롤링 작업 시작"""
    if crawling_status['is_running']:
        return jsonify({'status': 'error', 'message': '이미 크롤링이 실행 중입니다.'})
    
    # 별도 스레드에서 크롤링 실행
    thread = threading.Thread(target=run_all_crawlers)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'message': '전체 크롤링 작업이 시작되었습니다.'})

@app.route('/start_single/<crawler_name>', methods=['POST'])
def start_single_crawler(crawler_name):
    """개별 크롤러 실행"""
    if crawler_name not in CRAWLERS:
        return jsonify({'status': 'error', 'message': f'알 수 없는 크롤러: {crawler_name}'})
    
    status = crawling_status['individual_status'][crawler_name]
    if status['status'] == 'running':
        return jsonify({'status': 'error', 'message': f'{crawler_name} 크롤러가 이미 실행 중입니다.'})
    
    # 별도 스레드에서 개별 크롤러 실행
    thread = threading.Thread(target=run_single_crawler, args=(crawler_name,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'success', 'message': f'{crawler_name} 크롤러가 시작되었습니다.'})

@app.route('/stop', methods=['POST'])
def stop_crawling():
    """크롤링 작업 중단"""
    if not crawling_status['is_running']:
        return jsonify({'status': 'error', 'message': '실행 중인 크롤링이 없습니다.'})
    
    crawling_status['is_running'] = False
    log_message("🛑 크롤링 작업이 중단되었습니다.")
    
    return jsonify({'status': 'success', 'message': '크롤링 작업이 중단되었습니다.'})

@app.route('/status')
def get_status():
    """크롤링 상태 조회"""
    return jsonify(crawling_status)

@app.route('/download')
def download_results():
    """통합 크롤링 결과 파일 다운로드"""
    try:
        # 통합 엑셀 파일들 찾기
        excel_files = []
        for file in os.listdir('.'):
            if file.endswith('.xlsx') and '통합' in file:
                excel_files.append(file)
        
        if not excel_files:
            return jsonify({'status': 'error', 'message': '다운로드할 통합 파일이 없습니다.'})
        
        # 가장 최근 파일 선택
        latest_file = max(excel_files, key=os.path.getctime)
        
        return send_file(
            latest_file,
            as_attachment=True,
            download_name=latest_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'파일 다운로드 중 오류: {str(e)}'})

@app.route('/download_single/<crawler_name>')
def download_single_result(crawler_name):
    """개별 크롤러 결과 파일 다운로드"""
    try:
        if crawler_name not in CRAWLERS:
            return jsonify({'status': 'error', 'message': f'알 수 없는 크롤러: {crawler_name}'})
        
        filename = CRAWLERS[crawler_name]['filename']
        
        if not os.path.exists(filename):
            return jsonify({'status': 'error', 'message': f'{crawler_name}의 결과 파일이 없습니다.'})
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'파일 다운로드 중 오류: {str(e)}'})

@app.route('/download-all')
def download_all_files():
    """모든 엑셀 파일을 ZIP으로 다운로드"""
    try:
        # 엑셀 파일들 찾기
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
        if not excel_files:
            return jsonify({'status': 'error', 'message': '다운로드할 파일이 없습니다.'})
        
        # ZIP 파일 생성
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in excel_files:
                zf.write(file, file)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f'coffee_crawler_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'파일 다운로드 중 오류: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False) 