# YouTube Playlist Auto-Saver Bot

Discord上のメッセージからYouTubeリンクを自動検出し、指定したYouTube再生リストへ自動保存するDiscord Botです。

## 🌟 主な機能

- **リンク自動抽出**: メッセージ内のYouTube URL（通常、短縮、Shorts、Live）を自動判別して抽出します。
- **重複防止機能**: SQLiteデータベースにより、一度保存した動画の重複追加を防止します。
- **クォータ（API制限）対策**: YouTube APIの制限に達した場合、自動的に待機キューへ保存し、後ほど再試行します。
- **GUIダッシュボード**: Tkinterによる統計確認、連携チャンネル管理、およびコマンド操作が可能です。
- **初期設定ウィザード**: 初回起動時にトークン等を入力するだけで、設定ファイルを手動で書き換える必要なく利用を開始できます。

## 🤖 開発背景と免責事項

本プロジェクトは、**GoogleのAI「Gemini」およびAnthropicのAI「Claude」を使用して作成されました。**

AIにすべてのコードを記述させています。私自身の手によるコードの修正は行っていません。

> [!WARNING]
> **免責事項**
> 本プログラムはAIが生成したコードで構成されているため、予期せぬ動作をする可能性があります。本ソフトの使用によって生じた損害等について、開発者は一切の責任を負いません。

## 🛠 開発環境
- **Language:** Python 3.10+
- **Main Libraries:** `discord.py`, `google-api-python-client`, `tkinter`
- **Database:** SQLite3

---

## 🚀 導入・利用方法

### 1. 事前準備
実行前に以下の3点を用意してください。

1. **Discord Bot Token**
    - [Discord Developer Portal](https://discord.com/developers/applications/)でBotを作成し、Tokenを取得してください。
    - **Privileged Gateway Intents** セクションで「MESSAGE CONTENT INTENT」を必ず **ON** にしてください。
2. **Google Cloud APIキー (JSONファイル)**
    - [Google Cloud Console](https://console.cloud.google.com/)でYouTube Data API v3を有効にし、「OAuth 2.0 クライアント ID」を作成してJSONファイルをダウンロードしてください。
3. **自身のDiscordユーザーID**
    - Discordの「開発者モード」をONにし、自分のアイコンを右クリックして「ユーザーIDをコピー」してください。

### 2. インストールと起動手順
1. [Releases] から最新の `.zip`ファイルをダウンロードし、解凍してください。
2. 解凍したフォルダ内に、準備した `.json` ファイル（client_secret...）を配置してください。
3. `.exe` ファイルを起動します。
4. 初回のみ設定画面が表示されるので、**Botトークン** と **Discord ID** を入力してください。
5. Googleの認証ブラウザが開くので、使用するアカウントでログインし、アクセスを許可してください。

---

## 📖 使い方（Discord上での操作）

Botをサーバーに招待した後、以下の手順で保存先を設定します。

### チャンネルと再生リストの連携
保存したいチャンネルで、以下のコマンドを入力します。
/set_playlist playlist_url:[再生リストのURL]

- これにより、そのチャンネルに貼られたYouTubeリンクが自動的に指定した再生リストへ保存されるようになります。

### その他のコマンド
- `/sync`: チャンネルの過去のメッセージを遡り、未保存の動画を一括保存します。
- `/toggle`: そのチャンネルでの自動保存機能の有効/無効を切り替えます。

---

## 🛡️ 推奨されるBot権限
Botが正常に動作するために、サーバー招待時に以下の権限を付与してください。

- チャンネルを見る (View Channels)
- メッセージを送信 (Send Messages)
- メッセージ履歴を読む (Read Message History)
- スラッシュコマンドの使用 (Use Slash Commands)

---

## 📝 ライセンス
このプロジェクトは [MIT License](LICENSE) の下で公開されています。

---
*Developed with Gemini & Claude - An AI-Human Collaboration Project.*
