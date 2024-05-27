import tkinter as tk
from PIL import Image, ImageTk # pip install pillow
from tkinter import simpledialog, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
from utils.diary_manager import sort_diary, save_diary
from utils.sentiment_analysis import sentiment_analysis
from utils.summarizer import summarizer_per_week
from utils.img_generator import text_to_image_base64
from datetime import datetime
import pandas as pd
import random
import os

class DiaryService(tk.Tk):
    def __init__(self, diary, tokenizer, senti_model, config, summarizer, diffusion):
        super().__init__()
        self.diary = diary
        self.tokenizer = tokenizer
        self.senti_model = senti_model
        self.config = config
        self.summarizer = summarizer
        self.diffusion = diffusion
        self.title("- ̗̀ෆ⎛˶'ᵕ'˶ ⎞ෆ ̖́- Daily Diary Journal - ̗̀ෆ⎛˶'ᵕ'˶ ⎞ෆ ̖́-") 
        self.geometry("520x400")
        self.configure(bg='pink')
        self.show_main_menu()
        self.flash_text()

        self.icon_path = os.path.join(os.path.dirname(__file__), '../datasets/image/tiara.ico')
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)

        pic_path = os.path.join(os.path.dirname(__file__), '../datasets/image/default_pic.png')
        if os.path.exists(pic_path):
            image = Image.open(pic_path)
            image = image.resize((300, 300), Image.LANCZOS) # 항상 사이즈 맞춤
            self.default_pic = ImageTk.PhotoImage(image)
        else:
            self.default_pic = None

    # text(main title) 반짝 거리는 효과
    def flash_text(self):
        if hasattr(self, 'title_label') and self.title_label.winfo_exists():
            color = random.choice(['VioletRed1', 'deeppink', 'HotPink1'])
            self.title_label.config(fg=color)
            self.after(300, self.flash_text) # 0.3초마다

    def show_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Main menu widgets
        self.title_label = tk.Label(self, text="♥*♡+:｡.｡ ⍤⃝Daily Diary Journal ⍤⃝｡.｡:+♡*♥", font=("Comic Sans MS", 17, 'bold'), bg='pink', fg='HotPink1')
        self.title_label.pack(pady=50)

        self.view_diary_button = tk.Button(self, text="My Diary", width=15, command=self.update_diary, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.view_diary_button.pack(pady=12)

        self.view_all_diaries_button = tk.Button(self, text="View All", width=15, command=self.view_all_diaries, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.view_all_diaries_button.pack(pady=12)

        self.view_summary_button = tk.Button(self, text="Summary", width=15, command=self.view_weekly_summary, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.view_summary_button.pack(pady=12)

        self.exit_button = tk.Button(self, text="Exit", width=15, command=self.destroy, bg='lightpink', fg='VioletRed1', font=("Comic Sans MS", 12))
        self.exit_button.pack(pady=12)

    def update_diary(self):
        # Clear the window
        for widget in self.winfo_children():
            widget.destroy()

        self.date_label = tk.Label(self, text="Date (YYYY-MM-DD):", bg='pink', font=("Comic Sans MS", 13))
        self.date_label.pack(pady=5)

        self.date_entry = tk.Entry(self, font=("Comic Sans MS", 12))
        self.date_entry.pack(pady=5)

        self.text_label = tk.Label(self, text="₍˄·͈༝·͈˄*₎◞ ̑̑❤️How was your Day?   ₍˄·͈༝·͈˄*₎◞ ̑̑❤️", bg='pink', font=("Comic Sans MS", 13))
        self.text_label.pack(pady=5)

        self.text_entry = tk.Text(self, height=8, font=("Comic Sans MS", 12))
        self.text_entry.pack(pady=5)

        self.save_button = tk.Button(self, text="Save", command=self.submit_diary, bg='lightpink', font=("Comic Sans MS", 10))
        self.save_button.pack(pady=7)

        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=5)
            
    def submit_diary(self):
        date = self.date_entry.get()
        texts = self.text_entry.get("1.0", tk.END).strip()

        # 날짜 형식 확인
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in [YYYY-MM-DD] format!")
            return
        # 지정한 날짜에 이미 일기가 있는지 확인
        if not self.diary[self.diary['datetime'] == date].empty:
            messagebox.showerror("Error", f"Diary for [{date}] already exists!")
            return
        # 일기 공란은 안됨
        if not texts:
            messagebox.showerror("Error", "Diary is empty! Please add an entry!")
            return

        sentiment_scores = sentiment_analysis(self.tokenizer, self.senti_model, self.config, texts)

        if self.diffusion is None:
            new_diary = pd.DataFrame([{'datetime': date, 'texts': texts, 'sentiment': sentiment_scores, 'pic': 'no img'}])
        else:
            image, image_base64 = text_to_image_base64(self.diffusion, texts)
            new_diary = pd.DataFrame([{'datetime': date, 'texts': texts, 'sentiment': sentiment_scores, 'pic': image_base64}])

        self.diary = pd.concat([self.diary, new_diary], ignore_index=True)
        self.diary = sort_diary(self.diary)
        save_diary(self.diary)

        messagebox.showinfo("Info", "Diary updated successfully!")
        self.show_main_menu()
        
    def view_all_diaries(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.title_label = tk.Label(self, text="☆*:.｡.꒰ঌClick on a DATE to view the entry໒꒱.｡.:*☆", font=("Comic Sans MS", 15), bg='pink')
        self.title_label.pack(pady=10)

        self.text_label = ScrolledText(self, width=91, height=12, wrap=tk.WORD, font=("Comic Sans MS", 13))
        self.text_label.pack(pady=1)       
        
        # Display diary list
        if self.diary.empty:
            self.text_label.insert(tk.END, "\t\t  ! NO DIARY SAVED YET !\n")
        else:             
            # Diary list
            self.text_label.bind("<ButtonRelease-1>", self.show_selected_entry)
            
            # Load diary data into list
            diary_dates = self.diary['datetime'].dt.strftime('%Y-%m-%d').tolist()
            diary_moods = self.diary['sentiment'].tolist()    
            diary_info = [(date, mood) for date, mood in zip(diary_dates, diary_moods)]
            
            for date, mood in diary_info:
                mood_emoji = "🆒❤️" if mood == 'positive' else "🆗㋡" if mood == 'neutral' else "🆖💔"
                label_text = f"[{date}] Today's Mood: {mood_emoji}"
                self.text_label.insert(tk.END, label_text)
                self.text_label.insert(tk.END, "\n")

        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=3)

    def show_selected_entry(self, event):
        index = self.text_label.index(tk.CURRENT)
        line_number = int(index.split('.')[0])
        date_line = self.text_label.get(f"{line_number}.0", f"{line_number}.end")
        try:
            date = date_line.split("[")[1].split("]")[0]
            self.read_selected_entry(date)
        except IndexError:
            # Show error message for invalid selection
            messagebox.showerror("Error", "Invalid selection. Please click on a valid date.")

    def read_selected_entry(self, selected_date):
        selected_entry = self.diary[self.diary['datetime'].dt.strftime('%Y-%m-%d') == selected_date]
        if not selected_entry.empty:
            selected_texts = selected_entry.iloc[0]['texts']
            selected_sentiment = selected_entry.iloc[0]['sentiment']
            image_path = selected_entry.iloc[0]['pic']
            
            if image_path == 'no img':
                selected_image = self.default_pic
            else:
                pass
                # image = Image.open(image_path)
                # image = image.resize((300, 300), Image.LANCZOS)
                # selected_image = ImageTk.PhotoImage(image)
            
            self.show_entry_window(selected_date, selected_texts, selected_sentiment, selected_image)
        else:
            messagebox.showinfo("Error", "Please try again on valid data!")

    def show_entry_window(self, date, texts, sentiment, image):
        entry_window = tk.Toplevel(self)
        entry_window.title(f"{date} : {sentiment}")
        entry_window.geometry("600x400")
        entry_window.configure(bg='pink')

        # 이미지와 텍스트 
        left_frame = tk.Frame(entry_window, bg='pink' )
        left_frame.pack(side=tk.LEFT, padx=(10, 0), pady=10)
        
        right_frame = tk.Frame(entry_window, bg='pink')
        right_frame.pack(side=tk.RIGHT, padx=(0, 10), pady=10)

        # 이미지 라벨
        if image:
            image_label = tk.Label(left_frame, image=image)
            image_label.image = image  # Keep a reference to avoid garbage collection
            image_label.pack()
        else:
            image_label = tk.Label(left_frame, text="No image available", font=("Comic Sans MS", 12))
            image_label.pack()

        # 일기글, 감정분석 정보 표시를 위한 ScrolledText
        self.entry_text = ScrolledText(right_frame, width=27, height=20, wrap=tk.WORD, font=("Comic Sans MS", 10))
        self.entry_text.pack(padx=3, pady=3)
        # mood_emoji = "🆒❤️" if sentiment == 'positive' else "🆗㋡" if sentiment == 'neutral' else "🆖💔"
        # entry_text_content = f"[{date}]'s Mood: {mood_emoji}\n\n{texts}"
        self.entry_text.insert(tk.END, texts)
        self.entry_text.configure(state='disabled')  # 입력되는거 방지
        self.selected_date = date # edit에 쓰임

        # # back 버튼
        # back_button_frame = tk.Frame(left_frame, bg='pink')
        # back_button_frame.pack(pady=4, anchor='nw')
        # self.back_button = tk.Button(back_button_frame, text="BACK", command=entry_window.destroy, bg='lightpink', font=("Comic Sans MS", 10))
        # self.back_button.pack(pady=3, expand=True)
        # 수정 버튼
        edit_button_frame = tk.Frame(left_frame, bg='pink')
        edit_button_frame.pack(pady=4, anchor='nw')
        self.edit_button = tk.Button(edit_button_frame, text="EDIT", command=self.edit_selected_entry, bg='lightpink', font=("Comic Sans MS", 10))
        self.edit_button.pack(pady=3, expand=True)

    def edit_selected_entry(self):
        # 편집 가능하도록 텍스트 상자를 활성화
        self.entry_text.configure(state='normal')
        # 'Edit' 버튼을 'Save' 버튼으로 변경
        self.edit_button.configure(text="SAVE", command=self.save_edited_entry)

    def save_edited_entry(self):
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

    def view_weekly_summary(self):          
        # Clear the window
        for widget in self.winfo_children():
            widget.destroy()
        # Calculate weekly summaries
        weekly_summaries = summarizer_per_week(self.diary, self.summarizer)    
        # Display weekly summaries
        self.title_label = tk.Label(self, text="☆*:.｡.꒰ঌWeekly Summaries໒꒱.｡.:*☆", font=("Comic Sans MS", 15), bg='pink')
        self.title_label.pack(pady=10)

        self.text_label = ScrolledText(self, width=91, height=12, wrap=tk.WORD, font=("Comic Sans MS", 13))
        self.text_label.pack(pady=1)       
        
        if weekly_summaries.empty:
            self.text_label.insert(tk.END, "\t\t  ! NO WEEKLY SUMMARIES YET !\n")
        else:
            for index, row in weekly_summaries.iterrows():
                self.text_label.insert(tk.END, f"[{row['Week']}] : #{row['Number']}\n")
                self.text_label.insert(tk.END, f": {row['Summary']}\n")
                self.text_label.insert(tk.END, "--------------------------------------------------\n")
            #self.text_label.insert(tk.END, weekly_summaries.to_string(index=False))

        self.text_label.configure(state='disabled')
        self.back_button = tk.Button(self, text="Back", command=self.show_main_menu, bg='lightpink', font=("Comic Sans MS", 10))
        self.back_button.pack(pady=3)