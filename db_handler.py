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
            cursor.execute('CREATE TABLE IF NOT EXISTS videos (video_id TEXT PRIMARY KEY, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
            cursor.execute('''CREATE TABLE IF NOT EXISTS channel_settings (
                                channel_id TEXT PRIMARY KEY, 
                                playlist_id TEXT, 
                                is_enabled INTEGER DEFAULT 1,
                                allowed_role_id TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS waiting_queue (
                                video_id TEXT, 
                                playlist_id TEXT, 
                                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                PRIMARY KEY (video_id, playlist_id))''')
            conn.commit()

    def _migrate(self):
        """DBの構造が古い場合にカラムを追加する"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(channel_settings)")
                columns = [column[1] for column in cursor.fetchall()]
                if "is_enabled" not in columns:
                    cursor.execute("ALTER TABLE channel_settings ADD COLUMN is_enabled INTEGER DEFAULT 1")
                if "allowed_role_id" not in columns:
                    cursor.execute("ALTER TABLE channel_settings ADD COLUMN allowed_role_id TEXT")
                conn.commit()
        except Exception as e:
            logging.error(f"Migration Error: {e}")

    def is_video_processed(self, video_id):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT 1 FROM videos WHERE video_id = ?', (video_id,)).fetchone() is not None

    def save_video(self, video_id):
        with self._get_connection() as conn:
            conn.cursor().execute('INSERT OR IGNORE INTO videos (video_id) VALUES (?)', (video_id,))

    def get_channel_config(self, channel_id):
        with self._get_connection() as conn:
            res = conn.cursor().execute('SELECT playlist_id, is_enabled, allowed_role_id FROM channel_settings WHERE channel_id = ?', (str(channel_id),)).fetchone()
            return {"playlist_id": res[0], "is_enabled": res[1], "allowed_role_id": res[2]} if res else None

    def set_channel_config(self, channel_id, playlist_id=None, is_enabled=None, role_id=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            curr = self.get_channel_config(channel_id)
            p = playlist_id if playlist_id is not None else (curr["playlist_id"] if curr else "")
            e = is_enabled if is_enabled is not None else (curr["is_enabled"] if curr else 1)
            r = role_id if role_id is not None else (curr["allowed_role_id"] if curr else None)
            cursor.execute('INSERT OR REPLACE INTO channel_settings VALUES (?, ?, ?, ?)', (str(channel_id), p, e, r))

    def get_all_settings(self):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT channel_id, playlist_id, is_enabled, allowed_role_id FROM channel_settings').fetchall()

    def add_to_queue(self, v_id, p_id):
        with self._get_connection() as conn:
            conn.cursor().execute('INSERT OR IGNORE INTO waiting_queue (video_id, playlist_id) VALUES (?, ?)', (v_id, p_id))

    def get_queue(self):
        with self._get_connection() as conn:
            return conn.cursor().execute('SELECT video_id, playlist_id FROM waiting_queue').fetchall()

    def clear_from_queue(self, v_id, p_id):
        with self._get_connection() as conn:
            conn.cursor().execute('DELETE FROM waiting_queue WHERE video_id = ? AND playlist_id = ?', (v_id, p_id))

    def get_stats(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        with self._get_connection() as conn:
            cursor = conn.cursor()
            total = cursor.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
            today_count = cursor.execute('SELECT COUNT(*) FROM videos WHERE date(added_at) = ?', (today,)).fetchone()[0]
            queue = cursor.execute('SELECT COUNT(*) FROM waiting_queue').fetchone()[0]
            return {"total": total, "today": today_count, "queue": queue}