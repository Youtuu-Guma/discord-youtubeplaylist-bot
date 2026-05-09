import re

class YouTubeLinkExtractor:
    # 修正ポイント:
    # 1. youtu\.be\/ を明示的に追加し、短縮URLの誤検知を防ぐ
    # 2. /live/ を追加し、配信URLに対応
    # 3. 肯定の先読み (?=[%#?&]|$) を使い、IDの後のパラメータ（&t=等）を正確に切り離す
    PATTERN = re.compile(r'(?:youtu\.be\/|v=|\/shorts\/|\/live\/|\/)([0-9A-Za-z_-]{11})(?=[%#?&]|$)')

    @staticmethod
    def extract_video_ids(text: str):
        """
        テキスト内からYouTubeの動画ID（11文字）をすべて抽出し、
        重複を除去したリストとして返す。
        """
        if not text:
            return []
        
        # 正規表現にマッチするすべてのIDを抽出
        matches = YouTubeLinkExtractor.PATTERN.findall(text)
        
        # dict.fromkeys() を使って、順序を維持したまま重複を排除
        # (1つのメッセージに同じURLが2回貼られても、処理は1回にするため)
        return list(dict.fromkeys(matches))

# --- 動作テスト用 ---
if __name__ == "__main__":
    test_text = """
    通常: https://www.youtube.com/watch?v=ABC12345678
    短縮: https://youtu.be/ABC12345678
    時間指定: https://www.youtube.com/watch?v=ABC12345678&t=30s
    ショート: https://www.youtube.com/shorts/ABC12345678?feature=share
    ライブ: https://www.youtube.com/live/ABC12345678?si=xxxx
    """
    ids = YouTubeLinkExtractor.extract_video_ids(test_text)
    print(f"抽出されたID: {ids}")