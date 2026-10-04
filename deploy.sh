#!/usr/bin/env bash
# 從本機部署 bot 到伺服器並重啟
# 用法：./deploy.sh
set -euo pipefail

HOST="Contact_system"
BRANCH="main"

cd "$(dirname "$0")"

# 伺服器從 GitHub 拉程式碼，所以本機的 commit 必須先 push
if [ -n "$(git status --porcelain)" ]; then
  echo "⚠️  有未 commit 的變更，這些變更不會被部署"
fi
git fetch -q origin "$BRANCH"
if [ "$(git rev-parse HEAD)" != "$(git rev-parse "origin/$BRANCH")" ]; then
  echo "❌ 本機 HEAD 與 origin/$BRANCH 不一致，請先 push 或切到 $BRANCH" >&2
  exit 1
fi

echo "🚀 部署 $(git rev-parse --short HEAD) 到 $HOST"

# 以本機 .env 為準，上傳到伺服器（權限 600，只有 deploy 帳號能讀）
if [ -f .env ]; then
  echo "🔑 上傳 .env"
  ssh "$HOST" 'umask 077 && cat > "$HOME/.discord-bot.env.upload"' < .env
fi

ssh "$HOST" "bash -s" <<'REMOTE'
set -euo pipefail

APP_DIR="$HOME/discord-bot"
REPO_URL="https://github.com/HEROGWP/discord-bot.git"
BRANCH="main"
SESSION="discord-bot"
PYTHON_VERSION="3.12"

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "📦 安裝 uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if [ ! -d "$APP_DIR/.git" ]; then
  echo "📥 clone $REPO_URL"
  git clone -q "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
echo "📥 更新程式碼"
git fetch -q origin "$BRANCH"
git checkout -q "$BRANCH"
git pull -q --ff-only origin "$BRANCH"

echo "🐍 安裝套件"
[ -d .venv ] || uv venv -q --python "$PYTHON_VERSION"
uv pip install -q -r requirements.txt

if [ -f "$HOME/.discord-bot.env.upload" ]; then
  mv "$HOME/.discord-bot.env.upload" .env
  chmod 600 .env
fi
if [ ! -f .env ]; then
  echo "❌ 找不到 $APP_DIR/.env，請在本機建立 .env 後重新部署" >&2
  exit 1
fi

# 主機重開後自動啟動（只更新本專案這一行，不影響其他 crontab）
CRON_LINE="@reboot screen -dmS $SESSION $APP_DIR/run.sh"
{ crontab -l 2>/dev/null | grep -vF "$APP_DIR/run.sh" || true; echo "$CRON_LINE"; } | crontab -

echo "🔄 重啟 bot"
screen -S "$SESSION" -X quit >/dev/null 2>&1 || true
screen -dmS "$SESSION" "$APP_DIR/run.sh"

sleep 5
if screen -list | grep -q "\.$SESSION"; then
  echo "✅ bot 已在 screen session「$SESSION」中執行，最新 log："
else
  echo "❌ screen session 沒有啟動，最新 log：" >&2
fi
tail -n 5 bot.log 2>/dev/null || true
REMOTE
