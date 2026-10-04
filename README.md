# Discord Bot

使用 [discord.py](https://discordpy.readthedocs.io/) 撰寫的 Discord 機器人。

## 功能

- **成員離開通知**：成員離開伺服器（包含被踢出、被封鎖）時，會在名為 `紀錄` 的文字頻道發送 Embed 通知，內容包含：
  - 頭像與使用者名稱
  - 使用者 ID
  - 帳號建立時間
  - 加入伺服器時間
  - 擁有的身分組
  - 目前伺服器成員數

## 環境需求

- Python 3.8 以上

## 安裝

```bash
# （建議）建立並啟用虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 安裝套件
pip install -r requirements.txt
```

## 設定

### 1. 建立 Discord 應用程式

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)，建立新的 Application
2. 在 **Bot** 頁面取得 Token
3. 在 **Bot** 頁面的 **Privileged Gateway Intents** 開啟：
   - **Server Members Intent**（成員離開通知需要）

### 2. 設定 Token

複製範本並填入你的 Bot Token：

```bash
cp .env.example .env
```

```env
DISCORD_TOKEN=你的 Bot Token
```

> `.env` 已列在 `.gitignore` 中，請勿將 Token commit 進版本控制。

### 3. 邀請 Bot 進伺服器

在 Developer Portal 的 **OAuth2 → URL Generator** 勾選 `bot` scope，並給予以下權限後，用產生的網址邀請 bot：

- View Channels
- Send Messages
- Embed Links

### 4. 建立紀錄頻道

在伺服器中建立名稱為 `紀錄` 的文字頻道，並確認 bot 在該頻道有檢視與發送訊息的權限。

## 執行

```bash
python3 bot.py
```

啟動成功後，終端機會顯示：

```
We have logged in as <Bot 名稱>
```

## 專案結構

```
.
├── bot.py            # Bot 主程式
├── requirements.txt  # Python 套件清單
├── .env.example      # 環境變數範本
└── .gitignore
```
