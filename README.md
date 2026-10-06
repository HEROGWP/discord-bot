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
- **每週試算表截圖**：每週 20:00（台灣時間）把 城戰隊伍試算表 的指定範圍截圖發到 `紀錄` 頻道：
  - 週四：`A31:P62` 週四城戰隊伍攻城表
  - 週日：`R31:AG62` 週日決戰隊伍表

  排程設定在 `bot.py` 的 `WEEKLY_SNAPSHOTS`，試算表 ID 設定在 `.env` 的 `SHEET_ID`。試算表需設為「知道連結的任何人都能檢視」。執行 `python3 sheet_snapshot.py R31:AG62` 可在本機產生 `sheet.png` 預覽

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
SHEET_ID=試算表 ID（網址 /d/ 與 /edit 之間那段）
```

> `.env` 已列在 `.gitignore` 中，請勿將 Token commit 進版本控制。

### 3. 邀請 Bot 進伺服器

在 Developer Portal 的 **OAuth2 → URL Generator** 勾選 `bot` scope，並給予以下權限後，用產生的網址邀請 bot：

- View Channels
- Send Messages
- Embed Links
- Attach Files（每週試算表截圖需要）

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

## 部署

伺服器設定在 `~/.ssh/config` 的 `Contact_system`。在本機執行：

```bash
./deploy.sh
```

腳本會：

1. 確認本機 commit 已 push 到 GitHub（伺服器從 GitHub 拉程式碼）
2. 把本機的 `.env` 上傳到伺服器
3. 在伺服器上 `git pull`、用 [uv](https://docs.astral.sh/uv/) 安裝 Python 3.12 與套件（第一次會自動 clone 與安裝 uv）
4. 在 `screen` session `discord-bot` 中重啟 bot（`run.sh` 會在 bot 結束時自動重啟）
5. 設定 crontab `@reboot`，主機重開後自動啟動

在伺服器上查看狀態：

```bash
tail -f ~/discord-bot/bot.log   # 查看 log
screen -r discord-bot           # 進入 bot 畫面（Ctrl+A 再按 D 離開）
```

## 專案結構

```
.
├── bot.py            # Bot 主程式
├── sheet_snapshot.py # 試算表範圍截圖
├── deploy.sh         # 從本機部署到伺服器
├── run.sh            # 伺服器上執行 bot（自動重啟）
├── requirements.txt  # Python 套件清單
├── .env.example      # 環境變數範本
└── .gitignore
```
