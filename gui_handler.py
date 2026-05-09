import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import datetime
import logging
import os
import sys
import webbrowser
import urllib.request
import json

# バージョン・GitHub設定
VERSION = "1.3.0"
GITHUB_REPO = "YOUR_USERNAME/YOUR_REPO_NAME" # 要変更

class DashBoardHandler(logging.Handler):
    def __init__(self, display_func):
        super().__init__()
        self.display_func = display_func
    def emit(self, record):
        msg = self.format(record)
        self.display_func(msg)

class BotDashboard:
    def __init__(self, conf_obj, db_obj, bot_instance):
        self.conf = conf_obj
        self.db = db_obj
        self.bot = bot_instance
        
        self.root = tk.Tk()
        self.root.title(f"YouTube Bot 管理コンソール - v{VERSION}")
        self.root.geometry("950x700")
        self.root.configure(bg="#f0f2f5")

        # --- 統計エリア ---
        stat_frame = tk.Frame(self.root, bg="#ffffff", pady=10)
        stat_frame.pack(fill="x", padx=15, pady=10)
        self.lbl_stats = tk.Label(stat_frame, text="統計取得中...", font=("Yu Gothic", 10, "bold"), bg="#ffffff")
        self.lbl_stats.pack(side="left", padx=20)

        # --- メインパネル ---
        main_paned = tk.PanedWindow(self.root, orient="horizontal", bg="#f0f2f5", sashwidth=4)
        main_paned.pack(fill="both", expand=True, padx=15)

        # チャンネル一覧
        left_frame = tk.LabelFrame(main_paned, text=" 連携中のチャンネル ", bg="#ffffff", padx=5, pady=5)
        main_paned.add(left_frame, width=520)
        self.tree = ttk.Treeview(left_frame, columns=("Name", "ID", "Playlist", "Status"), show="headings")
        self.tree.heading("Name", text="サーバー / チャンネル名"); self.tree.heading("ID", text="ID")
        self.tree.heading("Playlist", text="再生リストID"); self.tree.heading("Status", text="状態")
        self.tree.column("Name", width=240); self.tree.column("ID", width=100); self.tree.column("Playlist", width=100); self.tree.column("Status", width=40)
        self.tree.pack(fill="both", expand=True)

        # ログエリア
        right_frame = tk.LabelFrame(main_paned, text=" システムログ ", bg="#ffffff", padx=5, pady=5)
        main_paned.add(right_frame, width=380)
        self.log_area = scrolledtext.ScrolledText(right_frame, state='disabled', bg="#202124", fg="#ffffff", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)

        # --- コマンド入力 ---
        cmd_frame = tk.Frame(self.root, bg="#ffffff", pady=10)
        cmd_frame.pack(fill="x", side="bottom", padx=15, pady=10)
        tk.Label(cmd_frame, text="管理コマンド:", bg="#ffffff", font=("Yu Gothic", 9, "bold")).pack(side="left", padx=5)
        self.cmd_entry = tk.Entry(cmd_frame, font=("Consolas", 10))
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cmd_entry.bind("<Return>", self.execute_command)
        tk.Button(cmd_frame, text="実行", command=self.execute_command, bg="#1a73e8", fg="white", width=10).pack(side="right", padx=5)

        self.refresh_ui()
        self.update_loop()
        self.root.after(1500, self.check_for_updates)

    def check_for_updates(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode())
                latest = data['tag_name'].replace('v', '')
                if latest > VERSION:
                    if messagebox.askyesno("更新", f"最新版 v{latest} が利用可能です。ダウンロードしますか？"):
                        webbrowser.open(data['html_url'])
        except: pass

    def _append_log(self, msg):
        if not self.root.winfo_exists(): return
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def execute_command(self, event=None):
        cmd = self.cmd_entry.get().strip().lower()
        self.cmd_entry.delete(0, tk.END)
        if not cmd: return
        self._append_log(f"> {cmd}")
        
        if cmd == "help":
            self._append_log("利用可能: help, restart, shutdown, sync, cls")
        elif cmd == "restart":
            if messagebox.askyesno("再起動", "Botを再起動しますか？"): os.execl(sys.executable, sys.executable, *sys.argv)
        elif cmd == "shutdown":
            if messagebox.askyesno("終了", "終了しますか？"): os._exit(0)
        elif cmd == "sync":
            self.bot.loop.create_task(self.bot.global_sync_task())
        elif cmd == "cls":
            self.log_area.configure(state='normal'); self.log_area.delete('1.0', tk.END); self.log_area.configure(state='disabled')
        else:
            self._append_log(f"エラー: コマンド '{cmd}' は不明です。")

    def refresh_ui(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in self.db.get_all_settings():
            c = self.bot.get_channel(int(row[0]))
            name = f"{c.guild.name} / {c.name}" if c else f"Unknown ({row[0]})"
            status = "ON" if row[2] else "OFF"
            self.tree.insert("", "end", values=(name, row[0], row[1], status))

    def update_loop(self):
        if not self.root.winfo_exists(): return
        s = self.db.get_stats()
        self.lbl_stats.config(text=f"📊 統計 | 累計: {s['total']}件  本日: {s['today']}件  待機: {s['queue']}件")
        self.refresh_ui()
        self.root.after(15000, self.update_loop)

    def run(self):
        self.root.mainloop()