YouTube Playlist Auto-Saver Bot
Discord上のメッセージからYouTubeリンクを自動検出し、指定したYouTube再生リストへ保存するDiscord Botです。

メッセージ内のYouTube URL（通常、短縮、Shorts、Live）を自動で判別。
データベース(SQLite)により、一度保存した動画の重複追加を防止。
YouTube APIの制限（Quota）に達した場合、自動的に待機キューへ保存し、後ほど再試行します。
GUI（Tkinter）による統計確認、連携チャンネル管理、およびコマンド操作。

# 本プロジェクトは「Gemini」,「Claude」を使用して作られました。
プログラミング初心者の私が、学習の一環としてAIを使用し、AIにすべてのコードを書かせたものです。コード自体に私自身の手は加わっていません。
免責事項として明記しておきますが、「AIが生成したコードなため、、予期せぬ動作をする可能性があります」
- **Language:** Python 3.10+
- **Main Libraries:** `discord.py`, `google-api-python-client`, `tkinter`
- **Database:** SQLite3
