import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import datetime
import logging
import os
import sys

class DashBoardHandler(logging.Handler):
    """loggingの出力をGUIのログエリアに転送するハンドラ"""
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
        self.root.title(f"YouTube Bot 管理コンソール")
        self.root.geometry("950x700")
        self.root.configure(bg="#f0f2f5")

        # --- 上部: 統計エリア ---
        stat_frame = tk.Frame(self.root, bg="#ffffff", pady=10)
        stat_frame.pack(fill="x", padx=15, pady=10)
        self.lbl_stats = tk.Label(stat_frame, text="統計を取得中...", font=("Yu Gothic", 10, "bold"), bg="#ffffff")
        self.lbl_stats.pack(side="left", padx=20)

        # --- メイン: 左右分割 ---
        main_paned = tk.PanedWindow(self.root, orient="horizontal", bg="#f0f2f5", sashwidth=4)
        main_paned.pack(fill="both", expand=True, padx=15)

        # 左側: 連携チャンネル一覧
        left_frame = tk.LabelFrame(main_paned, text=" 連携中のチャンネル ", bg="#ffffff", padx=5, pady=5)
        main_paned.add(left_frame, width=500)
        
        self.tree = ttk.Treeview(left_frame, columns=("Name", "ID", "Playlist", "Status"), show="headings")
        self.tree.heading("Name", text="サーバー / チャンネル名")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Playlist", text="再生リストID")
        self.tree.heading("Status", text="状態")
        self.tree.column("Name", width=220); self.tree.column("ID", width=100); self.tree.column("Playlist", width=100); self.tree.column("Status", width=40)
        self.tree.pack(fill="both", expand=True)

        # 右側: システムログ
        right_frame = tk.LabelFrame(main_paned, text=" システムログ ", bg="#ffffff", padx=5, pady=5)
        main_paned.add(right_frame, width=400)
        self.log_area = scrolledtext.ScrolledText(right_frame, state='disabled', bg="#202124", fg="#ffffff", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)

        # --- 下部: 管理コマンド入力 ---
        cmd_frame = tk.Frame(self.root, bg="#ffffff", pady=10)
        cmd_frame.pack(fill="x", side="bottom", padx=15, pady=10)
        
        tk.Label(cmd_frame, text="管理コマンド:", bg="#ffffff", font=("Yu Gothic", 9, "bold")).pack(side="left", padx=5)
        self.cmd_entry = tk.Entry(cmd_frame, font=("Consolas", 10))
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cmd_entry.bind("<Return>", self.execute_command)
        
        btn_run = tk.Button(cmd_frame, text="実行", command=self.execute_command, bg="#1a73e8", fg="white", width=10)
        btn_run.pack(side="right", padx=5)

        self.refresh_ui()
        self.update_loop()

    def _append_log(self, msg):
        """ログエリアにテキストを追加（スレッドセーフを考慮）"""
        if not self.root.winfo_exists(): return
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def execute_command(self, event=None):
        raw_cmd = self.cmd_entry.get().strip().lower()
        self.cmd_entry.delete(0, tk.END)
        if not raw_cmd: return

        self._append_log(f"> {raw_cmd}")
        
        if raw_cmd == "help":
            self._append_log("利用可能なコマンド:\n - help: ヘルプ表示\n - restart: Botを再起動\n - shutdown: Botを終了\n - sync: 全設定チャンネルの過去ログを同期\n - cls: ログ表示をクリア")
        
        elif raw_cmd == "restart":
            if messagebox.askyesno("確認", "Botを再起動しますか？"):
                os.execl(sys.executable, sys.executable, *sys.argv)
        
        elif raw_cmd == "shutdown":
            if messagebox.askyesno("確認", "Botを終了しますか？"):
                os._exit(0)
        
        elif raw_cmd == "sync":
            self._append_log("グローバル同期ジョブを開始します...")
            self.bot.loop.create_task(self.bot.global_sync_task())

        elif raw_cmd == "cls":
            self.log_area.configure(state='normal')
            self.log_area.delete('1.0', tk.END)
            self.log_area.configure(state='disabled')
        else:
            self._append_log(f"エラー: 未知のコマンド '{raw_cmd}'")

    def refresh_ui(self):
        """連携チャンネル一覧を最新の状態にする"""
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in self.db.get_all_settings():
            cid = int(row[0])
            channel = self.bot.get_channel(cid)
            # Discord APIから名前を取得（取得できない場合はID表示）
            name = f"{channel.guild.name} / {channel.name}" if channel else f"Unknown ({cid})"
            status = "ON" if row[2] else "OFF"
            self.tree.insert("", "end", values=(name, row[0], row[1], status))

    def update_loop(self):
        """統計とリストを定期更新"""
        if not self.root.winfo_exists(): return
        s = self.db.get_stats()
        self.lbl_stats.config(text=f"📊 統計 | 累計: {s['total']}件  本日: {s['today']}件  待機中: {s['queue']}件")
        self.refresh_ui()
        self.root.after(15000, self.update_loop)

    def run(self):
        self.root.mainloop()