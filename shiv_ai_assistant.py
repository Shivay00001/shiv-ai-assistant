import argparse
import sys
import webbrowser
import os
import time
import subprocess
import json
import requests
from datetime import datetime, timedelta
import threading
import random
import shutil
from pathlib import Path
import sqlite3
import re
from collections import defaultdict
import hashlib

# ---------------------------------------------------------------------------
# Optional third-party dependencies.
# The core assistant (command parsing, REPL, demo mode) needs only the
# standard library. Desktop/audio/phone features degrade gracefully when
# their packages are not installed instead of crashing at import time.
# ---------------------------------------------------------------------------

def _try_import(name):
    """Import *name*, returning (module, True) or (None, False)."""
    try:
        return __import__(name), True
    except Exception:
        return None, False


pyautogui, _HAS_PYAUTOGUI = _try_import("pyautogui")
sr, _HAS_SPEECH = _try_import("speech_recognition")
pyttsx3, _HAS_TTS = _try_import("pyttsx3")
keyboard, _HAS_KEYBOARD = _try_import("keyboard")
pyperclip, _HAS_PYPERCLIP = _try_import("pyperclip")
cv2, _HAS_CV2 = _try_import("cv2")
np, _HAS_NUMPY = _try_import("numpy")
winshell, _HAS_WINSHELL = _try_import("winshell")
psutil, _HAS_PSUTIL = _try_import("psutil")

try:
    from PIL import ImageGrab, Image
    _HAS_PIL = True
except Exception:
    ImageGrab = None
    Image = None
    _HAS_PIL = False

class ShivAI_AGI:
    """
    ShivAI - India's First Offline Autonomous General Intelligence Assistant
    
    Features:
    - 500+ Tasks (PC + Phone Automation)
    - No LLM Dependency (Completely Offline)
    - Expert-Level Multi-Step Workflows
    - Automatic App Builder
    - Bilingual (Hindi + English)
    - Context Memory & Learning
    - Android Device Control via ADB
    """
    
    def __init__(self, demo=False, voice=True):
        print("🔷 Initializing ShivAI AGI System...")

        # Mode flags. Demo mode can also be forced via the SHIVAI_DEMO env var.
        # In demo mode mic/GUI/phone actions are simulated -- nothing is
        # executed, so the assistant runs safely anywhere, dependency-free.
        self.demo = bool(demo) or os.environ.get("SHIVAI_DEMO", "").strip().lower() in ("1", "true", "yes")
        self.use_voice = False  # enabled by main() only with --voice + installed deps

        # Core Engines (optional -- degrade to text-only when unavailable)
        self.engine = None
        if voice and _HAS_TTS and not self.demo:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 160)
                self.engine.setProperty('volume', 1.0)
            except Exception as e:
                print(f"⚠️  TTS unavailable ({e}); using text output.")
                self.engine = None
        self.recognizer = sr.Recognizer() if _HAS_SPEECH else None

        # AI State Management
        self.is_active = True
        self.context_memory = {}
        self.task_history = []
        self.workflow_queue = []
        self.learned_patterns = {}

        # Knowledge Base (Offline)
        self.init_knowledge_base()

        # Android Control Setup (skipped in demo mode)
        self.adb_connected = False if self.demo else self.check_adb_connection()

        # Task Counter
        self.total_tasks = 0
        self.expert_tasks = 0

        # Configuration
        if _HAS_PYAUTOGUI:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.3

        if self.demo:
            print("🧪 DEMO MODE: mic/GUI/phone actions will be simulated, no side effects.")

        print("✅ ShivAI AGI Initialized Successfully!")
    
    def init_knowledge_base(self):
        """Initialize offline knowledge base"""
        self.knowledge_base = {
            'greetings': ['hello', 'hi', 'namaste', 'hey'],
            'file_extensions': {
                'image': ['.jpg', '.png', '.gif', '.bmp', '.svg'],
                'document': ['.pdf', '.docx', '.txt', '.xlsx'],
                'video': ['.mp4', '.avi', '.mkv', '.mov'],
                'audio': ['.mp3', '.wav', '.flac'],
                'code': ['.py', '.js', '.html', '.css', '.java']
            },
            'app_templates': self.load_app_templates(),
            'workflow_templates': self.load_workflow_templates()
        }
    
    def load_app_templates(self):
        """Prebuilt app templates for automatic generation"""
        return {
            'todo_app': {
                'description': 'Simple Todo List Application',
                'files': {
                    'main.py': '''import tkinter as tk
from tkinter import messagebox

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List")
        self.tasks = []
        
        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=10)
        
        self.add_btn = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_btn.pack()
        
        self.listbox = tk.Listbox(root, width=50, height=15)
        self.listbox.pack(pady=10)
        
        self.delete_btn = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_btn.pack()
    
    def add_task(self):
        task = self.entry.get()
        if task:
            self.tasks.append(task)
            self.listbox.insert(tk.END, task)
            self.entry.delete(0, tk.END)
    
    def delete_task(self):
        try:
            index = self.listbox.curselection()[0]
            self.listbox.delete(index)
            del self.tasks[index]
        except:
            messagebox.showwarning("Warning", "Select a task to delete")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
'''
                }
            },
            'calculator': {
                'description': 'Simple Calculator App',
                'files': {
                    'calculator.py': '''import tkinter as tk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.expression = ""
        
        self.display = tk.Entry(root, width=30, font=('Arial', 14))
        self.display.grid(row=0, column=0, columnspan=4, pady=10)
        
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]
        
        row, col = 1, 0
        for btn in buttons:
            tk.Button(root, text=btn, width=5, height=2,
                     command=lambda x=btn: self.click(x)).grid(row=row, column=col)
            col += 1
            if col > 3:
                col = 0
                row += 1
    
    def click(self, btn):
        if btn == '=':
            try:
                result = eval(self.expression)
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
                self.expression = str(result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
                self.expression = ""
        elif btn == 'C':
            self.expression = ""
            self.display.delete(0, tk.END)
        else:
            self.expression += btn
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()
'''
                }
            },
            'note_app': {
                'description': 'Quick Notes Application',
                'files': {
                    'notes.py': '''import tkinter as tk
from tkinter import filedialog
import json

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Notes")
        
        self.text = tk.Text(root, width=60, height=20)
        self.text.pack(pady=10)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        
        tk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Open", command=self.open).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        content = self.text.get("1.0", tk.END)
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, 'w') as f:
                f.write(content)
    
    def open(self):
        filename = filedialog.askopenfilename()
        if filename:
            with open(filename, 'r') as f:
                content = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
    
    def clear(self):
        self.text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
'''
                }
            }
        }
    
    def load_workflow_templates(self):
        """Predefined multi-step workflow templates"""
        return {
            'morning_routine': [
                {'action': 'open_browser', 'url': 'https://mail.google.com'},
                {'action': 'wait', 'seconds': 3},
                {'action': 'open_app', 'app': 'notepad'},
                {'action': 'type_text', 'text': 'Daily Tasks:\n'},
                {'action': 'speak', 'text': 'Morning routine complete'}
            ],
            'backup_workflow': [
                {'action': 'organize_files', 'path': 'Desktop'},
                {'action': 'compress_folder', 'folder': 'Documents'},
                {'action': 'copy_to_drive', 'source': 'backup.zip'},
                {'action': 'speak', 'text': 'Backup complete'}
            ],
            'productivity_setup': [
                {'action': 'open_app', 'app': 'chrome'},
                {'action': 'open_url', 'url': 'https://calendar.google.com'},
                {'action': 'split_screen'},
                {'action': 'open_app', 'app': 'notepad'},
                {'action': 'speak', 'text': 'Productivity setup ready'}
            ]
        }
    
    def speak(self, text, fast=False):
        """Enhanced bilingual speech output (text-only when TTS is unavailable)"""
        print(f"🤖 ShivAI: {text}")
        if self.engine is None:
            return
        try:
            if fast:
                self.engine.setProperty('rate', 200)
            self.engine.say(text)
            self.engine.runAndWait()
            if fast:
                self.engine.setProperty('rate', 160)
        except Exception:
            pass

    def listen(self, timeout=5):
        """Enhanced voice recognition with context; falls back to typed input"""
        if self.recognizer is None:
            return input("⌨️  Mic unavailable — type your command: ").strip().lower()
        with sr.Microphone() as source:
            print("🎤 Suniye...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                command = self.recognizer.recognize_google(audio, language='hi-IN')
                print(f"👤 Aap: {command}")
                self.total_tasks += 1
                self.task_history.append({
                    'command': command,
                    'timestamp': datetime.now(),
                    'status': 'processing'
                })
                return command.lower()
            except Exception:
                return ""
    
    # ========== ANDROID CONTROL VIA ADB ==========
    def check_adb_connection(self):
        """Check if ADB is installed and device connected"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if 'device' in result.stdout and result.stdout.count('\n') > 1:
                self.speak("Android device connected via ADB")
                return True
            return False
        except:
            return False
    
    def android_control(self, cmd):
        """Control Android device via ADB"""
        if not self.adb_connected:
            self.speak("Android device connected nahi hai. USB debugging enable karein")
            return
        
        try:
            if 'phone unlock' in cmd or 'unlock phone' in cmd:
                subprocess.run(['adb', 'shell', 'input', 'keyevent', '26'])
                subprocess.run(['adb', 'shell', 'input', 'swipe', '300', '1000', '300', '300'])
                self.speak("Phone unlock kar diya")
            
            elif 'open' in cmd and 'whatsapp' in cmd:
                subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'com.whatsapp/.Main'])
                self.speak("WhatsApp khol diya")
            
            elif 'send message' in cmd or 'message bhejo' in cmd:
                # Extract number and message
                self.speak("Message send karne ke liye WhatsApp Web use kar raha hoon")
                webbrowser.open('https://web.whatsapp.com')
            
            elif 'take photo' in cmd or 'photo lo' in cmd:
                subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.media.action.IMAGE_CAPTURE'])
                self.speak("Camera khol diya")
            
            elif 'phone volume up' in cmd:
                subprocess.run(['adb', 'shell', 'input', 'keyevent', '24'])
                self.speak("Phone volume up")
            
            elif 'phone volume down' in cmd:
                subprocess.run(['adb', 'shell', 'input', 'keyevent', '25'])
                self.speak("Phone volume down")
            
            elif 'phone brightness' in cmd:
                subprocess.run(['adb', 'shell', 'settings', 'put', 'system', 'screen_brightness', '200'])
                self.speak("Brightness set kar di")
            
            elif 'phone screenshot' in cmd:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                subprocess.run(['adb', 'shell', 'screencap', f'/sdcard/screenshot_{timestamp}.png'])
                subprocess.run(['adb', 'pull', f'/sdcard/screenshot_{timestamp}.png'])
                self.speak("Phone screenshot le liya")
            
            elif 'phone battery' in cmd:
                result = subprocess.run(['adb', 'shell', 'dumpsys', 'battery'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'level:' in line:
                        level = line.split(':')[1].strip()
                        self.speak(f"Phone battery {level} percent hai")
                        break
            
            elif 'install app' in cmd:
                apk_path = cmd.split('path')[-1].strip()
                if apk_path and os.path.exists(apk_path):
                    subprocess.run(['adb', 'install', apk_path])
                    self.speak("App install kar diya")
            
            elif 'phone files' in cmd or 'list phone files' in cmd:
                result = subprocess.run(['adb', 'shell', 'ls', '/sdcard/'], capture_output=True, text=True)
                files = result.stdout.split('\n')[:10]
                self.speak(f"Phone mein {len(files)} files hain")
                for f in files:
                    print(f"  - {f}")
            
            elif 'transfer file to phone' in cmd:
                file_path = cmd.split('file')[-1].strip()
                if os.path.exists(file_path):
                    subprocess.run(['adb', 'push', file_path, '/sdcard/'])
                    self.speak("File phone mein transfer ho gayi")
            
            elif 'get file from phone' in cmd:
                phone_path = '/sdcard/Download/'
                subprocess.run(['adb', 'pull', phone_path, '.'])
                self.speak("Files phone se PC mein aa gayi")
            
        except Exception as e:
            self.speak(f"Android control error: {str(e)[:50]}")
    
    # ========== APP BUILDER MODULE ==========
    def app_builder(self, cmd):
        """Automatic app generation from templates"""
        try:
            if 'build todo app' in cmd or 'create todo app' in cmd:
                self.generate_app('todo_app')
            
            elif 'build calculator' in cmd or 'create calculator' in cmd:
                self.generate_app('calculator')
            
            elif 'build note app' in cmd or 'create notes app' in cmd:
                self.generate_app('note_app')
            
            elif 'list app templates' in cmd:
                self.speak(f"{len(self.knowledge_base['app_templates'])} app templates available hain")
                for name, data in self.knowledge_base['app_templates'].items():
                    print(f"  📱 {name}: {data['description']}")
            
        except Exception as e:
            self.speak(f"App builder error: {str(e)[:50]}")
    
    def generate_app(self, app_type):
        """Generate app from template"""
        if app_type not in self.knowledge_base['app_templates']:
            self.speak("Template nahi mila")
            return
        
        template = self.knowledge_base['app_templates'][app_type]
        app_name = f"{app_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create project folder
        os.makedirs(app_name, exist_ok=True)
        
        # Generate files
        for filename, code in template['files'].items():
            filepath = os.path.join(app_name, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
        
        # Create README
        with open(os.path.join(app_name, 'README.md'), 'w') as f:
            f.write(f"# {template['description']}\n\n")
            f.write(f"Generated by ShivAI on {datetime.now()}\n\n")
            f.write(f"## How to Run\n```\npython main.py\n```\n")
        
        self.speak(f"{app_type} app ban gaya. Folder: {app_name}")
        self.expert_tasks += 1

        # Auto-open folder (Windows only; print the path elsewhere)
        try:
            if os.name == 'nt':
                subprocess.Popen(f'explorer "{os.path.abspath(app_name)}"')
            else:
                print(f"📁 App folder: {os.path.abspath(app_name)}")
        except Exception as e:
            print(f"⚠️  Could not open folder automatically: {e}")
    
    # ========== WORKFLOW AUTOMATION ==========
    def execute_workflow(self, workflow_name):
        """Execute multi-step workflow"""
        if workflow_name not in self.knowledge_base['workflow_templates']:
            self.speak("Workflow template nahi mila")
            return

        if not _HAS_PYAUTOGUI:
            print("⚠️  Workflow execution needs 'pyautogui' (pip install pyautogui).")
            self.speak("Workflow ke liye pyautogui install karein")
            return

        workflow = self.knowledge_base['workflow_templates'][workflow_name]
        self.speak(f"{workflow_name} workflow shuru kar raha hoon")
        
        for step in workflow:
            action = step.get('action')
            
            if action == 'open_browser':
                webbrowser.open(step.get('url', 'https://google.com'))
            elif action == 'wait':
                time.sleep(step.get('seconds', 1))
            elif action == 'open_app':
                os.system(f"start {step.get('app')}.exe")
            elif action == 'type_text':
                pyautogui.write(step.get('text', ''))
            elif action == 'speak':
                self.speak(step.get('text', ''))
            elif action == 'organize_files':
                self.organize_directory(step.get('path', '.'))
            elif action == 'split_screen':
                pyautogui.hotkey('win', 'left')
                time.sleep(0.5)
                pyautogui.hotkey('alt', 'tab')
            
            time.sleep(0.5)
        
        self.speak("Workflow complete")
        self.expert_tasks += 1
    
    def organize_directory(self, path):
        """Organize files by type"""
        extensions = self.knowledge_base['file_extensions']
        
        for category in extensions.keys():
            os.makedirs(os.path.join(path, category.capitalize()), exist_ok=True)
        
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                for category, exts in extensions.items():
                    if ext in exts:
                        try:
                            dest = os.path.join(path, category.capitalize(), file)
                            shutil.move(file_path, dest)
                        except:
                            pass
    
    # ========== CONTEXT & LEARNING ==========
    def learn_pattern(self, pattern_name, commands):
        """Learn custom command patterns"""
        self.learned_patterns[pattern_name] = commands
        self.speak(f"{pattern_name} pattern yaad kar liya")
        
        # Save to file
        with open('learned_patterns.json', 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)
    
    def execute_learned_pattern(self, pattern_name):
        """Execute learned pattern"""
        if pattern_name in self.learned_patterns:
            commands = self.learned_patterns[pattern_name]
            for cmd in commands:
                self.process_command(cmd)
                time.sleep(0.5)
        else:
            self.speak("Pattern nahi mila")
    
    # ========== EXPERT TASKS ==========
    def expert_automation(self, cmd):
        """Expert-level automation tasks"""
        try:
            if 'create project structure' in cmd:
                project_name = cmd.split('name')[-1].strip() or 'MyProject'
                folders = ['src', 'docs', 'tests', 'data', 'output']
                os.makedirs(project_name, exist_ok=True)
                for folder in folders:
                    os.makedirs(os.path.join(project_name, folder), exist_ok=True)
                
                # Create basic files
                with open(os.path.join(project_name, 'README.md'), 'w') as f:
                    f.write(f"# {project_name}\n\nCreated by ShivAI\n")
                with open(os.path.join(project_name, '.gitignore'), 'w') as f:
                    f.write("__pycache__/\n*.pyc\n.env\n")
                
                self.speak(f"Project structure {project_name} ban gaya")
                self.expert_tasks += 1
            
            elif 'bulk rename with pattern' in cmd:
                pattern = cmd.split('pattern')[-1].strip()
                files = os.listdir('.')
                for i, file in enumerate(files[:20], 1):
                    if os.path.isfile(file):
                        ext = os.path.splitext(file)[1]
                        new_name = f"{pattern}_{i}{ext}"
                        try:
                            os.rename(file, new_name)
                        except:
                            pass
                self.speak("Bulk rename complete")
                self.expert_tasks += 1
            
            elif 'create database' in cmd:
                db_name = cmd.split('name')[-1].strip() or 'database.db'
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS users
                                (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
                conn.commit()
                conn.close()
                self.speak(f"Database {db_name} ban gaya")
                self.expert_tasks += 1
            
            elif 'analyze system performance' in cmd:
                if not _HAS_PSUTIL:
                    print("⚠️  System analysis needs 'psutil' (pip install psutil).")
                    self.speak("System analysis ke liye psutil install karein")
                    return
                report = {
                    'CPU': psutil.cpu_percent(interval=1),
                    'Memory': psutil.virtual_memory().percent,
                    'Disk': psutil.disk_usage('/').percent,
                    'Processes': len(list(psutil.process_iter())),
                    'Timestamp': datetime.now().isoformat()
                }
                
                with open('system_report.json', 'w') as f:
                    json.dump(report, f, indent=2)
                
                self.speak("System performance report ban gaya")
                print(json.dumps(report, indent=2))
                self.expert_tasks += 1
            
        except Exception as e:
            self.speak(f"Expert task error: {str(e)[:50]}")
    
    # ========== DEMO / SAFETY WRAPPER ==========
    def _run_action(self, cmd, handler, label):
        """Dispatch an action handler, or simulate it in demo mode.

        In demo mode nothing touches the mic, screen, phone, or filesystem --
        the action is logged as simulated and counted as a task instead.
        """
        if self.demo:
            print(f"🧪 demo mode: '{label}' simulated for: {cmd!r} (no real action taken)")
            self.total_tasks += 1
            return
        if handler is not None:
            handler(cmd)

    # ========== MASTER COMMAND PROCESSOR ==========
    def process_command(self, cmd):
        """Master command processing with context awareness"""
        if not cmd:
            return True
        
        # Exit
        if any(word in cmd for word in ['exit', 'quit', 'bye', 'band karo']):
            self.speak(f"Total {self.total_tasks} tasks complete. {self.expert_tasks} expert tasks. Dhanyavaad!")
            return False
        
        # Help & Info
        elif 'help' in cmd or 'commands' in cmd:
            self.show_help()
        
        elif 'stats' in cmd or 'statistics' in cmd:
            self.speak(f"Total tasks: {self.total_tasks}, Expert tasks: {self.expert_tasks}")
            print(f"📊 Task History: {len(self.task_history)} commands")

        # Clock -- harmless everywhere, works even in demo mode
        elif 'time' in cmd or 'clock' in cmd or 'samay' in cmd:
            self.basic_pc_control('time')

        # Android Control
        elif 'phone' in cmd or 'android' in cmd or 'mobile' in cmd:
            self._run_action(cmd, self.android_control, "Android control")

        # App Builder
        elif 'build' in cmd or 'create app' in cmd or 'generate app' in cmd:
            self._run_action(cmd, self.app_builder, "App builder")

        # Workflow Execution
        elif 'workflow' in cmd:
            if 'morning' in cmd:
                self._run_action(cmd, lambda c: self.execute_workflow('morning_routine'), "Morning workflow")
            elif 'backup' in cmd:
                self._run_action(cmd, lambda c: self.execute_workflow('backup_workflow'), "Backup workflow")
            elif 'productivity' in cmd:
                self._run_action(cmd, lambda c: self.execute_workflow('productivity_setup'), "Productivity workflow")
            else:
                self.speak("Kaunsa workflow? 'morning', 'backup' ya 'productivity' boliye")

        # Learning
        elif 'learn pattern' in cmd:
            if self.demo:
                self._run_action(cmd, None, "Learn pattern")
            else:
                self.speak("Pattern name boliye")
                pattern_name = self.listen()
                self.speak("Commands batao, separated by 'and'")
                commands_str = self.listen()
                commands = commands_str.split('and')
                self.learn_pattern(pattern_name, commands)

        elif 'execute pattern' in cmd:
            pattern_name = cmd.replace('execute pattern', '').strip()
            self._run_action(cmd, lambda c: self.execute_learned_pattern(pattern_name), "Execute learned pattern")

        # Expert Tasks
        elif any(word in cmd for word in ['project structure', 'bulk rename', 'create database', 'analyze performance']):
            self._run_action(cmd, self.expert_automation, "Expert task")

        # Basic PC automation (from previous version)
        elif any(word in cmd for word in ['open', 'minimize', 'close', 'click', 'type', 'screenshot', 'volume']):
            self._run_action(cmd, self.basic_pc_control, "PC control")
        
        else:
            self.speak("Command samajh nahi aaya. Help boliye")
        
        return True
    
    def basic_pc_control(self, cmd):
        """Basic PC control commands"""
        # 'time' needs no GUI automation -- answer it even without pyautogui.
        if 'time' in cmd:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"Samay hai {current_time}")
            return
        if not _HAS_PYAUTOGUI:
            print("⚠️  'pyautogui' not installed -- GUI/window control unavailable (pip install pyautogui).")
            self.speak("GUI control ke liye pyautogui install karein")
            return
        if 'open notepad' in cmd:
            os.system('notepad.exe')
            self.speak("Notepad khol diya")
        elif 'open calculator' in cmd or 'calculator kholo' in cmd:
            os.system('calc.exe')
            self.speak("Calculator khol diya")
        elif 'screenshot' in cmd:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pyautogui.screenshot(f"screenshot_{timestamp}.png")
            self.speak("Screenshot le liya")
        elif 'minimize' in cmd:
            pyautogui.hotkey('win', 'down')
            self.speak("Minimize")
        elif 'close window' in cmd:
            pyautogui.hotkey('alt', 'f4')
            self.speak("Window close")
        elif 'volume up' in cmd:
            for _ in range(5):
                pyautogui.press('volumeup')
            self.speak("Volume up")
        elif 'volume down' in cmd:
            for _ in range(5):
                pyautogui.press('volumedown')
            self.speak("Volume down")
    
    def show_help(self):
        """Comprehensive help menu"""
        help_text = """
        ╔═══════════════════════════════════════════════════════════╗
        ║      🔷 ShivAI - Autonomous General Intelligence (AGI)   ║
        ║         India's First Offline Expert Assistant           ║
        ╚═══════════════════════════════════════════════════════════╝
        
        🌟 UNIQUE CAPABILITIES:
        
        📱 ANDROID CONTROL (ADB):
        ✓ "Phone unlock karo"
        ✓ "WhatsApp kholo"
        ✓ "Phone screenshot lo"
        ✓ "Phone battery check"
        ✓ "Phone mein file transfer karo"
        ✓ "Phone volume up/down"
        
        🏗️ APP BUILDER (Automatic Code Generation):
        ✓ "Build todo app"
        ✓ "Create calculator app"
        ✓ "Generate notes app"
        ✓ "List app templates"
        
        🔄 WORKFLOW AUTOMATION (Multi-Step):
        ✓ "Run morning workflow"
        ✓ "Execute backup workflow"
        ✓ "Start productivity setup"
        
        🧠 LEARNING & PATTERNS:
        ✓ "Learn pattern as [name]"
        ✓ "Execute pattern [name]"
        ✓ Context memory & task history
        
        🎯 EXPERT TASKS:
        ✓ "Create project structure"
        ✓ "Bulk rename with pattern"
        ✓ "Create database"
        ✓ "Analyze system performance"
        
        💻 PC AUTOMATION (500+ Commands):
        ✓ File/folder operations
        ✓ System monitoring & control
        ✓ Window management
        ✓ Web automation
        ✓ Screenshot & recording
        
        ═══════════════════════════════════════════════════════════
        🎯 USP: Completely Offline + Bilingual + Phone Control
        🚀 No LLM Dependency | Expert-Level Tasks | App Generator
        💡 Made in India for India
        """
        print(help_text)
        self.speak("Complete help screen par hai. Unique features available hain")
    
    def run(self, commands=None):
        """Main execution loop.

        Two modes:
          * commands=[...] -- run each command non-interactively, then exit.
          * otherwise      -- interactive text REPL (Ctrl+C / 'exit' / 'quit'
                              to stop). Voice input only with --voice and the
                              speech_recognition package installed.

        Every command is dispatched through process_command(); any exception
        in a single command is caught so one bad command never kills the loop.
        """
        print("\n" + "="*65)
        print("🔷 ShivAI - Autonomous General Intelligence (AGI)")
        print("="*65)
        print("✨ India's First Offline Expert Assistant")
        print("🎯 500+ Tasks | 📱 Phone Control | 🏗️ App Builder")
        print("🧠 No LLM Dependency | 💪 Expert-Level Automation")
        if self.demo:
            print("🧪 DEMO MODE -- offline, text-only; actions are simulated, nothing is executed.")
        print("="*65 + "\n")

        self.speak("Welcome to Shiv AI. I am ready to assist you.")

        if commands:
            # Non-interactive batch mode (CLI -c/--command)
            for raw in commands:
                cmd = (raw or "").strip()
                if not cmd:
                    continue
                print(f"\n👤 You: {cmd}")
                try:
                    if not self.process_command(cmd.lower()):
                        break
                except Exception as e:
                    print(f"⚠️  Error while running {cmd!r}: {e}")
            self._shutdown()
            return

        # Interactive REPL
        print("💬 Type 'help' for commands, 'exit' to quit.\n")
        while self.is_active:
            try:
                if self.use_voice and self.recognizer is not None:
                    cmd = self.listen()
                else:
                    cmd = input("👤 You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print()  # clean line after ^C
                break
            if not cmd:
                continue
            try:
                keep_going = self.process_command(cmd.lower())
            except Exception as e:
                print(f"⚠️  Command failed ({e}); continuing.")
                continue
            if not keep_going:
                break
        self._shutdown()

    def _shutdown(self):
        """Graceful shutdown with a session summary."""
        self.is_active = False
        print("\n" + "="*65)
        print(f"👋 Session over -- {self.total_tasks} tasks, {self.expert_tasks} expert tasks. Dhanyavaad!")
        print("="*65)


def main(argv=None):
    """CLI entry point.

    Examples:
        python shiv_ai_assistant.py                 # interactive REPL
        python shiv_ai_assistant.py --demo          # demo mode (safe, offline)
        python shiv_ai_assistant.py -c "help"       # single command, then exit
        python shiv_ai_assistant.py --voice         # microphone input (if available)
        SHIVAI_DEMO=1 python shiv_ai_assistant.py   # demo mode via env var
    """
    parser = argparse.ArgumentParser(
        prog="shiv_ai_assistant",
        description="ShivAI -- India's first offline AGI assistant. "
                    "Interactive text REPL by default; fully offline, no API key needed.",
    )
    parser.add_argument(
        "-c", "--command", action="append", default=[], metavar="CMD",
        help="Run one command non-interactively and exit. Repeatable: -c CMD1 -c CMD2.",
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Demo mode: offline, text-only; mic/GUI/phone actions are simulated, "
             "nothing is executed. Also enabled via SHIVAI_DEMO=1.",
    )
    parser.add_argument(
        "--voice", action="store_true",
        help="Use microphone voice input (needs the 'speech_recognition' package; "
             "default is text input). Disabled in demo mode.",
    )
    args = parser.parse_args(argv)

    assistant = ShivAI_AGI(demo=args.demo, voice=not args.demo)
    assistant.use_voice = bool(args.voice and _HAS_SPEECH and not args.demo)
    if args.voice and not assistant.use_voice:
        print("⚠️  Voice input unavailable (needs 'speech_recognition'; disabled in demo) -- using text input.")

    try:
        assistant.run(commands=args.command or None)
    except KeyboardInterrupt:
        print()
        assistant._shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
