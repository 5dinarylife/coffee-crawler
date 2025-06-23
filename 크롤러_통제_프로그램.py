import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pandas as pd
from datetime import datetime
import os
import sys
import subprocess
import traceback

class CrawlerController:
    def __init__(self, root):
        self.root = root
        self.root.title("생두 크롤러 통제 프로그램")
        self.root.geometry("900x700")
        
        # 크롤러 정보 (소펙스 제외)
        self.crawlers = {
            'GSC': {'script': 'gsc_crawler.py', 'filename': 'gsc_greenbean.xlsx', 'status': '대기중'},
            '맥널티': {'script': '맥널티_크롤러.py', 'filename': '맥널티_원두.xlsx', 'status': '대기중'},
            '블레스빈': {'script': '블레스빈_크롤러.py', 'filename': '블레스빈_원두.xlsx', 'status': '대기중'},
            '엠아이커피': {'script': '엠아이커피_크롤러.py', 'filename': '엠아이커피_원두.xlsx', 'status': '대기중'},
            '코빈즈': {'script': '코빈즈_크롤러.py', 'filename': '코빈즈_원두.xlsx', 'status': '대기중'},
            '알마씨엘로': {'script': '알마씨엘로_크롤러.py', 'filename': '알마씨엘로_원두.xlsx', 'status': '대기중'}
        }
        
        self.is_running = False
        self.total_data_count = 0
        self.total_time = 0
        self.completed_crawlers = set()  # 완료된 크롤러 추적
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 제목
        title_label = ttk.Label(main_frame, text="생두 크롤러 통제 프로그램", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # 통합 수집 버튼
        self.all_crawl_button = ttk.Button(main_frame, text="모든 크롤러 실행", 
                                          command=self.run_all_crawlers)
        self.all_crawl_button.grid(row=1, column=0, columnspan=4, pady=(0, 20), sticky="ew")
        
        # 구분선
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)
        
        # 개별 크롤러 프레임
        crawler_frame = ttk.LabelFrame(main_frame, text="개별 크롤러", padding="10")
        crawler_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        
        # 크롤러 버튼들과 상태 표시
        self.crawler_buttons = {}
        self.status_labels = {}
        self.time_labels = {}
        self.count_labels = {}
        
        row = 0
        col = 0
        for name, info in self.crawlers.items():
            # 크롤러 버튼
            btn = ttk.Button(crawler_frame, text=f"{name} 크롤링", 
                           command=lambda n=name: self.run_single_crawler(n))
            btn.grid(row=row, column=col*4, padx=5, pady=5, sticky="ew")
            self.crawler_buttons[name] = btn
            
            # 상태 라벨
            status_lbl = ttk.Label(crawler_frame, text="대기중", foreground="gray")
            status_lbl.grid(row=row, column=col*4+1, padx=5, pady=5)
            self.status_labels[name] = status_lbl
            
            # 시간 라벨
            time_lbl = ttk.Label(crawler_frame, text="", foreground="blue")
            time_lbl.grid(row=row, column=col*4+2, padx=5, pady=5)
            self.time_labels[name] = time_lbl
            
            # 데이터 개수 라벨
            count_lbl = ttk.Label(crawler_frame, text="", foreground="green")
            count_lbl.grid(row=row, column=col*4+3, padx=5, pady=5)
            self.count_labels[name] = count_lbl
            
            col += 1
            if col >= 2:  # 2열로 배치
                col = 0
                row += 1
        
        # 통합 결과 프레임
        result_frame = ttk.LabelFrame(main_frame, text="통합 결과", padding="10")
        result_frame.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=(10, 0))
        
        # 통합 결과 라벨들
        self.total_status_label = ttk.Label(result_frame, text="대기중", font=("Arial", 12))
        self.total_status_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        self.total_time_label = ttk.Label(result_frame, text="", font=("Arial", 12))
        self.total_time_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.total_count_label = ttk.Label(result_frame, text="", font=("Arial", 12))
        self.total_count_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 통합 엑셀 생성 버튼
        self.merge_button = ttk.Button(result_frame, text="통합 엑셀 파일 생성", 
                                     command=self.merge_excel_files, state="disabled")
        self.merge_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 진행률 표시
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=4, sticky="ew", pady=10)
        
        # 로그 텍스트
        log_frame = ttk.LabelFrame(main_frame, text="실행 로그", padding="5")
        log_frame.grid(row=6, column=0, columnspan=4, sticky="nsew", pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=10, width=90)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(6, weight=1)
        crawler_frame.columnconfigure(1, weight=1)
        crawler_frame.columnconfigure(3, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def log_message(self, message):
        """로그 메시지 추가"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"로그 메시지 오류: {e}")
        
    def check_merge_button_activation(self):
        """통합 버튼 활성화 조건 확인"""
        # 완료된 크롤러가 하나라도 있으면 통합 버튼 활성화
        if self.completed_crawlers:
            self.root.after(0, lambda: self.merge_button.config(state="normal"))
            self.log_message("통합 엑셀 파일 생성 버튼이 활성화되었습니다.")
        
    def run_single_crawler(self, crawler_name):
        """개별 크롤러 실행"""
        if self.is_running:
            messagebox.showwarning("경고", "다른 크롤러가 실행 중입니다.")
            return
            
        self.is_running = True
        self.crawler_buttons[crawler_name].config(state="disabled")
        self.status_labels[crawler_name].config(text="실행중...", foreground="orange")
        self.time_labels[crawler_name].config(text="")
        self.count_labels[crawler_name].config(text="")
        
        thread = threading.Thread(target=self._run_crawler_thread, args=(crawler_name,))
        thread.daemon = True
        thread.start()
        
    def _run_crawler_thread(self, crawler_name):
        """크롤러 실행 스레드"""
        try:
            start_time = time.time()
            self.log_message(f"{crawler_name} 크롤링 시작...")
            
            # 크롤러 스크립트 실행
            script_name = self.crawlers[crawler_name]['script']
            if os.path.exists(script_name):
                # 환경 변수 설정 (한글 파일명 지원)
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run([sys.executable, script_name], 
                                      capture_output=True, text=True, timeout=300,  # 5분 타임아웃
                                      env=env, encoding='utf-8')
                
                if result.returncode == 0:
                    # 결과 확인
                    filename = self.crawlers[crawler_name]['filename']
                    if os.path.exists(filename):
                        try:
                            df = pd.read_excel(filename, skiprows=1)  # 첫 번째 행(크롤링 일시) 건너뛰기
                            data_count = len(df)
                        except Exception as e:
                            self.log_message(f"{crawler_name} 엑셀 파일 읽기 오류: {e}")
                            data_count = 0
                    else:
                        data_count = 0
                    
                    end_time = time.time()
                    elapsed = end_time - start_time
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)
                    
                    # 완료된 크롤러에 추가
                    self.completed_crawlers.add(crawler_name)
                    
                    # UI 업데이트
                    self.root.after(0, lambda: self._update_crawler_result(
                        crawler_name, "완료", f"{minutes}분 {seconds}초", f"{data_count}개", "green"
                    ))
                    
                    self.log_message(f"{crawler_name} 크롤링 완료! ({data_count}개 데이터, {minutes}분 {seconds}초 소요)")
                    
                    # 통합 버튼 활성화 확인
                    self.check_merge_button_activation()
                    
                else:
                    error_msg = result.stderr if result.stderr else "알 수 없는 오류"
                    self.root.after(0, lambda: self._update_crawler_result(
                        crawler_name, "오류", "", "", "red"
                    ))
                    self.log_message(f"{crawler_name} 크롤링 실패: {error_msg}")
                    
            else:
                self.root.after(0, lambda: self._update_crawler_result(
                    crawler_name, "오류", "", "", "red"
                ))
                self.log_message(f"{crawler_name} 스크립트 파일을 찾을 수 없습니다: {script_name}")
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self._update_crawler_result(
                crawler_name, "타임아웃", "", "", "red"
            ))
            self.log_message(f"{crawler_name} 크롤링 타임아웃 (5분 초과)")
        except Exception as e:
            self.root.after(0, lambda: self._update_crawler_result(
                crawler_name, "오류", "", "", "red"
            ))
            self.log_message(f"{crawler_name} 크롤링 오류: {str(e)}")
            self.log_message(f"상세 오류: {traceback.format_exc()}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.crawler_buttons[crawler_name].config(state="normal"))
            
    def _update_crawler_result(self, crawler_name, status, time_text, count_text, color):
        """크롤러 결과 업데이트"""
        try:
            self.status_labels[crawler_name].config(text=status, foreground=color)
            self.time_labels[crawler_name].config(text=time_text)
            self.count_labels[crawler_name].config(text=count_text)
        except Exception as e:
            print(f"UI 업데이트 오류: {e}")
        
    def run_all_crawlers(self):
        """모든 크롤러 순차 실행"""
        if self.is_running:
            messagebox.showwarning("경고", "크롤러가 이미 실행 중입니다.")
            return
            
        self.is_running = True
        self.all_crawl_button.config(state="disabled")
        self.total_status_label.config(text="실행중...", foreground="orange")
        self.progress.config(maximum=len(self.crawlers), value=0)
        
        thread = threading.Thread(target=self._run_all_crawlers_thread)
        thread.daemon = True
        thread.start()
        
    def _run_all_crawlers_thread(self):
        """모든 크롤러 실행 스레드"""
        try:
            start_time = time.time()
            self.log_message("모든 크롤러 순차 실행 시작...")
            
            total_data_count = 0
            completed_count = 0
            
            for crawler_name in self.crawlers.keys():
                if not self.is_running:  # 중단 체크
                    break
                    
                self.log_message(f"{crawler_name} 크롤링 시작...")
                
                # 개별 크롤러 실행
                self.root.after(0, lambda name=crawler_name: self._update_crawler_result(
                    name, "실행중...", "", "", "orange"
                ))
                
                try:
                    # 크롤러 스크립트 실행
                    script_name = self.crawlers[crawler_name]['script']
                    if os.path.exists(script_name):
                        # 환경 변수 설정
                        env = os.environ.copy()
                        env['PYTHONIOENCODING'] = 'utf-8'
                        
                        result = subprocess.run([sys.executable, script_name], 
                                              capture_output=True, text=True, timeout=300,
                                              env=env, encoding='utf-8')
                        
                        if result.returncode == 0:
                            # 결과 확인
                            filename = self.crawlers[crawler_name]['filename']
                            if os.path.exists(filename):
                                try:
                                    df = pd.read_excel(filename, skiprows=1)
                                    data_count = len(df)
                                    total_data_count += data_count
                                except Exception as e:
                                    self.log_message(f"{crawler_name} 엑셀 파일 읽기 오류: {e}")
                                    data_count = 0
                            else:
                                data_count = 0
                                
                            completed_count += 1
                            self.completed_crawlers.add(crawler_name)
                            
                            self.root.after(0, lambda name=crawler_name, count=data_count: 
                                          self._update_crawler_result(name, "완료", "", f"{count}개", "green"))
                            
                            self.log_message(f"{crawler_name} 완료 ({data_count}개 데이터)")
                        else:
                            error_msg = result.stderr if result.stderr else "알 수 없는 오류"
                            self.root.after(0, lambda name=crawler_name: 
                                          self._update_crawler_result(name, "오류", "", "", "red"))
                            self.log_message(f"{crawler_name} 오류: {error_msg}")
                    else:
                        self.root.after(0, lambda name=crawler_name: 
                                      self._update_crawler_result(name, "오류", "", "", "red"))
                        self.log_message(f"{crawler_name} 스크립트 파일을 찾을 수 없습니다")
                        
                except subprocess.TimeoutExpired:
                    self.root.after(0, lambda name=crawler_name: 
                                  self._update_crawler_result(name, "타임아웃", "", "", "red"))
                    self.log_message(f"{crawler_name} 타임아웃 (5분 초과)")
                except Exception as e:
                    self.root.after(0, lambda name=crawler_name: 
                                  self._update_crawler_result(name, "오류", "", "", "red"))
                    self.log_message(f"{crawler_name} 오류: {str(e)}")
                
                # 진행률 업데이트
                self.root.after(0, lambda: self.progress.config(value=completed_count))
                
            end_time = time.time()
            elapsed = end_time - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            
            # 최종 결과 업데이트
            self.root.after(0, lambda: self._update_total_result(
                "완료", f"{minutes}분 {seconds}초", f"{total_data_count}개", "green"
            ))
            
            self.log_message(f"모든 크롤러 실행 완료! (총 {total_data_count}개 데이터, {minutes}분 {seconds}초 소요)")
            
            # 통합 엑셀 생성 버튼 활성화
            self.check_merge_button_activation()
            
        except Exception as e:
            self.root.after(0, lambda: self._update_total_result("오류", "", "", "red"))
            self.log_message(f"전체 실행 오류: {str(e)}")
            self.log_message(f"상세 오류: {traceback.format_exc()}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.all_crawl_button.config(state="normal"))
            
    def _update_total_result(self, status, time_text, count_text, color):
        """전체 결과 업데이트"""
        try:
            self.total_status_label.config(text=status, foreground=color)
            self.total_time_label.config(text=f"총 소요 시간: {time_text}")
            self.total_count_label.config(text=f"총 데이터 수: {count_text}")
        except Exception as e:
            print(f"전체 결과 업데이트 오류: {e}")
        
    def merge_excel_files(self):
        """모든 엑셀 파일을 하나로 통합"""
        try:
            self.log_message("엑셀 파일 통합 시작...")
            
            all_data = []
            current_time = datetime.now().strftime("통합 일시: %Y-%m-%d %H:%M:%S")
            included_crawlers = []
            
            for crawler_name, info in self.crawlers.items():
                filename = info['filename']
                if os.path.exists(filename):
                    try:
                        df = pd.read_excel(filename, skiprows=1)  # 크롤링 일시 행 건너뛰기
                        if len(df) > 0:  # 데이터가 있는 경우만 포함
                            all_data.append(df)
                            included_crawlers.append(crawler_name)
                            self.log_message(f"{crawler_name} 데이터 추가 ({len(df)}개)")
                        else:
                            self.log_message(f"{crawler_name} 데이터가 없어서 제외됨")
                    except Exception as e:
                        self.log_message(f"{crawler_name} 파일 읽기 오류: {str(e)}")
                else:
                    self.log_message(f"{crawler_name} 파일이 존재하지 않습니다.")
            
            if all_data:
                # 모든 데이터 통합
                merged_df = pd.concat(all_data, ignore_index=True)
                
                # 통합 파일 저장
                merged_filename = f"통합_생두_데이터_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with pd.ExcelWriter(merged_filename, engine='openpyxl') as writer:
                    pd.DataFrame([[current_time]]).to_excel(writer, index=False, header=False)
                    merged_df.to_excel(writer, index=False, startrow=1)
                
                self.log_message(f"통합 완료! 파일명: {merged_filename} (총 {len(merged_df)}개 데이터)")
                self.log_message(f"포함된 크롤러: {', '.join(included_crawlers)}")
                messagebox.showinfo("완료", f"통합 엑셀 파일이 생성되었습니다.\n파일명: {merged_filename}\n총 데이터 수: {len(merged_df)}개\n포함된 크롤러: {', '.join(included_crawlers)}")
            else:
                self.log_message("통합할 데이터가 없습니다.")
                messagebox.showwarning("경고", "통합할 데이터가 없습니다.")
                
        except Exception as e:
            self.log_message(f"통합 오류: {str(e)}")
            self.log_message(f"상세 오류: {traceback.format_exc()}")
            messagebox.showerror("오류", f"엑셀 파일 통합 중 오류가 발생했습니다.\n{str(e)}")

def main():
    try:
        root = tk.Tk()
        app = CrawlerController(root)
        
        # 창 크기 조정 가능하도록 설정
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        root.mainloop()
    except Exception as e:
        print(f"프로그램 실행 오류: {e}")
        print(f"상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 