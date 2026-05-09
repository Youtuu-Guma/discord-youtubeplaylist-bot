# YouTube Playlist Auto-Saver Bot

Discord上のメッセージからYouTubeリンクを自動検出し、指定したYouTube再生リストへ自動保存するDiscord Botです。

## 🌟 主な機能

- **リンク自動抽出**: メッセージ内のYouTube URL（通常、短縮、Shorts、Live）を自動判別して抽出します。
- **重複防止機能**: SQLiteデータベースにより、一度保存した動画の重複追加を防止します。
- **クォータ（API制限）対策**: YouTube APIの制限に達した場合、自動的に待機キューへ保存し、後ほど再試行します。
- **GUIダッシュボード**: Tkinterによる統計確認、連携チャンネル管理、およびコマンド操作が可能です。

## 🤖 開発背景と免責事項

本プロジェクトは、**GoogleのAI「Gemini」およびAnthropicのAI「Claude」を使用して作成されました。**

AIにすべてのコードを記述させています。私自身の手によるコードの修正は行っていません。

> [!WARNING]
> **免責事項** > 本プログラムはAIが生成したコードで構成されているため、予期せぬ動作をする可能性があります。本ソフトの使用によって生じた損害等について、開発者は一切の責任を負いません。

## 🛠 開発環境
- **Language:** Python 3.10+
- **Main Libraries:** `discord.py`, `google-api-python-client`, `tkinter`
- **Database:** SQLite3

---

## 🚀 導入・利用方法

### 1. 事前準備
実行前に以下の3点を用意してください。

1.  **Discord Bot Token**
    - [Discord Developer Portal](https://discord.com/developers/applications/)でBotを作成し、Tokenを取得してください。
    - ※Tokenは絶対に他人に教えないでください。
2.  **Google Cloud APIキー (JSONファイル)**
    - [Google Cloud Console](https://console.cloud.google.com/)にアクセスし、YouTube Data API v3を有効にして「OAuth 2.0 クライアント ID」を作成し、JSONファイルをダウンロードしてください。
3.  **自身のDiscordユーザーID**
    - Discordの設定で「開発者モード」をONにし、自分のアイコンを右クリックして「ユーザーIDをコピー」してください。

### 2. インストールと起動手順
1.  [Releases](https://github.com/あなたのユーザー名/リポジトリ名/releases)から最新の `.zip` ファイルをダウンロードし、解凍してください。
2.  解凍したフォルダ一式を、任意の場所（ドキュメントフォルダなど）へ移動させることをお勧めします。
3.  **解凍したフォルダ内（.exeファイルと同じ階層）に、準備した `.json` ファイルを配置してください。**
4.  `.exe` ファイルを起動します。
5.  設定画面が表示されるので、**Botトークン** と **Discord ID** を入力してください。

---

## 📝 ライセンス
このプロジェクトは [MIT License](LICENSE) の下で公開されています。

---
*Developed with Gemini & Claude - An AI-Human Collaboration Project.*
