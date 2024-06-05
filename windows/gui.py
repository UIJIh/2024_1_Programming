import tkinter as tk
from PIL import Image, ImageTk # pip install pillow
from tkinter import simpledialog, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
from utils.diary_manager import sort_diary, save_diary
from utils.sentiment_analysis import sentiment_analysis
from utils.summarizer import summarizer
from utils.img_generator import text_to_image_base64, decode_image_base64
from utils.text_generator import generate_texts, generate_summaries
from datetime import datetime
import pandas as pd
import random, os
import pygame # 오디오 파일 재생 위해서 (bgm)
# import sys
# print(sys.path)

class DiaryService(tk.Tk):
    def __init__(self, diary, tokenizer, senti_model, config, text_generator, summarizer, img_generator_base, img_generator_refiner):
        super().__init__()
        
        # 초기화 시 전달받은 인자들 저장
        self.diary = diary
        self.tokenizer = tokenizer
        self.senti_model = senti_model
        self.config = config
        self.summarizer = summarizer 
        self.text_generator = text_generator
        self.img_generator_base = img_generator_base
        self.img_generator_refiner = img_generator_refiner
        
        # 창 제목 설정
        self.title("- ̗̀ෆ⎛˶'ᵕ'˶ ⎞ෆ ̖́- Daily Diary Journal - ̗̀ෆ⎛˶'ᵕ'˶ ⎞ෆ ̖́-")         
        # 창 크기 설정
        self.geometry("520x400")        
        # 배경색 설정
        self.configure(bg='pink')        
        # 메인 메뉴 표시
        self.show_main_menu()        
        # 텍스트 깜빡임 효과
        self.flash_text()
        # 아이콘 경로 설정
        self.icon_path = os.path.join(os.path.dirname(__file__), '../datasets/image/tiara.ico')               
        # 아이콘 파일이 존재하면 설정
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)
        
        # GPU를 사용할 수 없어서 이미지 생성을 못할 때 사용할 기본 이미지 설정
        pic_path = os.path.join(os.path.dirname(__file__), '../datasets/image/default_pic.png')
        
        # 기본 이미지 파일이 존재하면 설정
        if os.path.exists(pic_path):
            image = Image.open(pic_path)
            image = image.resize((300, 300), Image.LANCZOS) # 항상 사이즈 맞춤
            self.default_pic = ImageTk.PhotoImage(image)
        else:
            # 기본 이미지 파일이 존재하지 않으면 None으로 설정
            self.default_pic = None

        pygame.init()  # 모든 pygame 모듈 초기화
        pygame.mixer.init()  # pygame의 mixer 모듈 초기화
          
    # 텍스트(메인 제목) 반짝거리는 효과
    def flash_text(self):
        # 만약 title_label이 존재하고 위젯이 유효하면
        if hasattr(self, 'title_label') and self.title_label.winfo_exists():
            # 무작위로 색상 선택
            color = random.choice(['VioletRed1', 'deeppink', 'HotPink1'])
            # 선택한 색상으로 제목의 글자 색 변경
            self.title_label.config(fg=color)
            # 0.3초 후에 flash_text 함수를 다시 호출
            self.after(300, self.flash_text)
            
    def play_music(self, sentiment):
        """
        감정에 따라 음악을 재생합니다.
        """
        music_files = {
            'positive': 'datasets/music/positive_song.mp3',
            'negative': 'datasets/music/negative_song.mp3',
            'neutral': 'datasets/music/neutral_song.mp3'
        }

        if sentiment in music_files:
            music_file = music_files[sentiment]
            if os.path.isfile(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(loops=-1)  # 무한 반복 재생
            else:
                print(f"Music file for {sentiment} not found.")

    def stop_music(self):
        """
        음악 재생을 중지합니다.
        """
        pygame.mixer.music.stop()
        
    def stop_music_and_close(self, window):
        """
        음악 중지 함수 & 윈도우 닫힘
        """
        def _stop_music_and_close():
            self.stop_music()
            window.destroy()
        return _stop_music_and_close
    
    def show_main_menu(self):
        # 현재 창에 있는 모든 위젯 제거
        for widget in self.winfo_children():
            widget.destroy()
        # 메인 메뉴 위젯 설정
        self.title_label = tk.Label(self, text="♥*♡+:。.。 ⍤⃝Daily Diary Journal ⍤⃝。.。:+♡*♥", font=("Comic Sans MS", 17, 'bold'), bg='pink', fg='HotPink1')
        self.title_label.pack(pady=50)
        # 'My Diary' 버튼 설정 및 배치
        self.view_diary_button = tk.Button(self, text="My Diary", width=15, command=self.update_diary, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.view_diary_button.pack(pady=12)
        # 'View All' 버튼 설정 및 배치
        self.view_all_diaries_button = tk.Button(self, text="View All", width=15, command=self.view_all_diaries, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.view_all_diaries_button.pack(pady=12)
        # 'Summary' 버튼 설정 및 배치
        self.view_summary_button = tk.Button(self, text="Summary", width=15, command=self.view_summary_subdisplay, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.view_summary_button.pack(pady=12)
        # 'Exit' 버튼 설정 및 배치
        self.exit_button = tk.Button(self, text="Exit", width=15, command=self.destroy, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.exit_button.pack(pady=12)
        
    ############################################### 쓰기 (write)
    def update_diary(self):
        # 창을 초기화
        for widget in self.winfo_children():
            widget.destroy()
        # 날짜 입력 라벨 설정 및 배치
        self.date_label = tk.Label(self, text="Date (YYYY-MM-DD):", bg='pink', font=("Comic Sans MS", 13))
        self.date_label.pack(pady=5)
        # 날짜 입력 필드 설정 및 배치
        self.date_entry = tk.Entry(self, font=("Comic Sans MS", 12))
        self.date_entry.pack(pady=5)
        # 일기 입력 라벨 설정 및 배치
        self.text_label = tk.Label(self, text="₍˄·͈༝·͈˄*₎◞ ̑̑❤️How was your Day?  ₍˄·͈༝·͈˄*₎◞ ̑̑❤️\nPut a few keywords, a diary entry will be generated!",bg='pink', font=("Comic Sans MS", 13))
        self.text_label.pack(pady=5)
        # 일기 입력 텍스트 박스 설정 및 배치
        self.text_entry = tk.Text(self, height=6, font=("Comic Sans MS", 12))
        self.text_entry.pack(pady=5)
        # 저장 버튼 설정 및 배치
        self.save_button = tk.Button(self, text="Save", command=self.submit_diary, bg='lightpink', font=("Comic Sans MS", 10))
        self.save_button.pack(pady=7)
        # 뒤로 가기 버튼 설정 및 배치
        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=5)
        
    # 모델 돌려서 저장하기
    def submit_diary(self):
        # 날짜와 텍스트 입력값 가져오기
        date = self.date_entry.get()
        texts = self.text_entry.get("1.0", tk.END).strip()  # 공백 제거
        generated_texts = generate_texts(self.text_generator, texts).strip()  # 텍스트 생성( 모델) + 공백 제거
        # 날짜 형식 확인
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            # 날짜 형식이 올바르지 않으면 에러 메시지 출력
            messagebox.showerror("Error", "Date must be in [YYYY-MM-DD] format!")
            return
        
        # 지정한 날짜에 이미 일기가 있는지 확인
        if not self.diary[self.diary['datetime'] == date].empty:
            # 해당 날짜에 이미 일기가 있으면 에러 메시지 출력
            messagebox.showerror("Error", f"Diary for [{date}] already exists!")
            return
        
        # 일기 내용이 비어있는지 확인
        if not texts:
            # 일기 내용이 없으면 에러 메시지 출력
            messagebox.showerror("Error", "Diary is empty! Please add an entry!")
            return
        # 생성된 텍스트에 대해 감정 분석 수행 (모델)
        sentiment_scores = sentiment_analysis(self.tokenizer, self.senti_model, self.config, generated_texts)
        # 이미지 생성기가 없는 경우 
        if self.img_generator_refiner is None:
            new_diary = pd.DataFrame([{'datetime': date, 'texts': generated_texts, 'sentiment': sentiment_scores, 'pic': 'no img'}])
        else:
            # 텍스트를 이미지로 변환하고 base64 인코딩 (모델)
            image_base64 = text_to_image_base64(self.img_generator_base, self.img_generator_refiner, texts)
            new_diary = pd.DataFrame([{'datetime': date, 'texts': generated_texts, 'sentiment': sentiment_scores, 'pic': image_base64}])
        # 새로운 일기를 기존 일기 데이터프레임에 추가
        self.diary = pd.concat([self.diary, new_diary], ignore_index=True)
        # 일기 정렬
        self.diary = sort_diary(self.diary)
        # 일기 저장
        save_diary(self.diary)
        # 성공 메시지 출력
        messagebox.showinfo("Info", "Diary generated successfully!\nGo to Check!")
        # 메인 메뉴로 돌아가기
        self.show_main_menu()
        
    ##########################################보기 view
    # 모든 일기 보기
    def view_all_diaries(self):
        # 현재 창에 있는 모든 위젯 제거
        for widget in self.winfo_children():
            widget.destroy()
            
        # 제목 라벨 설정 및 배치
        self.title_label = tk.Label(self, text="☆*:.。.꒰ঌClick on a DATE to view the entry໒꒱.。.:*☆", font=("Comic Sans MS", 15), bg='pink')
        self.title_label.pack(pady=10)
        # 스크롤 가능한 텍스트 박스 설정 및 배치
        self.text_label = ScrolledText(self, width=91, height=12, wrap=tk.WORD, font=("Comic Sans MS", 13))
        self.text_label.pack(pady=1)       
        
        # 일기 리스트 표시
        if self.diary.empty:
            # 저장된 일기가 없으면 메시지 출력
            self.text_label.insert(tk.END, "\t\t  ! NO DIARY SAVED YET !\n")
        else:             
            # 일기 리스트
            self.text_label.bind("<ButtonRelease-1>", self.show_selected_entry)
            
            # 일기 데이터를 리스트에 로드
            diary_dates = self.diary['datetime'].dt.strftime('%Y-%m-%d').tolist()
            diary_moods = self.diary['sentiment'].tolist()    
            diary_info = [(date, mood) for date, mood in zip(diary_dates, diary_moods)]
            
            # 각 일기를 텍스트 박스에 삽입
            for date, mood in diary_info:
                mood_emoji = "🆒❤️" if mood == 'positive' else "🆗㋡" if mood == 'neutral' else "🆖💔"
                label_text = f"[{date}] Today's Mood: {mood_emoji}"
                self.text_label.insert(tk.END, label_text)
                self.text_label.insert(tk.END, "\n")
        # 뒤로 가기 버튼 설정 및 배치
        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=3)
        
    # 선택된 일기 보기
    def show_selected_entry(self, event):
        # 현재 클릭한 위치의 인덱스를 가져옴
        index = self.text_label.index(tk.CURRENT)
        # 클릭한 줄 번호를 가져옴
        line_number = int(index.split('.')[0])
        # 해당 줄의 텍스트를 가져옴
        date_line = self.text_label.get(f"{line_number}.0", f"{line_number}.end")
        try:
            # 선택한 날짜를 추출
            date = date_line.split("[")[1].split("]")[0]
            # 선택한 일기 읽기
            self.read_selected_entry(date)
        except IndexError:
            # 유효하지 않은 선택일 경우 에러 메시지 출력
            messagebox.showerror("Error", "Invalid selection. Please click on a valid date.")
            
    # 선택한 날짜의 일기 읽기
    def read_selected_entry(self, selected_date):
        # 선택한 날짜에 해당하는 일기를 가져옴
        selected_entry = self.diary[self.diary['datetime'].dt.strftime('%Y-%m-%d') == selected_date]
        if not selected_entry.empty:
            selected_texts = selected_entry.iloc[0]['texts']
            selected_sentiment = selected_entry.iloc[0]['sentiment']
            selected_image = selected_entry.iloc[0]['pic']
            
            # 이미지가 없는 경우 기본 이미지 설정
            if selected_image == 'no img':
                selected_image = self.default_pic
            else:
                # base64 인코딩된 이미지를 디코딩하여 설정
                selected_image = decode_image_base64(selected_image)
                #selected_image = Image.open(selected_image)
                selected_image = selected_image.resize((300, 300), Image.LANCZOS) # 항상 사이즈 맞춤
                selected_image = ImageTk.PhotoImage(selected_image)
                #print("오예 성공!")
            
            # 선택한 일기를 새 창에 표시
            self.show_entry_window(selected_date, selected_texts, selected_sentiment, selected_image)
        else:
            # 유효한 데이터가 없을 경우 에러 메시지 출력
            messagebox.showinfo("Error", "Please try again on valid data!")
            
    # 선택한 일기를 보여주는 새 창
    def show_entry_window(self, date, texts, sentiment, image):
        # 새 창 생성
        entry_window = tk.Toplevel(self)
        entry_window.title(f"{date} : {sentiment}")
        entry_window.geometry("600x400")
        entry_window.configure(bg='pink')
        # 이미지와 텍스트를 나눌 프레임 설정
        left_frame = tk.Frame(entry_window, bg='pink')
        left_frame.pack(side=tk.LEFT, padx=(10, 0), pady=10)
        
        right_frame = tk.Frame(entry_window, bg='pink')
        right_frame.pack(side=tk.RIGHT, padx=(0, 10), pady=10)
        # 이미지 라벨 설정
        if image:
            # 이미지가 있는 경우
            image_label = tk.Label(left_frame, image=image)
            image_label.image = image  # 참조를 유지하여 가비지 컬렉션 방지
            image_label.pack()
        else:
            # 이미지가 없는 경우
            image_label = tk.Label(left_frame, text="No image available", font=("Comic Sans MS", 12))
            image_label.pack()
        # 일기 텍스트와 감정 분석 정보를 표시하기 위한 ScrolledText
        self.entry_text = ScrolledText(right_frame, width=27, height=20, wrap=tk.WORD, font=("Comic Sans MS", 10))
        self.entry_text.pack(padx=3, pady=3)
        # 일기 내용을 삽입
        self.entry_text.insert(tk.END, texts)
        self.entry_text.configure(state='disabled')  # 입력 방지
        self.selected_date = date  # 편집에 사용
        # 수정 버튼 설정
        edit_button_frame = tk.Frame(left_frame, bg='pink')
        edit_button_frame.pack(pady=4, anchor='nw')
        self.edit_button = tk.Button(edit_button_frame, text="EDIT", command=self.edit_selected_entry, bg='lightpink', font=("Comic Sans MS", 10))
        self.edit_button.pack(pady=3, expand=True)

        # 감정에 따라 음악 재생
        self.play_music(sentiment)

        # 창이 닫힐 때 음악 중지
        entry_window.protocol("WM_DELETE_WINDOW", self.stop_music_and_close(entry_window))
        
    # 선택한 일기를 편집하도록 설정
    def edit_selected_entry(self):
        # 텍스트 상자를 편집 가능하도록 설정
        self.entry_text.configure(state='normal')
        # 'Edit' 버튼을 'Save' 버튼으로 변경
        self.edit_button.configure(text="SAVE", command=self.save_edited_entry)
        
    # 편집된 일기를 저장
    def save_edited_entry(self):
        # 편집된 데이터를 가져옴
        edited_texts = self.entry_text.get('1.0', tk.END)

        # 현재 선택된 일기 데이터 업데이트
        selected_date = self.selected_date
        self.diary.loc[self.diary['datetime'].dt.strftime('%Y-%m-%d') == selected_date, 'texts'] = edited_texts

        # 수정된 일기 내용 저장
        save_diary(self.diary)
        # 메시지 표시
        messagebox.showinfo("Success", "Diary has been successfully edited!")
        # 텍스트 상자를 다시 비활성화
        self.entry_text.configure(state='disabled')

        # 'Save' 버튼을 'Edit' 버튼으로 변경
        self.edit_button.configure(text="EDIT", command=self.edit_selected_entry)
    
    # 편집된 일기를 저장하는 함수
    def save_edited_entry(self):
        # 텍스트 상자에서 편집된 텍스트 가져오기
        edited_texts = self.entry_text.get('1.0', tk.END)
        # 현재 선택된 일기의 날짜 가져오기
        selected_date = self.selected_date
        # 선택된 날짜의 일기 내용을 업데이트
        self.diary.loc[self.diary['datetime'].dt.strftime('%Y-%m-%d') == selected_date, 'texts'] = edited_texts
        # 수정된 일기 내용을 저장
        save_diary(self.diary)
        # 성공 메시지 표시
        messagebox.showinfo("Success", "Diary has been successfully edited!")
        # 텍스트 상자를 다시 비활성화하여 편집 불가능하게 설정
        self.entry_text.configure(state='disabled')
        # 'Save' 버튼을 다시 'Edit' 버튼으로 변경
        self.edit_button.configure(text="EDIT", command=self.edit_selected_entry)
        
    # 요약 옵션 화면을 보여주는 함수
    def view_summary_subdisplay(self):
        # 현재 창에 있는 모든 위젯 제거
        for widget in self.winfo_children():
            widget.destroy()
        # 요약 옵션 버튼 추가
        self.title_label = tk.Label(self, text="♥*♡+:。.。 ⍤⃝Summary Options ⍤⃝。.。:+♡*♥", font=("Comic Sans MS", 17, 'bold'), bg='pink')
        self.title_label.pack(pady=50)
        self.weekly_summary_button = tk.Button(self, text="Weekly Summary", width=20, command=self.view_weekly_summary, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.weekly_summary_button.pack(pady=17)
        self.monthly_summary_button = tk.Button(self, text="Monthly Summary", width=20, command=self.view_monthly_summary, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.monthly_summary_button.pack(pady=15)
        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=10)
        
    # 주간 요약을 보여주는 함수
    def view_weekly_summary(self):          
        # 현재 창에 있는 모든 위젯 제거
        for widget in self.winfo_children():
            widget.destroy()
        # 주간 요약 계산
        #weekly_summaries = summarizer(self.diary, self.summarizer, 'weekly')            
        weekly_summaries = summarizer(self.diary, self.text_generator, generate_summaries, 'weekly') # llama
        # 주간 요약 표시
        self.title_label = tk.Label(self, text="☆*:.。.꒰ঌWeekly Summaries໒꒱.。.:*☆", font=("Comic Sans MS", 15), bg='pink')
        self.title_label.pack(pady=10)
        # 스크롤 가능한 텍스트 상자 생성
        self.text_label = ScrolledText(self, width=91, height=12, wrap=tk.WORD, font=("Comic Sans MS", 13))
        self.text_label.pack(pady=1)       
        
        if weekly_summaries.empty:
            # 요약이 없는 경우 메시지 표시
            self.text_label.insert(tk.END, "\t\t  ! NO WEEKLY SUMMARIES YET !\n")
        else:
            # 주간 요약이 있는 경우 각 요약을 표시
            for index, row in weekly_summaries.iterrows():
                self.text_label.insert(tk.END, f"[{row['Week']}]\nTOTAL : {row['Number']}, AVERAGE MOOD : {row['Average Sentiment']}\n\n")
                self.text_label.insert(tk.END, f": {row['Summary']}\n")
                self.text_label.insert(tk.END, "--------------------------------------------------\n")
            #self.text_label.insert(tk.END, weekly_summaries.to_string(index=False))
        # 텍스트 상자를 읽기 전용으로 설정
        self.text_label.configure(state='disabled')
        # 'Back' 버튼 추가
        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=3)
        
    # 월간 요약을 보여주는 함수
    def view_monthly_summary(self):
        # 현재 창에 있는 모든 위젯 제거
        for widget in self.winfo_children():
            widget.destroy()
        
        # 월간 요약 계산
        # monthly_summaries = summarizer(self.diary, self.summarizer, 'monthly')
        monthly_summaries = summarizer(self.diary, self.text_generator, generate_summaries, 'monthly')  # llama 모델 사용
        
        # 월간 요약 표시
        self.title_label = tk.Label(self, text="☆*:.。.꒰ঌMonthly Summaries໒꒱.。.:*☆", font=("Comic Sans MS", 15), bg='pink')
        self.title_label.pack(pady=10)
        # 스크롤 가능한 텍스트 상자 생성
        self.text_label = ScrolledText(self, width=91, height=12, wrap=tk.WORD, font=("Comic Sans MS", 13))
        self.text_label.pack(pady=1)
        
        # 월간 요약이 없는 경우 메시지 표시
        if monthly_summaries.empty:
            self.text_label.insert(tk.END, "\t\t  ! NO MONTHLY SUMMARIES YET !\n")
        else:
            # 월간 요약이 있는 경우 각 요약을 표시
            for index, row in monthly_summaries.iterrows():
                self.text_label.insert(tk.END, f"[{row['Month']}]\nTOTAL : {row['Number']}, AVERAGE MOOD : {row['Average Sentiment']}\n\n")
                self.text_label.insert(tk.END, f": {row['Summary']}\n")
                self.text_label.insert(tk.END, "--------------------------------------------------\n")
            #self.text_label.insert(tk.END, weekly_summaries.to_string(index=False))
        # 텍스트 상자를 읽기 전용으로 설정
        self.text_label.configure(state='disabled')
        
        # 'Back' 버튼 추가
        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=3)