import streamlit as st
import subprocess
import sys
import os
import pandas as pd
from datetime import datetime
import time
import threading
import traceback

# 페이지 설정
st.set_page_config(
    page_title="생두 크롤러 웹 시스템",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'crawler_running' not in st.session_state:
    st.session_state.crawler_running = False
if 'completed_crawlers' not in st.session_state:
    st.session_state.completed_crawlers = set()
if 'crawler_results' not in st.session_state:
    st.session_state.crawler_results = {}

# 크롤러 정보 (기존 크롤러_통제_프로그램.py에서 가져옴)
CRAWLERS = {
    'GSC': {'script': 'gsc_crawler.py', 'filename': 'gsc_greenbean.xlsx', 'status': '대기중'},
    '맥널티': {'script': '맥널티_크롤러.py', 'filename': '맥널티_원두.xlsx', 'status': '대기중'},
    '블레스빈': {'script': '블레스빈_크롤러.py', 'filename': '블레스빈_원두.xlsx', 'status': '대기중'},
    '엠아이커피': {'script': '엠아이커피_크롤러.py', 'filename': '엠아이커피_원두.xlsx', 'status': '대기중'},
    '코빈즈': {'script': '코빈즈_크롤러.py', 'filename': '코빈즈_원두.xlsx', 'status': '대기중'},
    '알마씨엘로': {'script': '알마씨엘로_크롤러.py', 'filename': '알마씨엘로_원두.xlsx', 'status': '대기중'},
    '소펙스': {'script': '소펙스_크롤러.py', 'filename': '소펙스_원두.xlsx', 'status': '대기중'},
    '리브레': {'script': '리브레_크롤러.py', 'filename': '리브레_원두.xlsx', 'status': '대기중'},
    '후성': {'script': '후성_크롤러.py', 'filename': '후성_원두.xlsx', 'status': '대기중'},
    '모모스': {'script': '모모스_크롤러.py', 'filename': '모모스_원두.xlsx', 'status': '대기중'}
}

def log_message(message):
    """로그 메시지 추가"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.write(f"[{timestamp}] {message}")

def run_crawler(crawler_name):
    """개별 크롤러 실행 (기존 로직 재사용)"""
    try:
        start_time = time.time()
        log_message(f"{crawler_name} 크롤링 시작...")
        
        # 크롤러 스크립트 실행
        script_name = CRAWLERS[crawler_name]['script']
        if os.path.exists(script_name):
            # 환경 변수 설정 (한글 파일명 지원)
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run([sys.executable, script_name], 
                                  capture_output=True, text=True, timeout=1800,  # 30분 타임아웃
                                  env=env, encoding='utf-8')
            
            if result.returncode == 0:
                # 결과 확인
                filename = CRAWLERS[crawler_name]['filename']
                if os.path.exists(filename):
                    try:
                        df = pd.read_excel(filename, skiprows=1)  # 첫 번째 행(크롤링 일시) 건너뛰기
                        data_count = len(df)
                    except Exception as e:
                        log_message(f"{crawler_name} 엑셀 파일 읽기 오류: {e}")
                        data_count = 0
                else:
                    data_count = 0
                
                end_time = time.time()
                elapsed = end_time - start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                time_text = f"{minutes}분 {seconds}초"
                
                log_message(f"{crawler_name} 크롤링 완료! (소요 시간: {time_text}, 수집된 데이터: {data_count}개)")
                
                # 결과 저장
                st.session_state.crawler_results[crawler_name] = {
                    'status': '성공',
                    'time': time_text,
                    'count': data_count,
                    'filename': filename
                }
                
                return True, data_count, time_text
            else:
                log_message(f"{crawler_name} 크롤링 실패: {result.stderr}")
                st.session_state.crawler_results[crawler_name] = {
                    'status': '실패',
                    'time': '',
                    'count': 0,
                    'filename': ''
                }
                return False, 0, ''
        else:
            log_message(f"{crawler_name} 스크립트 파일을 찾을 수 없습니다: {script_name}")
            return False, 0, ''
            
    except subprocess.TimeoutExpired:
        log_message(f"{crawler_name} 크롤링 타임아웃 (30분 초과)")
        return False, 0, ''
    except Exception as e:
        log_message(f"{crawler_name} 크롤링 오류: {str(e)}")
        return False, 0, ''

def merge_excel_files():
    """통합 엑셀 파일 생성 (기존 로직 재사용)"""
    try:
        all_data = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, info in CRAWLERS.items():
            filename = info['filename']
            if os.path.exists(filename):
                try:
                    df = pd.read_excel(filename, skiprows=1)
                    all_data.append(df)
                    log_message(f"{name} 데이터 추가됨 ({len(df)}개)")
                except Exception as e:
                    log_message(f"{name} 파일 읽기 실패: {e}")
                    continue
        
        if all_data:
            merged_df = pd.concat(all_data, ignore_index=True)
            output_filename = f"통합_생두_데이터_{timestamp}.xlsx"
            
            # 엑셀 첫 행에 날짜/시간 추가
            with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                now_str = datetime.now().strftime("크롤링 일시: %Y-%m-%d %H:%M:%S")
                pd.DataFrame([[now_str]]).to_excel(writer, index=False, header=False)
                merged_df.to_excel(writer, index=False, startrow=1)
            
            log_message(f"통합 엑셀 파일 생성 완료: {output_filename} ({len(merged_df)}개 데이터)")
            return output_filename
        else:
            log_message("통합할 데이터가 없습니다.")
            return None
    except Exception as e:
        log_message(f"통합 엑셀 파일 생성 실패: {e}")
        return None

def main():
    # 메인 타이틀
    st.title("☕ 생두 크롤러 웹 시스템")
    st.markdown("---")
    
    # 사이드바 설정
    st.sidebar.header("🎛️ 크롤러 제어")
    
    # 개별 크롤러 실행
    st.sidebar.subheader("📊 개별 크롤러 실행")
    selected_crawler = st.sidebar.selectbox(
        "크롤러 선택",
        list(CRAWLERS.keys())
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button(f"🚀 {selected_crawler} 실행", disabled=st.session_state.crawler_running):
            st.session_state.crawler_running = True
            
            # 진행 상황 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(f"{selected_crawler} 크롤링 중..."):
                success, count, time_text = run_crawler(selected_crawler)
                progress_bar.progress(100)
                
                if success:
                    st.success(f"✅ {selected_crawler} 크롤링 완료!")
                    st.session_state.completed_crawlers.add(selected_crawler)
                    
                    # 엑셀 파일 다운로드 버튼
                    filename = CRAWLERS[selected_crawler]['filename']
                    if os.path.exists(filename):
                        with open(filename, "rb") as file:
                            st.download_button(
                                label=f"📥 {selected_crawler} 엑셀 다운로드",
                                data=file.read(),
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                else:
                    st.error(f"❌ {selected_crawler} 크롤링 실패")
            
            st.session_state.crawler_running = False
    
    with col2:
        if st.button("🔄 새로고침", disabled=st.session_state.crawler_running):
            st.rerun()
    
    # 모든 크롤러 실행
    st.sidebar.subheader("🔥 일괄 실행")
    if st.sidebar.button("🚀 모든 크롤러 실행", disabled=st.session_state.crawler_running):
        st.session_state.crawler_running = True
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_crawlers = len(CRAWLERS)
        completed = 0
        successful_crawlers = 0
        
        for i, (name, info) in enumerate(CRAWLERS.items()):
            status_text.text(f"🔄 {name} 크롤링 중... ({i+1}/{total_crawlers})")
            
            success, count, time_text = run_crawler(name)
            completed += 1
            progress_bar.progress(completed / total_crawlers)
            
            if success:
                successful_crawlers += 1
                st.session_state.completed_crawlers.add(name)
            
            # 잠시 대기 (서버 부하 방지)
            time.sleep(1)
        
        status_text.text(f"✅ 모든 크롤링 완료! (성공: {successful_crawlers}/{total_crawlers})")
        st.session_state.crawler_running = False
        
        # 통합 엑셀 파일 생성 버튼 활성화
        if successful_crawlers > 0:
            st.sidebar.success("📊 통합 엑셀 파일 생성 가능")
    
    # 통합 엑셀 파일 생성
    if st.session_state.completed_crawlers:
        st.sidebar.subheader("📊 통합 파일")
        if st.sidebar.button("🔗 통합 엑셀 생성"):
            with st.spinner("통합 엑셀 파일 생성 중..."):
                merged_file = merge_excel_files()
                if merged_file and os.path.exists(merged_file):
                    with open(merged_file, "rb") as file:
                        st.sidebar.download_button(
                            label="📥 통합 엑셀 다운로드",
                            data=file.read(),
                            file_name=merged_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    
    # 메인 콘텐츠 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 크롤러 상태")
        
        # 크롤러 상태 테이블
        status_data = []
        for name, info in CRAWLERS.items():
            if name in st.session_state.crawler_results:
                result = st.session_state.crawler_results[name]
                status_data.append({
                    "크롤러": name,
                    "상태": result['status'],
                    "소요시간": result['time'],
                    "데이터수": result['count']
                })
            else:
                status_data.append({
                    "크롤러": name,
                    "상태": "대기중",
                    "소요시간": "",
                    "데이터수": 0
                })
        
        if status_data:
            df_status = pd.DataFrame(status_data)
            st.dataframe(df_status, use_container_width=True)
    
    with col2:
        st.subheader("📁 생성된 파일")
        
        # 엑셀 파일 목록
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
        if excel_files:
            for file in excel_files:
                if st.button(f"📥 {file}", key=f"download_{file}"):
                    with open(file, "rb") as f:
                        st.download_button(
                            label="다운로드",
                            data=f.read(),
                            file_name=file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{file}"
                        )
        else:
            st.info("아직 생성된 파일이 없습니다.")
    
    # 로그 섹션
    st.subheader("📝 실행 로그")
    log_container = st.container()
    
    # 페이지 하단 정보
    st.markdown("---")
    st.markdown("**💡 사용법**: 사이드바에서 크롤러를 선택하고 실행하세요. 모든 크롤러 실행 후 통합 엑셀 파일을 생성할 수 있습니다.")

if __name__ == "__main__":
    main() 