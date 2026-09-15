import customtkinter as ctk
import json
import os
from datetime import datetime
import time
from fetcher import get_schedule_data

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ScheduleWidget(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Schedule Widget")
        self.geometry("450x600")
        self.attributes('-topmost', True)
        # self.overrideredirect(True) # borderless if they want, but let's keep it draggable for now
        
        self.configure(fg_color="#1a1b26") # Dark background similar to screenshot
        
        self.blocks = []
        self.cookie_value = None
        self.load_cookie()
        
        self.header = ctk.CTkLabel(self, text="Your schedule", font=("Arial", 24, "bold"), text_color="white")
        self.header.pack(pady=15, padx=20, anchor="w")
        
        self.date_label = ctk.CTkLabel(self, text="Loading...", font=("Arial", 14), text_color="#a9b1d6")
        self.date_label.pack(pady=5)
        
        self.countdown_label = ctk.CTkLabel(self, text="", font=("Arial", 18, "bold"), text_color="#bb9af7")
        self.countdown_label.pack(pady=10)
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.block_frames = []
        
        if self.cookie_value:
            self.fetch_data()
        else:
            self.date_label.configure(text="No cookie found. Please log in first.")
            
        self.update_clock()
        
    def load_cookie(self):
        # We can hardcode the cookie provided by the user just for now, or read from a file.
        # Since they provided the raw array, let's just use it:
        self.cookie_value = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiV3VybVpwTnJManc1cEhnYUJSOWJyNDBHdnlsSFlzaHM4RUZrUUQ1aFpsTFFDWGVqLTlhUTFJbU9GWF96Nmt2MDFuRTh3OGUyUjBnaFR0WlM5Z2tQMUEifQ..VCyuLxL9y7FyDnbgiPTFSQ.szPkPc1ktg91mVja_6cO2LmptAYGT9mn1sY4NyMDH3og31VnVFokXM9ZmoMTjDugB9ToapmTKdZaLaIW3A0uqlmy-jgqeS20CE1A7JBGMRxhypMtSeXnKty9zYE8euh-YlJ3m_clq87-Fhx_QTTxemngE4MjhFH8I-uqHw64ZogyJ2jN2G6U7hM_fsSMTIYJjQ8bJqAm_YbwVFU9EVd2hAgm6mB6C8maGnGR69NRuFymlvgyuKi29p0RYveGkHuX_DN2hEsXNncFjx4FXd3rOw3-FBWzBiuEOtt6bs4FfxAHQxmyYQaV_3Mo9MZZXAHhT-4ro6i1HsVYHaMdYVOP0_3Wq9MKQoa7NK8ibU05LldQxmqFHXBWX-6EQgEpowoVF9vFilUxQUpCfF8F1pBiGA.0bcbEEUL0UoTciJWvi3gpD1sTBiailrThQDAQqkL1oI"

    def fetch_data(self):
        data = get_schedule_data(self.cookie_value)
        if data:
            date_str = data.get('date', 'Unknown Date')
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d")
                self.date_label.configure(text=d.strftime("%A %d %B - %Y"))
            except:
                self.date_label.configure(text=date_str)
            
            self.blocks = data.get('blocks', [])
            self.render_blocks()
            
    def render_blocks(self):
        for f in self.block_frames:
            f.destroy()
        self.block_frames.clear()
        
        for idx, b in enumerate(self.blocks):
            frame = ctk.CTkFrame(self.scroll, fg_color="#24283b", corner_radius=8)
            frame.pack(fill="x", pady=5)
            
            time_str = f"{b['start']} - {b['end']}"
            
            title = b['name']
            if b.get('classes') and len(b['classes']) > 0:
                cls = b['classes'][0]
                # Try to clean up title "ENGLISH 12(1400) SN:2 Per:3" -> "ENGLISH 12"
                raw_title = cls.get('title', '')
                clean_title = raw_title.split('(')[0].strip() if '(' in raw_title else raw_title
                title = f"{b.get('period', '')} {clean_title}"
            
            time_lbl = ctk.CTkLabel(frame, text=time_str, font=("Arial", 12), text_color="#7aa2f7", width=100, anchor="w")
            time_lbl.grid(row=0, column=0, padx=10, pady=10)
            
            name_lbl = ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold"), text_color="white", anchor="w")
            name_lbl.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            # Subtext (room and teacher)
            if b.get('classes') and len(b['classes']) > 0:
                cls = b['classes'][0]
                room = cls.get('room', '')
                teachers = cls.get('teachers', [])
                teacher_name = teachers[0].get('name', '') if teachers else ''
                
                sub_str = f"Room {room}"
                if teacher_name: sub_str += f" • {teacher_name}"
                
                sub_lbl = ctk.CTkLabel(frame, text=sub_str, font=("Arial", 11), text_color="#565f89", anchor="w")
                sub_lbl.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")
                
            self.block_frames.append((frame, b))

    def update_clock(self):
        now = datetime.now()
        current_time = now.time()
        
        current_block = None
        
        # Reset all frames
        for frame, b in self.block_frames:
            frame.configure(border_width=0)
            
        for frame, b in self.block_frames:
            try:
                start_h, start_m = map(int, b['start'].split(':'))
                end_h, end_m = map(int, b['end'].split(':'))
                
                start_t = datetime.now().replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                end_t = datetime.now().replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                
                if start_t <= now <= end_t:
                    current_block = (b, end_t)
                    # Highlight this frame
                    frame.configure(border_width=2, border_color="#bb9af7")
                    break
            except:
                continue
                
        if current_block:
            b, end_t = current_block
            diff = end_t - now
            mins, secs = divmod(int(diff.total_seconds()), 60)
            self.countdown_label.configure(text=f"Ends in: {mins:02d}:{secs:02d}")
        else:
            self.countdown_label.configure(text="")
            
        self.after(1000, self.update_clock)

if __name__ == "__main__":
    app = ScheduleWidget()
    app.mainloop()
