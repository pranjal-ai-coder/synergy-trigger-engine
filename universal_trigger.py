import tkinter as tk
from tkinter import font, messagebox, scrolledtext, filedialog
import json
import os
import threading
import time
import subprocess
import speech_recognition as sr
import pyaudio
import math
import struct
import webbrowser
import pythoncom  # Ye import sabse upar honi chahiye
import win32com.client
import ctypes           # <-- Window Auto-Arrange ke liye

# --- CONSTANTS & SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "mode": "voice",
    "wake_word": "chatur active",
    "action_list": [], 
    "clap_threshold": 0.25
}

# --- STYLING (CYBER-DARK THEME) ---
BG_COLOR = "#0D1117"
FG_COLOR = "#C9D1D9"
PANEL_BG = "#161B22"
ACCENT_GREEN = "#00FF9D"
ACCENT_RED = "#FF4444"
INPUT_BG = "#010409"
HOVER_COLOR = "#00CC7A"

class SynergyEngine(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SYNERGY TRIGGER ENGINE - BY BOSS PRANJAL")
        
        # FULL SCREEN / MAXIMIZED HACKER GUI
        self.state('zoomed') 
        self.configure(bg=BG_COLOR)
        
        self.checkbox_vars = []
        self.is_running = False
        self.engine_thread = None
        
        self.load_settings()
        self.build_gui()
        self.refresh_checkboxes()
        self.is_speaking = False # Nayi line
    def speak(self, text):
        if self.is_speaking: return # Lock check
        
        def run_speech():
            self.is_speaking = True # Lock set
            pythoncom.CoInitialize() 
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Rate = -2 
                speaker.Volume = 100
                
                # Zira check
                voices = speaker.GetVoices()
                for voice in voices:
                    if "Zira" in voice.GetDescription():
                        speaker.Voice = voice
                        break
                
                speaker.Speak(text)
            except Exception as e:
                self.log_gui(f"[AUDIO ERROR] {e}", color=ACCENT_RED)
            finally:
                self.is_speaking = False # Lock release
                pythoncom.CoUninitialize()

        import threading
        threading.Thread(target=run_speech, daemon=True).start()

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
            self.settings = DEFAULT_SETTINGS
        else:
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = DEFAULT_SETTINGS

    def save_settings(self):
        self.settings["mode"] = self.mode_var.get()
        self.settings["wake_word"] = self.word_var.get().lower()
        
        with open(SETTINGS_FILE, 'w') as f: 
            json.dump(self.settings, f, indent=4)
            
        self.log_gui("[SYSTEM] Config Saved.", color=ACCENT_GREEN)

    # --- BUTTON HOVER EFFECT UTILITY ---
    def make_btn(self, parent, text, command, bg, fg, hover_bg=HOVER_COLOR):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, 
                        font=("Consolas", 10, "bold"), relief="flat", cursor="hand2", padx=10, pady=5)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg, fg="black"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg, fg=fg))
        return btn

    def add_script(self):
        file_path = filedialog.askopenfilename(
            title="Select File", 
            filetypes=[
                ("All Files", "*.*"),
                ("Python Files", "*.py"),
                ("Media Files", "*.mp3 *.wav *.mp4 *.mkv *.avi"),
                ("Executables", "*.exe *.bat *.cmd")
            ]
        )
        if file_path:
            if file_path not in self.settings.get("action_list", []):
                self.settings.setdefault("action_list", []).append(file_path)
                self.save_settings()
                self.refresh_checkboxes()
                self.log_gui(f"[ADDED] {os.path.basename(file_path)}", color=FG_COLOR)
            else:
                self.log_gui("[INFO] File pehle se list mein hai.", color=ACCENT_GREEN)

    def clear_scripts(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all scripts?"):
            self.settings["action_list"] = []
            self.save_settings()
            self.refresh_checkboxes()
            self.log_gui("[SYSTEM] All scripts cleared.", color=ACCENT_RED)

    def refresh_checkboxes(self):
        for widget in self.check_frame.winfo_children():
            widget.destroy()
        self.checkbox_vars = []

        paths = self.settings.get("action_list", [])
        for path in paths:
            var = tk.BooleanVar(value=True)
            display_name = path.replace("https://", "").replace("http://", "").replace("www.", "") if path.startswith("http") else os.path.basename(path)
            
            cb = tk.Checkbutton(self.check_frame, text=display_name, 
                               variable=var, bg=BG_COLOR, fg=FG_COLOR, 
                               selectcolor=PANEL_BG, font=("Consolas", 11), activebackground=BG_COLOR, activeforeground=ACCENT_GREEN)
            cb.pack(anchor="w", padx=10, pady=5)
            self.checkbox_vars.append((var, path))

    def build_gui(self):
        # ---------------------------------------------------------
        # NEW COLOR PALETTE (DEEP CYBER THEME)
        # ---------------------------------------------------------
        BG_MAIN = "#09090B"
        BG_PANEL = "#18181B"
        ACCENT_CYAN = "#00FFFF"
        ACCENT_PURPLE = "#C026D3"
        TEXT_PRIMARY = "#F4F4F5"
        TEXT_MUTED = "#A1A1AA"
        GLOW_CYAN = "#00D4FF"
        GLOW_PURPLE = "#D946EF"
        
        font_title = ("Courier New", 18, "bold")
        font_main = ("Consolas", 11)
        font_small = ("Consolas", 10)

        # ---------------------------------------------------------
        # 1. TOP HEADER WITH PULSE ANIMATION
        # ---------------------------------------------------------
        header = tk.Frame(self, bg=BG_MAIN, highlightbackground=ACCENT_PURPLE, highlightthickness=2)
        header.pack(fill="x", pady=10, padx=15)
        
        self.header_label = tk.Label(header, text="❖ SYNERGY TRIGGER CORE v3.0 ❖", font=font_title, bg=BG_MAIN, fg=ACCENT_CYAN)
        self.header_label.pack(pady=10)
        
        # Pulse animation for header
        def pulse_header():
            current_color = self.header_label.cget('fg')
            next_color = GLOW_CYAN if current_color == ACCENT_CYAN else ACCENT_CYAN
            self.header_label.config(fg=next_color)
            self.after(1500, pulse_header)
        
        self.after(100, pulse_header)

        # ---------------------------------------------------------
        # MAIN BODY CONTAINER
        # ---------------------------------------------------------
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=15, pady=5)

        # LEFT PANEL
        left_panel = tk.Frame(body, bg=BG_PANEL, highlightbackground="#27272A", highlightthickness=1)
        left_panel.pack(side="left", fill="y", padx=(0, 10), ipadx=10)

        tk.Label(left_panel, text="[ SYSTEM_CONFIG ]", font=("Consolas", 12, "bold"), bg=BG_PANEL, fg=ACCENT_PURPLE).pack(pady=15, anchor="w", padx=15)

        # Trigger Mode
        tk.Label(left_panel, text="> TRIGGER_MODE:", font=font_small, bg=BG_PANEL, fg=TEXT_MUTED).pack(anchor="w", padx=15, pady=(5,0))
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "voice"))
        
        tk.Radiobutton(left_panel, text="Voice (Wake-Word)", variable=self.mode_var, value="voice", bg=BG_PANEL, fg=TEXT_PRIMARY, 
                    selectcolor=BG_MAIN, activebackground=BG_PANEL, activeforeground=GLOW_CYAN, font=font_main, cursor="hand2",
                    highlightbackground=GLOW_CYAN, highlightthickness=1, highlightcolor=GLOW_CYAN).pack(anchor="w", padx=20, pady=5)
        tk.Radiobutton(left_panel, text="Acoustic (Clap)", variable=self.mode_var, value="clap", bg=BG_PANEL, fg=TEXT_PRIMARY, 
                    selectcolor=BG_MAIN, activebackground=BG_PANEL, activeforeground=GLOW_CYAN, font=font_main, cursor="hand2",
                    highlightbackground=GLOW_CYAN, highlightthickness=1, highlightcolor=GLOW_CYAN).pack(anchor="w", padx=20)

        # Wake Word Input
        tk.Label(left_panel, text="> WAKE_WORD:", font=font_small, bg=BG_PANEL, fg=TEXT_MUTED).pack(anchor="w", padx=15, pady=(20,0))
        self.word_var = tk.StringVar(value=self.settings.get("wake_word", ""))
        entry = tk.Entry(left_panel, textvariable=self.word_var, font=font_main, bg=BG_MAIN, fg=ACCENT_CYAN, 
                        insertbackground=ACCENT_CYAN, relief="flat", highlightbackground=GLOW_PURPLE, highlightthickness=2,
                        highlightcolor=GLOW_PURPLE, bd=0)
        entry.pack(fill="x", padx=15, pady=8, ipady=4)

        # Status Indicator with glow
        self.status_label = tk.Label(left_panel, text="● STATUS: STANDBY", font=("Consolas", 13, "bold"), 
                                    bg=BG_PANEL, fg="#EF4444", highlightbackground="#EF4444", highlightthickness=2)
        self.status_label.pack(pady=30)

        # RIGHT PANEL
        right_panel = tk.Frame(body, bg=BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True)

        # Tools Frame
        tools_frame = tk.Frame(right_panel, bg=BG_PANEL, highlightbackground="#27272A", highlightthickness=1)
        tools_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(tools_frame, text="[ PAYLOAD_INJECTORS ]", font=("Consolas", 12, "bold"), bg=BG_PANEL, fg=ACCENT_PURPLE).pack(pady=10, anchor="w", padx=15)

        btn_grid = tk.Frame(tools_frame, bg=BG_PANEL)
        btn_grid.pack(fill="x", padx=15, pady=(0, 15))

        # Pro-level buttons with hover glow
        def create_glow_btn(parent, text, command, bg_color, fg_color):
            btn = tk.Button(parent, text=text, font=("Consolas", 11, "bold"), bg=bg_color, fg=fg_color, 
                        relief="flat", bd=0, activebackground=GLOW_CYAN, activeforeground="#000",
                        cursor="hand2", highlightthickness=0, pady=8, padx=15)
            
            def on_enter(e):
                btn.config(bg=GLOW_CYAN if fg_color == ACCENT_CYAN else GLOW_PURPLE, fg="#000")
            def on_leave(e):
                btn.config(bg=bg_color, fg=fg_color)
                
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.config(command=command)
            return btn

        create_glow_btn(btn_grid, "➕ SCRIPT", self.add_script, BG_MAIN, ACCENT_CYAN).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        create_glow_btn(btn_grid, "🔗 URL", self.add_url_gui, BG_MAIN, ACCENT_CYAN).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        create_glow_btn(btn_grid, "🛠 TOOLS", self.select_system_tool, BG_MAIN, ACCENT_CYAN).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        create_glow_btn(btn_grid, "📂 BROWSE", self.browse_system_tools, BG_MAIN, ACCENT_CYAN).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        create_glow_btn(btn_grid, "🗑 CLEAR", self.clear_scripts, "#1F0000", "#EF4444").grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_grid.grid_columnconfigure(0, weight=1)
        btn_grid.grid_columnconfigure(1, weight=1)
        btn_grid.grid_columnconfigure(2, weight=1)

        # Checkbox & Log frames (unchanged structure)
        self.check_frame = tk.Frame(right_panel, bg=BG_PANEL, highlightbackground="#27272A", highlightthickness=1)
        self.check_frame.pack(fill="both", expand=True, pady=(0, 10))

        log_frame = tk.Frame(right_panel, bg=BG_PANEL, highlightbackground="#27272A", highlightthickness=1)
        log_frame.pack(fill="x")
        
        tk.Label(log_frame, text=">_ LIVE_TERMINAL", font=font_small, bg=BG_PANEL, fg=TEXT_MUTED).pack(anchor="w", padx=10, pady=5)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=7, bg=BG_MAIN, fg=ACCENT_CYAN, font=("Consolas", 9), 
                                                relief="flat", state="disabled", insertbackground=ACCENT_CYAN,
                                                selectbackground=GLOW_CYAN, selectforeground=BG_MAIN)
        self.log_area.pack(fill="x", padx=10, pady=(0, 10))

        # BOTTOM CONTROLS with pro animations
        ctrl_frame = tk.Frame(self, bg=BG_MAIN)
        ctrl_frame.pack(fill="x", pady=10, padx=15)

        self.start_btn = tk.Button(ctrl_frame, text="▶ ENGAGE SYSTEM", font=("Courier New", 14, "bold"), 
                                bg="#064E3B", fg="#10B981", command=self.start_engine, relief="flat", 
                                activebackground=GLOW_CYAN, activeforeground="#000", cursor="hand2",
                                highlightthickness=0, pady=10)
        
        def start_hover(e):
            self.start_btn.config(bg="#10B981", fg="#000")
        def start_leave(e):
            self.start_btn.config(bg="#064E3B", fg="#10B981")
        
        self.start_btn.bind("<Enter>", start_hover)
        self.start_btn.bind("<Leave>", start_leave)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_btn = tk.Button(ctrl_frame, text="■ HALT SYSTEM", font=("Courier New", 14, "bold"), 
                                bg="#7F1D1D", fg="#EF4444", command=self.stop_engine, relief="flat",
                                activebackground="#FF4444", activeforeground="#000", state="disabled", cursor="hand2",
                                highlightthickness=0, pady=10)
        
        def stop_hover(e):
            self.stop_btn.config(bg="#EF4444", fg="#000")
        def stop_leave(e):
            self.stop_btn.config(bg="#7F1D1D", fg="#EF4444")
        
        self.stop_btn.bind("<Enter>", stop_hover)
        self.stop_btn.bind("<Leave>", stop_leave)
        self.stop_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.log_gui("Synergy Core Re-Architected. Awaiting Boss...", color=ACCENT_CYAN)

    def log_gui(self, message, color=ACCENT_GREEN):
        def update():
            self.log_area.config(state="normal")
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state="disabled")
        self.after(0, update)

    # --- NEW PRO GUI FOR URL ADDING ---
    def add_url_gui(self):
        url_win = tk.Toplevel(self)
        url_win.title("Add Web Link")
        url_win.geometry("400x150")
        url_win.configure(bg=PANEL_BG)
        url_win.resizable(False, False)

        tk.Label(url_win, text="Enter Website URL:", font=("Consolas", 10), bg=PANEL_BG, fg=FG_COLOR).pack(pady=(15,5))
        url_entry = tk.Entry(url_win, font=("Consolas", 11), bg=INPUT_BG, fg=ACCENT_GREEN, insertbackground=ACCENT_GREEN, width=40)
        url_entry.pack(pady=5)
        url_entry.focus()

        def save_url():
            url = url_entry.get().strip()
            if url:
                if not url.startswith("http"): url = "https://" + url
                if url not in self.settings.get("action_list", []):
                    self.settings.setdefault("action_list", []).append(url)
                    self.save_settings()
                    self.refresh_checkboxes()
                    self.log_gui(f"[ADDED URL] {url}", color=ACCENT_GREEN)
            url_win.destroy()

        self.make_btn(url_win, "ADD LINK", save_url, INPUT_BG, "#3498db").pack(pady=10)

    def get_chrome_path(self):
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def browse_system_tools(self):
        system_dir = r"C:\Windows\System32"
        file_path = filedialog.askopenfilename(
            initialdir=system_dir,
            title="Select System Tool",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            if file_path not in self.settings.get("action_list", []):
                self.settings.setdefault("action_list", []).append(file_path)
                self.save_settings()
                self.refresh_checkboxes()
                self.log_gui(f"[ADDED SYSTEM TOOL] {os.path.basename(file_path)}", color=ACCENT_GREEN)

    def select_system_tool(self):
        tool_window = tk.Toplevel(self)
        tool_window.title("Select System Tool")
        tool_window.geometry("350x450")
        tool_window.configure(bg=PANEL_BG)

        tools = {
            "Command Prompt": "cmd", "Notepad": "notepad", "Calculator": "calc",
            "Task Manager": "taskmgr", "Control Panel": "control", "Paint": "mspaint",
            "Registry Editor": "regedit", "Services": "services.msc", "System Information": "msinfo32"
        }

        tk.Label(tool_window, text="Select Tool to Add:", font=("Consolas", 11, "bold"), bg=PANEL_BG, fg=FG_COLOR).pack(pady=10)
        tool_list = tk.Listbox(tool_window, bg=INPUT_BG, fg=FG_COLOR, font=("Consolas", 11), selectbackground=ACCENT_GREEN, selectforeground="black", borderwidth=0)
        tool_list.pack(fill="both", expand=True, padx=20, pady=5)

        for name in tools:
            tool_list.insert(tk.END, name)

        def add_selected():
            selection = tool_list.curselection()
            if selection:
                name = tool_list.get(selection[0])
                cmd = tools[name]
                entry = f"tool:{cmd}"
                if entry not in self.settings.get("action_list", []):
                    self.settings.setdefault("action_list", []).append(entry)
                    self.save_settings()
                    self.refresh_checkboxes()
                    self.log_gui(f"[ADDED TOOL] {name}", color=ACCENT_GREEN)
                tool_window.destroy()

        self.make_btn(tool_window, "ADD SELECTED", add_selected, INPUT_BG, "#e67e22").pack(pady=15)

    # --- WINDOW AUTO-ARRANGE LOGIC ---
    def snap_window_to_quadrant(self, hwnd, index, total_windows):
        """Pro-Level Dynamic Window Snapping Logic"""
        try:
            user32 = ctypes.windll.user32
            
            # IMPORTANT: Window ko pehle 'Restore' mode mein laao 
            # (Agar background window maximized hui, toh move nahi hogi, isliye restore karna zaruri hai)
            user32.ShowWindow(hwnd, 9) # 9 = SW_RESTORE
            
            # Screen dimensions
            sw = user32.GetSystemMetrics(0)
            sh = user32.GetSystemMetrics(1)
            
            # --- DYNAMIC LAYOUT LOGIC ---
            
            if total_windows == 1:
                # 1 App: Full Screen Maximize
                user32.ShowWindow(hwnd, 3) # 3 = SW_MAXIMIZE
                self.log_gui("[SNAP] 1 Window -> Fullscreen Set")
                return # Yahan se nikal jao, SetWindowPos ki zarurat nahi
                
            elif total_windows == 2:
                # 2 Apps: 50-50 Side by Side (Left aur Right)
                w = sw // 2
                h = sh
                x = 0 if index == 0 else w
                y = 0
                
            elif total_windows == 3:
                # 3 Apps: Pehli window Left mein half, baaki 2 Right mein half-half (Top/Bottom)
                if index == 0:
                    w = sw // 2
                    h = sh
                    x = 0
                    y = 0
                else:
                    w = sw // 2
                    h = sh // 2
                    x = sw // 2
                    y = 0 if index == 1 else h
                    
            else:
                # 4 (ya usse zyada) Apps: Proper 4 Quadrants (Grid)
                w = sw // 2
                h = sh // 2
                # 4 ke baad wapas zero se wrap ho jaye
                safe_index = index % 4
                x = (safe_index % 2) * w
                y = (safe_index // 2) * h

            # Window ko naye coordinates par set karo (0x0040 = SWP_SHOWWINDOW)
            user32.SetWindowPos(hwnd, 0, x, y, w, h, 0x0040)
            self.log_gui(f"[SNAP] Window {index+1}/{total_windows} set dynamically!")

        except Exception as e:
            self.log_gui(f"[ERROR] Snapping failed: {e}", color=ACCENT_RED) # Assuming ACCENT_RED defined

    def execute_action(self):
        selected_items = [path for var, path in self.checkbox_vars if var.get()]
        
        if not selected_items:
            self.log_gui("[INFO] Kuch bhi selected nahi hai.", color=FG_COLOR)
            return

        window_counter = 0
        user32 = ctypes.windll.user32
        
        # --- PRO LEVEL LOGIC: Total apps count karo ---
        total_apps = len(selected_items)

        for path in selected_items:
            path = path.strip()
            try:
                # 1. App Launching Logic
                if path.startswith("tool:"):
                    tool_cmd = path.split(":")[1]
                    subprocess.Popen([tool_cmd], shell=True)
                    self.log_gui(f"[LAUNCHED TOOL] {tool_cmd}", color=ACCENT_GREEN)
                elif path.startswith("http"):
                    chrome_path = self.get_chrome_path()
                    if chrome_path:
                        subprocess.Popen([chrome_path, path])
                    else:
                        webbrowser.open(path)
                    self.log_gui(f"[OPENED URL] {path}", color=ACCENT_GREEN)
                elif path.lower().endswith(".exe"):
                    subprocess.Popen([path])
                    self.log_gui(f"[LAUNCHED EXE] {os.path.basename(path)}", color=ACCENT_GREEN)
                elif path.lower().endswith(".py"):
                    subprocess.Popen(['python', path], shell=True)
                    self.log_gui(f"[LAUNCHED SCRIPT] {os.path.basename(path)}", color=ACCENT_GREEN)
                else:
                    os.startfile(path)
                    self.log_gui(f"[OPENED FILE] {os.path.basename(path)}", color=ACCENT_GREEN)
                
                # 2. Robust Snapping (Retry Loop)
                # Hum 3 seconds tak wait karenge window ke active hone ka
                found_window = False
                for _ in range(6): 
                    time.sleep(0.5) 
                    active_hwnd = user32.GetForegroundWindow()
                    
                    # Agar handle valid hai, toh snap karo aur break karo
                    if active_hwnd:
                        # --- UPDATE: total_apps parameter add kar diya ---
                        self.snap_window_to_quadrant(active_hwnd, window_counter, total_apps)
                        self.log_gui(f"[SNAP] Window positioned successfully.")
                        found_window = True
                        break
                
                if not found_window:
                    self.log_gui("[WARN] Could not detect window handle for snap.", color=ACCENT_RED)
                
                window_counter += 1 # Isko simple counter rakha hai, baaki math naye function mein hai

            except Exception as e:
                self.log_gui(f"[ERROR] {e}", color=ACCENT_RED)

        # 3. Finalization
        self.speak("SIR, ALL COMMANDS EXECUTED SUCCESSFULLY")
        self.stop_engine()

    def start_engine(self):
        self.save_settings() 
        self.is_running = True
        self.start_btn.config(state="disabled", bg="#161B22")
        self.stop_btn.config(state="normal", bg="#440000")
        self.status_label.config(text="● STATUS: ACTIVE", fg=ACCENT_GREEN)
        
        self.engine_thread = threading.Thread(target=self.run_engine, daemon=True)
        self.engine_thread.start()

    def stop_engine(self):
        self.is_running = False
        self.start_btn.config(state="normal", bg="#004422")
        self.stop_btn.config(state="disabled", bg="#161B22")
        self.status_label.config(text="● STATUS: IDLE", fg=ACCENT_RED)
        self.log_gui("[SYSTEM] Engine stopped.", color=ACCENT_RED)

    def get_rms(self, block):
        count = len(block) / 2
        format = "%dh" % (count)
        shorts = struct.unpack(format, block)
        sum_squares = sum(sample * sample for sample in shorts)
        return math.sqrt(sum_squares / count) / 32768.0
    
    def run_engine(self):
        mode = self.settings["mode"]
        
        if mode == "voice":
            self.log_gui(f"[LISTENING] Mode: Voice | Wake Word: '{self.settings['wake_word']}'")
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 2000
            
            try:
                with sr.Microphone() as source: # <-- Yaha error aata tha
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    while self.is_running:
                        try:
                            audio = recognizer.listen(source, phrase_time_limit=3, timeout=1)
                            text = recognizer.recognize_google(audio).lower()
                            self.log_gui(f"Heard: {text}", color=FG_COLOR)
                            
                            if self.settings["wake_word"] in text:
                                self.log_gui(f"[TRIGGER] Wake word match confirmed!", color=ACCENT_GREEN)
                                self.execute_action()
                                break
                        except sr.WaitTimeoutError:
                            continue 
                        except sr.UnknownValueError:
                            continue 
                        except Exception as e:
                            self.log_gui(f"[ERROR] Recognition error: {e}", color=ACCENT_RED)
                            break
            except Exception as e:
                self.log_gui(f"[CRITICAL] Microphone not found: {e}", color=ACCENT_RED)
                self.stop_engine() # Crash hone se bachaya aur engine stop kiya
                            
        elif mode == "clap":
            self.log_gui(f"[LISTENING] Mode: Acoustic (Clap) | Awaiting Spike...")
            try:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
                
                while self.is_running:
                    try:
                        data = stream.read(1024, exception_on_overflow=False)
                        volume = self.get_rms(data)
                        
                        if volume > self.settings["clap_threshold"]:
                            self.log_gui(f"[TRIGGER] Audio Spike Detected! (Vol: {volume:.3f})", color=ACCENT_GREEN)
                            self.execute_action()
                            break
                    except Exception as e:
                        self.log_gui(f"[ERROR] Audio processing error: {e}", color=ACCENT_RED)
                        break
                
                stream.stop_stream()
                stream.close()
                p.terminate()
            except Exception as e:
                self.log_gui(f"[CRITICAL] No Audio Input device detected: {e}", color=ACCENT_RED)
                self.stop_engine()

if __name__ == "__main__":
    app = SynergyEngine()
    app.mainloop()


    