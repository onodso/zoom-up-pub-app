# Lenovo Tiny セットアップガイド

**対象**: Lenovo Tiny (または任意のローカルPC)  
**OS**: Ubuntu 22.04 LTS  
**役割**: AI専用エンジン + データベース + クローリング  
**予算**: 電気代のみ（月500円程度）

---

## 📋 事前準備

### 必要なもの
- ✅ Lenovo Tiny本体（または任意のPC、最低2GB RAM推奨）
- ✅ 有線LAN接続（安定性重視）
- ✅ USBメモリ（Ubuntu起動ディスク作成用）

### 推奨スペック
- **CPU**: 2コア以上
- **RAM**: 4GB以上（Ollamaは最低2GB必要）
- **SSD**: 60GB以上

---

## 🚀 Phase 1: OS インストール

### 1-1. Ubuntu 22.04 LTS のダウンロード
MacまたはWindows PCで実施：
```bash
# Ubuntu公式サイトからISOをダウンロード
https://ubuntu.com/download/server

# balenaEtcherでUSBメモリに書き込み
https://etcher.balena.io/
```

### 1-2. Lenovo TinyへUbuntuをインストール
1. USBメモリを挿してLenovo Tinyを起動
2. BIOS設定でUSBブートを最優先に
3. Ubuntuインストーラーに従って進める
   - **言語**: 日本語
   - **タイムゾーン**: Asia/Tokyo
   - **ユーザー名**: `ubuntu`（推奨）
   - **パスワード**: 強力なパスワード設定
   - **OpenSSH Server**: ✅ インストールする

### 1-3. 初回起動・ネットワーク確認
```bash
# インストール完了後、再起動してログイン
ubuntu@lenovo-tiny:~$ 

# IPアドレス確認
ip addr show

# インターネット接続確認
ping -c 3 google.com
```

---

## 🔐 Phase 2: セキュリティ設定

### 2-1. システムアップデート
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 2-2. UFW ファイアウォール設定
```bash
# UFWインストール
sudo apt install ufw -y

# デフォルトポリシー（内向き拒否、外向き許可）
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH許可（リモートアクセス用）
sudo ufw allow 22/tcp

# ファイアウォール有効化
sudo ufw enable
sudo ufw status
```

### 2-3. Fail2ban インストール
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🐳 Phase 3: Docker環境構築

### 3-1. Docker インストール
```bash
# 古いバージョン削除
sudo apt remove docker docker-engine docker.io containerd runc

# 依存関係インストール
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker公式GPGキー追加
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Dockerリポジトリ追加
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerインストール
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# ユーザーをdockerグループに追加（sudo不要にする）
sudo usermod -aG docker $USER

# ログアウト→再ログインして反映
exit
# SSHで再接続

# Docker動作確認
docker --version
docker compose version
docker run hello-world
```

---

## 📦 Phase 4: プロジェクトセットアップ

### 4-1. プロジェクトディレクトリ作成
```bash
# 作業ディレクトリ作成
sudo mkdir -p /opt/zoom-dx
sudo chown -R ubuntu:ubuntu /opt/zoom-dx
cd /opt/zoom-dx
```

### 4-2. GitHubからクローン
```bash
# Gitインストール
sudo apt install git -y

# プロジェクトクローン
git clone https://github.com/onodso/zoom-up-pub-app.git .

# ブランチ確認
git branch
git status
```

### 4-3. 環境変数設定（.env）
```bash
# Lenovo Tiny専用の.envファイルを作成
cp .env.example .env.lenovo
nano .env.lenovo
```

**重要な設定項目**:
```bash
# Database (Lenovo Tiny内部)
POSTGRES_HOST=postgres
POSTGRES_USER=zoom_admin
POSTGRES_PASSWORD=【強力なパスワード64文字】
POSTGRES_DB=zoom_dx_db

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=【強力なシークレット64文字】
JWT_ALGORITHM=HS256

# Ollama (同じDockerネットワーク内)
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3

# Google Search API
GOOGLE_SEARCH_API_KEY=【実際のAPIキー】
GOOGLE_SEARCH_ENGINE_ID=【実際のエンジンID】

# Node-RED
TZ=Asia/Tokyo

# Production Mode
NODE_ENV=production
LOG_LEVEL=INFO
```

---

## 🎯 Phase 5: サービス起動

### 5-1. Lenovo Tiny用 docker-compose.yml
```bash
# Lenovo Tiny専用構成ファイルを使用
cd /opt/zoom-dx
docker compose -f docker-compose.lenovo.yml up -d
```

### 5-2. 起動確認
```bash
# コンテナ状態確認
docker compose -f docker-compose.lenovo.yml ps

# ログ確認
docker compose -f docker-compose.lenovo.yml logs -f api
docker compose -f docker-compose.lenovo.yml logs -f ollama
```

### 5-3. Ollamaモデルダウンロード
```bash
# コンテナ内でLlama3モデルをダウンロード（約4GB）
docker exec -it zoom-dx-ollama ollama pull llama3

# 動作確認
docker exec -it zoom-dx-ollama ollama run llama3 "こんにちは"
```

### 5-4. データベース初期化
```bash
# PostgreSQLコンテナへ接続
docker exec -it zoom-dx-postgres psql -U zoom_admin -d zoom_dx_db

# テーブル確認
\dt

# 終了
\q
```

### 5-5. 自治体データインポート
```bash
# インポートスクリプト実行
docker exec -it zoom-dx-api python /app/import_mp.py

# データ確認
docker exec -it zoom-dx-postgres psql -U zoom_admin -d zoom_dx_db -c "SELECT COUNT(*) FROM municipalities;"
```

---

## 🌐 Phase 6: Tailscale VPN設定

### 6-1. Tailscaleインストール（Lenovo Tiny側）
```bash
# Tailscale公式リポジトリ追加
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noexpand.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

# Tailscaleインストール
sudo apt update
sudo apt install tailscale -y

# バージョン確認
tailscale version
```

### 6-2. Tailscale起動・認証
```bash
# Tailscale起動（ブラウザで認証画面が開く）
sudo tailscale up

# 表示されたURLをMacのブラウザで開いて認証
# Googleアカウントでログイン推奨（無料）
```

### 6-3. Lenovo TinyのIPアドレス確認
```bash
# TailscaleネットワークでのIPアドレス確認
tailscale ip -4

# 例: 100.x.x.x のようなIPが表示される
```

### 6-4. AWS Lightsail側にもTailscaleインストール
```bash
# SSHでAWS Lightsailに接続
ssh -i ~/.ssh/zoom-dx-prod.pem ubuntu@54.150.207.122

# Lenovo Tinyと同じ手順でインストール
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noexpand.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update
sudo apt install tailscale -y

# 起動・認証（同じアカウントでログイン）
sudo tailscale up
```

### 6-5. 接続確認
```bash
# AWS LightsailからLenovo TinyのAPIにアクセス
curl http://100.x.x.x:8000/health

# レスポンス例
# {"status":"ok","version":"1.0.0"}

# Lenovo TinyからAWSへもping確認
ping -c 3 100.y.y.y
```

### 6-6. Mac（開発マシン）にもTailscaleインストール（オプション）
```bash
# Macでも同じネットワークに参加可能
# https://tailscale.com/download/mac からダウンロード
# またはHomebrewで:
brew install tailscale

# 起動
sudo tailscaled install-system-daemon
tailscale up
```

### 6-7. Tailscale設定のベストプラクティス
```bash
# Lenovo Tinyに固定的な名前を付ける
sudo tailscale set --hostname lenovo-ai-engine

# AWS Lightsailにも名前を付ける
sudo tailscale set --hostname aws-frontend

# 名前でアクセス可能に
# 例: curl http://lenovo-ai-engine:8000/health
```

---

## ✅ Phase 7: 動作確認

### 7-1. ローカルAPI確認
```bash
# Lenovo Tiny内部からAPIにアクセス
curl http://localhost:8000/health

# 期待される結果
# {"status":"ok","version":"1.0.0"}
```

### 7-2. 外部からのアクセス確認
別PCのブラウザで以下にアクセス：
```
https://api.your-domain.com/docs
```
→ FastAPI Swagger UIが表示されればOK

### 7-3. AI分析テスト
```bash
# ニュース収集・分析実行
curl -X POST http://localhost:8000/api/collector/run

# 結果確認（スコアが付与されているか）
```

---

## 🔄 Phase 8: 定期実行設定

### 8-1. Cronジョブ設定
```bash
# Crontab編集
crontab -e

# 毎日深夜3時にニュース収集実行
0 3 * * * curl -X POST http://localhost:8000/api/collector/run >> /opt/zoom-dx/logs/cron.log 2>&1
```

---

## 🛠 トラブルシューティング

### Docker起動しない
```bash
sudo systemctl status docker
sudo systemctl restart docker
```

### Ollamaがメモリ不足
```bash
# メモリ使用量確認
free -h

# 不要なコンテナ停止
docker compose -f docker-compose.lenovo.yml stop frontend
```

### Cloudflare Tunnel接続エラー
```bash
# ログ確認
sudo journalctl -u cloudflared -f

# 再起動
sudo systemctl restart cloudflared
```

---

## 📊 次のステップ

1. ✅ AWS Lightsailのフロントエンドから `NEXT_PUBLIC_API_URL=https://api.your-domain.com` に変更
2. ✅ Node-REDフロー作成（自動クローリング）
3. ✅ Zoom Chat通知設定

---

**完成イメージ**: Lenovo Tinyが24時間稼働し、毎日深夜3時に全国の自治体サイトをクローリング→AI分析→スコアリング→データベース更新を自動実行！
