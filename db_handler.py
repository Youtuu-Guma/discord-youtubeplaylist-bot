import sqlite3
import logging
import datetime

class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()
        self._migrate()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 完了済み動画
            cursor.execute('CREATE TABLE IF NOT EXISTS videos (video_id TEXT PRIMARY KEY, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
            # チャンネル設定 (初期構造)
            cursor.execute('CREATE TABLE IF NOT EXISTS channel_settings (channel_id TEXT PRIMARY KEY, playlist_id TEXT)')
            # 待機キュー
            cursor.execute('''CREATE TABLE IF NOT EXISTS waiting_queue (
                                video_id TEXT, playlist_id TEXT, 
                                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                PRIMARY KEY (video_id, playlist_id))''')
            conn.commit()

    def _migrate(self):
        """カラムの追加など、DBの構造変更を安全に行う"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(channel_settings)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_enabled' not in columns:
                cursor.execute("ALTER TABLE channel_settings ADD COLUMN is_enabled INTEGER DEFAULT 1")
                logging.info("DB Migration: 'is_enabled' カラムを追加しました。")
            if 'allowed_role_id' not in columns:
                cursor.execute("ALTER TABLE channel_settings ADD COLUMN allowed_role_id TEXT DEFAULT NULL")
                logging.info("DB Migration: 'allowed_role_id' カラムを追加しました。")
            conn.commit()

    # 設定の取得・更新
    def set_channel_config(self, channel_id, playlist_id=None, is_enabled=None, role_id=None):
        with self._get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute("SELECT playlist_id, is_enabled, allowed_role_id FROM channel_settings WHERE channel_id=?", (str(channel_id),)).fetchone()
            
            p = playlist_id if playlist_id is not None else (res[0] if res else "")
            e = is_enabled if is_enabled is not None else (res[1] if res else 1)
            r = role_id if role_id is not None else (res[2] if res else None)
            
            cur.execute("INSERT OR REPLACE INTO channel_settings VALUES (?, ?, ?, ?)", (str(channel_id), p, e, r))

    def get_channel_config(self, channel_id):
        with self._get_connection() as conn:
            res = conn.cursor().execute('SELECT playlist_id, is_enabled, allowed_role_id FROM channel_settings WHERE channel_id = ?', (str(channel_id),)).fetchone()
            if res:
                return {"playlist_id": res[0], "is_enabled": bool(res[1]), "allowed_role_id": res[2]}
            return None

    # GUI用データ取得
    def get_all_settings(self):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT channel_id, playlist_id, is_enabled FROM channel_settings').fetchall()

    def get_stats(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            cur = conn.cursor()
            return {
                "total": cur.execute('SELECT COUNT(*) FROM videos').fetchone()[0],
                "today": cur.execute('SELECT COUNT(*) FROM videos WHERE date(added_at) = ?', (today,)).fetchone()[0],
                "queue": cur.execute('SELECT COUNT(*) FROM waiting_queue').fetchone()[0]
            }

    def get_recent_history(self, limit=10):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT video_id, added_at FROM videos ORDER BY added_at DESC LIMIT ?', (limit,)).fetchall()

    # 動画・キュー操作
    def is_video_processed(self, video_id):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT 1 FROM videos WHERE video_id = ?', (video_id,)).fetchone() is not None

    def save_video(self, video_id):
        with self._get_connection() as conn:
            conn.cursor().execute('INSERT OR IGNORE INTO videos (video_id) VALUES (?)', (video_id,))

    def add_to_queue(self, video_id, playlist_id):
        with self._get_connection() as conn:
            conn.cursor().execute('INSERT OR IGNORE INTO waiting_queue (video_id, playlist_id) VALUES (?, ?)', (video_id, playlist_id))

    def get_queue(self):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT video_id, playlist_id FROM waiting_queue').fetchall()

    def clear_from_queue(self, video_id, playlist_id):
        with self._get_connection() as conn:
            conn.cursor().execute('DELETE FROM waiting_queue WHERE video_id = ? AND playlist_id = ?', (video_id, playlist_id))

    def delete_setting(self, channel_id):
        with self._get_connection() as conn:
            conn.cursor().execute('DELETE FROM channel_settings WHERE channel_id = ?', (str(channel_id),))