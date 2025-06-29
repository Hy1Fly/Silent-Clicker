#you need "pip install pynput psutil pywin32 ttkthemes PyInstaller" in cmd.exe
#and I use PyInstaller for package

#This is 2.0.1 ver code 20250629-2
import time
import threading
import random
import sys
import os
from pynput.mouse import Controller, Button, Listener
from collections import deque
import tkinter as tk
from tkinter import ttk, Frame, Label, Scale, Button as TkButton, Entry, Checkbutton, BooleanVar

class SilentClicker:
    def __init__(self):
        self.threshold_cps = 7
        self.max_cps = 20
        self.randomness = 0.3
        self.hide_gui = False
        self.hide_position = (0, 0)
        
        self.mouse = Controller()
        self.user_clicks = deque()
        self.auto_clicks = deque()
        self.running = False
        self.auto_active = False
        self.click_lock = threading.Lock()
        
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()
        
        self.monitor_thread = None
        self.auto_thread = None
        
        self.create_gui()
        print("Silent-Clicker initialized. Press F1 to hide/show GUI.")
    
    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("AutoClicker Settings")
        self.root.geometry("400x450")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.root.bind("<F1>", self.toggle_gui)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background="#121212")
        style.configure("TLabel", background="#121212", foreground="#e0e0e0", font=("Arial", 10))
        style.configure("TScale", background="#121212", foreground="#bb86fc")
        style.configure("TCheckbutton", background="#121212", foreground="#e0e0e0")
        style.configure("TButton", background="#3700B3", foreground="white", font=("Arial", 10, "bold"))
        style.map("TButton", background=[("active", "#6200EE")])
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = Label(main_frame, text="SILENT-CLICKER", font=("Arial", 16, "bold"), 
                     fg="#bb86fc", bg="#121212")
        title.pack(pady=(0, 15))
        
        threshold_frame = Frame(main_frame, bg="#121212")
        threshold_frame.pack(fill=tk.X, pady=5)
        
        Label(threshold_frame, text="Activation Threshold (CPS):", bg="#121212", fg="#e0e0e0").pack(anchor=tk.W)
        self.threshold_var = tk.IntVar(value=self.threshold_cps)
        threshold_slider = Scale(threshold_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                                variable=self.threshold_var, bg="#121212", fg="#bb86fc", 
                                troughcolor="#333333", highlightbackground="#121212")
        threshold_slider.pack(fill=tk.X)
        
        maxcps_frame = Frame(main_frame, bg="#121212")
        maxcps_frame.pack(fill=tk.X, pady=5)
        
        Label(maxcps_frame, text="Maximum CPS:", bg="#121212", fg="#e0e0e0").pack(anchor=tk.W)
        self.maxcps_var = tk.IntVar(value=self.max_cps)
        maxcps_slider = Scale(maxcps_frame, from_=1, to=50, orient=tk.HORIZONTAL, 
                             variable=self.maxcps_var, bg="#121212", fg="#bb86fc", 
                             troughcolor="#333333", highlightbackground="#121212")
        maxcps_slider.pack(fill=tk.X)
        
        randomness_frame = Frame(main_frame, bg="#121212")
        randomness_frame.pack(fill=tk.X, pady=5)
        
        Label(randomness_frame, text="Randomness:", bg="#121212", fg="#e0e0e0").pack(anchor=tk.W)
        self.randomness_var = tk.DoubleVar(value=self.randomness)
        randomness_slider = Scale(randomness_frame, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL, 
                                 variable=self.randomness_var, bg="#121212", fg="#bb86fc", 
                                 troughcolor="#333333", highlightbackground="#121212")
        randomness_slider.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="Status: Stopped")
        status_label = Label(main_frame, textvariable=self.status_var, 
                           font=("Arial", 10, "bold"), fg="#03DAC5", bg="#121212")
        status_label.pack(pady=10)
        
        button_frame = Frame(main_frame, bg="#121212")
        button_frame.pack(fill=tk.X, pady=15)
        
        self.toggle_button = TkButton(button_frame, text="Start AutoClicker", command=self.toggle_autoclicker,
                                    bg="#3700B3", fg="white", relief=tk.FLAT, padx=15)
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        hide_button = TkButton(button_frame, text="Hide GUI (F1)", command=self.hide_gui_window,
                             bg="#333333", fg="white", relief=tk.FLAT, padx=15)
        hide_button.pack(side=tk.RIGHT, padx=5)
        
        self.hide_label = Label(main_frame, text="Hidden position: (0, 0)", 
                               fg="#666666", bg="#121212", font=("Arial", 8))
        self.hide_label.pack(pady=(10, 0))
        
        footer = Label(main_frame, text="Silent-Clicker v1.1 | Press F1 to toggle GUI", 
                     fg="#666666", bg="#121212", font=("Arial", 8))
        footer.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def on_click(self, x, y, button, pressed):
        if button == Button.left and pressed:
            with self.click_lock:
                now = time.time()
                self.user_clicks.append(now)
                while self.user_clicks and now - self.user_clicks[0] > 1.0:
                    self.user_clicks.popleft()
    
    def get_current_user_cps(self):
        with self.click_lock:
            now = time.time()
            while self.user_clicks and now - self.user_clicks[0] > 1.0:
                self.user_clicks.popleft()
            return len(self.user_clicks)
    
    def get_total_cps(self):
        now = time.time()
        with self.click_lock:
            user_count = sum(1 for t in self.user_clicks if now - t <= 1.0)
            auto_count = sum(1 for t in self.auto_clicks if now - t <= 1.0)
            return user_count + auto_count
    
    def monitor_cps(self):
        while self.running:
            self.threshold_cps = self.threshold_var.get()
            self.max_cps = self.maxcps_var.get()
            self.randomness = self.randomness_var.get()
            
            user_cps = self.get_current_user_cps()
            
            if user_cps >= self.threshold_cps:
                if not self.auto_active:
                    print(f"User CPS: {user_cps} >= threshold. Activating auto-click.")
                    self.auto_active = True
                    self.status_var.set(f"Status: Active ({user_cps} CPS)")
            else:
                if self.auto_active:
                    print(f"User CPS: {user_cps} < threshold. Deactivating auto-click.")
                    self.auto_active = False
                    self.status_var.set(f"Status: Waiting ({user_cps} CPS)")
            
            time.sleep(0.1)
    
    def humanized_interval(self, base_interval):
        rand_factor = 1 + random.uniform(-self.randomness, self.randomness)
        interval = base_interval * rand_factor
        
        if random.random() < 0.05:
            interval *= 0.2
        
        return max(interval, 0.01)
    
    def auto_click_loop(self):
        while self.running:
            if self.auto_active:
                current_cps = self.get_total_cps()
                available_cps = max(0, self.max_cps - current_cps)
                
                if available_cps > 0:
                    base_interval = 1.0 / available_cps
                    
                    interval = self.humanized_interval(base_interval)
                    
                    self.mouse.press(Button.left)
                    self.mouse.release(Button.left)
                    
                    with self.click_lock:
                        now = time.time()
                        self.auto_clicks.append(now)
                        while self.auto_clicks and now - self.auto_clicks[0] > 2.0:
                            self.auto_clicks.popleft()
                    
                    time.sleep(interval)
                else:
                    time.sleep(0.05)
            else:
                time.sleep(0.1)
    
    def toggle_autoclicker(self):
        if not self.running:
            self.start_autoclicker()
        else:
            self.stop_autoclicker()
    
    def start_autoclicker(self):
        if self.running:
            return
        
        self.running = True
        self.auto_active = False
        
        self.monitor_thread = threading.Thread(target=self.monitor_cps, daemon=True)
        self.monitor_thread.start()
        
        self.auto_thread = threading.Thread(target=self.auto_click_loop, daemon=True)
        self.auto_thread.start()
        
        self.toggle_button.config(text="Stop AutoClicker", bg="#B00020")
        self.status_var.set("Status: Running - Waiting for threshold")
        print("AutoClicker started.")
    
    def stop_autoclicker(self):
        if not self.running:
            return
        
        self.running = False
        self.auto_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=0.5)
        
        if self.auto_thread and self.auto_thread.is_alive():
            self.auto_thread.join(timeout=0.5)
        
        self.monitor_thread = None
        self.auto_thread = None
        
        self.toggle_button.config(text="Start AutoClicker", bg="#3700B3")
        self.status_var.set("Status: Stopped")
        print("AutoClicker stopped.")
    
    def hide_gui_window(self, event=None):
        if not self.hide_gui:
            self.hide_position = (self.root.winfo_x(), self.root.winfo_y())
            self.root.withdraw()
            self.hide_gui = True
            self.hide_label.config(text=f"Hidden position: {self.hide_position}")
            print(f"GUI hidden at position: {self.hide_position}")
        else:
            self.root.deiconify()
            self.root.geometry(f"+{self.hide_position[0]}+{self.hide_position[1]}")
            self.hide_gui = False
            print("GUI restored")
    
    def toggle_gui(self, event=None):
        if self.hide_gui:
            self.root.deiconify()
            self.root.geometry(f"+{self.hide_position[0]}+{self.hide_position[1]}")
            self.hide_gui = False
            print("GUI restored")
        else:
            self.hide_position = (self.root.winfo_x(), self.root.winfo_y())
            self.root.withdraw()
            self.hide_gui = True
            self.hide_label.config(text=f"Hidden position: {self.hide_position}")
            print(f"GUI hidden at position: {self.hide_position}")
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        self.stop_autoclicker()
        self.listener.stop()
        self.root.destroy()
        print("Silent-Clicker closed.")
        sys.exit(0)

if __name__ == "__main__":
    print("Starting Silent-Clicker...")
    clicker = SilentClicker()
    clicker.run()
