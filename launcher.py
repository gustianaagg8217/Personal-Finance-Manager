#!/usr/bin/env python3
"""
Personal Finance Manager - Launcher GUI
Provides a unified interface to start CLI or Telegram bot
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
from pathlib import Path
from datetime import datetime

class FinanceLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Manager - Launcher")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Set icon if exists
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # Color scheme
        self.bg_color = "#f0f0f0"
        self.accent_color = "#2E86AB"
        self.success_color = "#06A77D"
        self.warning_color = "#D62839"
        
        self.root.configure(bg=self.bg_color)
        
        # Processes tracking
        self.cli_process = None
        self.bot_process = None
        
        self.setup_ui()
        self.check_environment()
        
    def setup_ui(self):
        """Setup the launcher GUI"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.accent_color, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="💰 Personal Finance Manager", 
                        font=("Segoe UI", 20, "bold"), bg=self.accent_color, fg="white")
        title.pack(pady=10)
        
        subtitle = tk.Label(header_frame, text="CLI + Telegram Bot Launcher", 
                           font=("Segoe UI", 10), bg=self.accent_color, fg="white")
        subtitle.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Environment status
        status_frame = tk.LabelFrame(content_frame, text="📊 System Status", 
                                    font=("Segoe UI", 10, "bold"), bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_text = tk.Label(status_frame, text="Checking environment...", 
                                   justify=tk.LEFT, bg=self.bg_color, font=("Segoe UI", 9))
        self.status_text.pack(anchor=tk.W, padx=10, pady=10)
        
        # Launch options
        launch_frame = tk.LabelFrame(content_frame, text="🚀 Launch Options", 
                                    font=("Segoe UI", 10, "bold"), bg=self.bg_color)
        launch_frame.pack(fill=tk.X, pady=(0, 15))
        
        # CLI Button
        cli_btn_frame = tk.Frame(launch_frame, bg=self.bg_color)
        cli_btn_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.cli_btn = tk.Button(cli_btn_frame, text="▶ Start CLI", 
                                command=self.start_cli, font=("Segoe UI", 11, "bold"),
                                bg=self.success_color, fg="white", padx=15, pady=8,
                                cursor="hand2")
        self.cli_btn.pack(side=tk.LEFT)
        
        cli_desc = tk.Label(cli_btn_frame, 
                           text="Desktop application with full features (Add/Edit/Delete/Reports/Analytics/Export)",
                           font=("Segoe UI", 9), bg=self.bg_color, fg="#555")
        cli_desc.pack(side=tk.LEFT, padx=15)
        
        # Bot Button
        bot_btn_frame = tk.Frame(launch_frame, bg=self.bg_color)
        bot_btn_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.bot_btn = tk.Button(bot_btn_frame, text="▶ Start Telegram Bot", 
                                command=self.start_bot, font=("Segoe UI", 11, "bold"),
                                bg=self.success_color, fg="white", padx=15, pady=8,
                                cursor="hand2")
        self.bot_btn.pack(side=tk.LEFT)
        
        bot_desc = tk.Label(bot_btn_frame, 
                           text="Telegram bot interface (12 menu commands for on-the-go access)",
                           font=("Segoe UI", 9), bg=self.bg_color, fg="#555")
        bot_desc.pack(side=tk.LEFT, padx=15)
        
        # Both Button
        both_btn_frame = tk.Frame(launch_frame, bg=self.bg_color)
        both_btn_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.both_btn = tk.Button(both_btn_frame, text="▶ Start Both", 
                                 command=self.start_both, font=("Segoe UI", 11, "bold"),
                                 bg="#FF9500", fg="white", padx=15, pady=8,
                                 cursor="hand2")
        self.both_btn.pack(side=tk.LEFT)
        
        both_desc = tk.Label(both_btn_frame, 
                            text="Launch both CLI and Telegram bot simultaneously",
                            font=("Segoe UI", 9), bg=self.bg_color, fg="#555")
        both_desc.pack(side=tk.LEFT, padx=15)
        
        # Control options
        control_frame = tk.LabelFrame(content_frame, text="🛠️ Control", 
                                     font=("Segoe UI", 10, "bold"), bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        control_btn_frame = tk.Frame(control_frame, bg=self.bg_color)
        control_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        stop_btn = tk.Button(control_btn_frame, text="⏹ Stop All", 
                            command=self.stop_all, font=("Segoe UI", 10),
                            bg=self.warning_color, fg="white", padx=10, pady=5,
                            cursor="hand2")
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        restart_btn = tk.Button(control_btn_frame, text="🔄 Restart All", 
                               command=self.restart_all, font=("Segoe UI", 10),
                               bg=self.accent_color, fg="white", padx=10, pady=5,
                               cursor="hand2")
        restart_btn.pack(side=tk.LEFT, padx=5)
        
        setup_tg_btn = tk.Button(control_btn_frame, text="🤖 Setup Telegram", 
                                command=self.setup_telegram, font=("Segoe UI", 10),
                                bg="#0088CC", fg="white", padx=10, pady=5,
                                cursor="hand2")
        setup_tg_btn.pack(side=tk.LEFT, padx=5)
        
        docs_btn = tk.Button(control_btn_frame, text="📖 Documentation", 
                            command=self.open_docs, font=("Segoe UI", 10),
                            bg="#555", fg="white", padx=10, pady=5,
                            cursor="hand2")
        docs_btn.pack(side=tk.LEFT, padx=5)
        
        # Footer with timestamp
        footer_frame = tk.Frame(self.root, bg="#ddd", height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        self.timestamp_label = tk.Label(footer_frame, text="", font=("Segoe UI", 8), bg="#ddd", fg="#666")
        self.timestamp_label.pack(pady=5)
        
        self.update_timestamp()
    
    def check_environment(self):
        """Check system environment and dependencies"""
        def check():
            status_items = []
            
            # Check Python version
            py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            status_items.append(f"✅ Python {py_version}")
            
            # Check main files
            main_exists = Path("main.py").exists()
            status_items.append(f"{'✅' if main_exists else '❌'} CLI (main.py)")
            
            bot_exists = Path("run_telegram_bot.py").exists()
            tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
            bot_status = "✅" if (bot_exists and tg_token) else ("⚠️" if bot_exists else "❌")
            status_items.append(f"{bot_status} Telegram Bot{'' if tg_token else ' (Token needed)'}")
            
            db_exists = Path("trades.db").exists()
            status_items.append(f"{'✅' if db_exists else '⚠️'} Database (trades.db)")
            
            # Check config
            config_exists = Path("configs").exists()
            status_items.append(f"{'✅' if config_exists else '❌'} Config folder")
            
            status_text = " | ".join(status_items)
            self.status_text.config(text=status_text)
            
            # Enable/disable buttons
            if main_exists and bot_exists and tg_token:
                self.cli_btn.config(state=tk.NORMAL)
                self.bot_btn.config(state=tk.NORMAL)
                self.both_btn.config(state=tk.NORMAL)
            elif main_exists and bot_exists:
                self.cli_btn.config(state=tk.NORMAL)
                self.bot_btn.config(state=tk.NORMAL)  # Still allow, will prompt for token
                self.both_btn.config(state=tk.NORMAL)
            elif main_exists:
                self.cli_btn.config(state=tk.NORMAL)
                self.bot_btn.config(state=tk.DISABLED)
                self.both_btn.config(state=tk.DISABLED)
            elif bot_exists:
                self.cli_btn.config(state=tk.DISABLED)
                self.bot_btn.config(state=tk.NORMAL)
                self.both_btn.config(state=tk.DISABLED)
            else:
                self.cli_btn.config(state=tk.DISABLED)
                self.bot_btn.config(state=tk.DISABLED)
                self.both_btn.config(state=tk.DISABLED)
        
        threading.Thread(target=check, daemon=True).start()
    
    def start_cli(self):
        """Start the CLI application"""
        try:
            if self.cli_process and self.cli_process.poll() is None:
                messagebox.showwarning("Already Running", "CLI is already running!")
                return
            
            self.cli_process = subprocess.Popen(
                [sys.executable, "main.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            messagebox.showinfo("Started", "CLI application started! 🚀")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start CLI:\n{e}")
    
    def start_bot(self):
        """Start the Telegram bot"""
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not tg_token:
            result = messagebox.showerror(
                "Telegram Token Required",
                "TELEGRAM_BOT_TOKEN is not configured!\n\n"
                "Steps to fix:\n"
                "1. Click 'Setup Telegram' button\n"
                "2. Create bot with @BotFather\n"
                "3. Enter the token when prompted\n\n"
                "Would you like to open the setup guide?"
            )
            # Open setup guide
            readme_path = Path("TELEGRAM_SETUP_GUIDE.md")
            if readme_path.exists():
                try:
                    os.startfile(readme_path) if os.name == 'nt' else os.system(f"xdg-open {readme_path}")
                except:
                    pass
            return
        
        try:
            if self.bot_process and self.bot_process.poll() is None:
                messagebox.showwarning("Already Running", "Telegram bot is already running!")
                return
            
            self.bot_process = subprocess.Popen(
                [sys.executable, "run_telegram_bot.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            messagebox.showinfo("Started", 
                              "Telegram bot started! 🤖\n\n"
                              "Bot commands available:\n"
                              "/add_transaction, /summary,\n"
                              "/category_report, /analytics,\n"
                              "/charts, /help, and more!\n\n"
                              "Check 'Bot window' for activity logs")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bot:\n{e}")
    
    def setup_telegram(self):
        """Setup Telegram bot token"""
        setup_script = Path("quick_setup_telegram.bat")
        if not setup_script.exists():
            messagebox.showerror("Not Found", "quick_setup_telegram.bat not found!")
            return
        
        try:
            subprocess.Popen([str(setup_script)], cwd=os.getcwd())
            messagebox.showinfo("Setup Started", 
                              "Setup window opened!\n\n"
                              "After completing setup:\n"
                              "1. Restart this launcher\n"
                              "2. Try starting the bot again")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open setup:\n{e}")
    
    def start_both(self):
        """Start both CLI and bot"""
        try:
            cli_ok = False
            bot_ok = False
            
            if not (self.cli_process and self.cli_process.poll() is None):
                self.cli_process = subprocess.Popen(
                    [sys.executable, "main.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                cli_ok = True
            
            if not (self.bot_process and self.bot_process.poll() is None):
                self.bot_process = subprocess.Popen(
                    [sys.executable, "run_telegram_bot.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                bot_ok = True
            
            if cli_ok and bot_ok:
                messagebox.showinfo("Started", "Both CLI and Telegram bot started! 🚀🤖")
            elif cli_ok or bot_ok:
                msg = "CLI started! 🚀" if cli_ok else "Telegram bot started! 🤖"
                messagebox.showinfo("Partially Started", msg)
            else:
                messagebox.showwarning("Already Running", "Both are already running!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start:\n{e}")
    
    def stop_all(self):
        """Stop all running processes"""
        count = 0
        
        if self.cli_process and self.cli_process.poll() is None:
            self.cli_process.terminate()
            count += 1
        
        if self.bot_process and self.bot_process.poll() is None:
            self.bot_process.terminate()
            count += 1
        
        if count > 0:
            messagebox.showinfo("Stopped", f"Stopped {count} process(es)! ⏹")
        else:
            messagebox.showwarning("Nothing Running", "No processes are currently running!")
    
    def restart_all(self):
        """Restart all processes"""
        cli_was_running = self.cli_process and self.cli_process.poll() is None
        bot_was_running = self.bot_process and self.bot_process.poll() is None
        
        self.stop_all()
        
        if cli_was_running:
            self.start_cli()
        if bot_was_running:
            self.start_bot()
    
    def open_docs(self):
        """Open documentation"""
        readme_path = Path("README.md")
        if readme_path.exists():
            try:
                os.startfile(readme_path) if os.name == 'nt' else os.system(f"xdg-open {readme_path}")
                messagebox.showinfo("Opening", "README.md opened! 📖")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open README:\n{e}")
        else:
            messagebox.showwarning("Not Found", "README.md not found!")
    
    def update_timestamp(self):
        """Update timestamp in footer"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.config(text=f"Launcher Active | {now}")
        self.root.after(1000, self.update_timestamp)


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceLauncher(root)
    root.mainloop()
