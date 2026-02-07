# Lenovo Tiny 活用プラン: AI専用エンジン構成

**作成日**: 2026-02-07  
**ステータス**: 設計フェーズ

---

## 🎯 基本方針

### Lenovo Tinyの役割
「**眠らないAIマシン**」として、CPU/RAMを使い倒してAI処理とバッチ処理を担当します。

- ✅ **24時間稼働**: 定期クローリング、AI分析を夜間も実行
- ✅ **ローカルLLM**: Ollama (Llama3) を常駐させ、AWS APIコストゼロ
- ✅ **ゼロランニングコスト**: 電気代のみ（月数百円程度）
- ✅ **重い処理専用**: データクローリング、PDF解析、議事録スクレイピング

### AWS Lightsailの役割
「**軽量フロントエンド + 薄いAPI**」として、最小限の費用で外部公開します。

- ✅ **$10/月固定**: これ以上増やさない
- ✅ **静的コンテンツ**: Next.js フロントエンド + API Gatewayのみ
- ✅ **データベースなし**: PostgreSQL/RedisはLenovo Tinyへ
- ✅ **外部アクセス専用**: インターネット経由でのUI提供のみ

---

## 🏗 提案アーキテクチャ (Phase 2)

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Lightsail                        │
│                   (Tokyo Region)                        │
│                                                         │
│  ┌──────────────┐          ┌──────────────┐           │
│  │  Frontend    │          │  Thin API    │           │
│  │  (Next.js)   │◄────────►│  (FastAPI)   │           │
│  │  Port 3000   │          │  Port 8000   │           │
│  └──────────────┘          └───────┬──────┘           │
│                                    │                    │
│                                    │ HTTP API Call      │
└────────────────────────────────────┼────────────────────┘
                                     │
                                     │ Cloudflare Tunnel
                                     │ (またはVPN)
                                     ▼
┌─────────────────────────────────────────────────────────┐
│              Lenovo Tiny (ローカル自宅)                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  AI Engine (Ollama + Llama3)                    │  │
│  │  - ニュース分析 (LLM)                            │  │
│  │  - スコアリング                                   │  │
│  │  - 議事録解析                                     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Data Collection Engine (Node-RED)              │  │
│  │  - 自治体Webクローリング                         │  │
│  │  - J-LIS入札情報収集                             │  │
│  │  - PDF解析                                       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Database Cluster                               │  │
│  │  - PostgreSQL (TimescaleDB)                     │  │
│  │  - Redis Cache                                  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  API Endpoint (Internal)                        │  │
│  │  - FastAPI (完全版)                              │  │
│  │  - Port 8000 (Cloudflare Tunnel経由で公開)      │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

```

---

## 📦 各サービスの配置

### AWS Lightsail ($10/月)
| サービス | 説明 | ポート |
|---------|------|--------|
| **Frontend** | Next.js (本番ビルド) | 3000 |
| **Thin API** | 認証とプロキシのみ | 8000 |

### Lenovo Tiny (電気代のみ)
| サービス | 説明 | ポート | CPU/RAM負荷 |
|---------|------|--------|------------|
| **Ollama** | Llama3 (4GB) | 11434 | 高 |
| **PostgreSQL** | メインDB | 5432 | 中 |
| **Redis** | キャッシュ | 6379 | 低 |
| **FastAPI (Full)** | 全API機能 | 8000 | 中 |
| **Node-RED** | クローリング自動化 | 1880 | 中 |

---

## 🔌 AWS ↔ Lenovo Tiny 接続方法

### オプション1: Cloudflare Tunnel (推奨)
✅ **無料**  
✅ **静的IP不要**  
✅ **DDoS保護**  
✅ **SSL証明書自動**  

**設定手順**:
```bash
# Lenovo Tinyで実行
curl -fsSL https://pkg.cloudflare.com/cloudflared-stable-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
cloudflared tunnel login
cloudflared tunnel create zoom-dx-backend
cloudflared tunnel route dns zoom-dx-backend api.your-domain.com
cloudflared tunnel run zoom-dx-backend
```

### オプション2: ngrok (開発用)
⚠️ 有料プラン推奨 ($8/月)  
✅ 設定が超簡単  

```bash
ngrok http 8000
```

### オプション3: 自宅VPN (OpenVPN)
⚠️ 設定複雑  
✅ 完全コントロール  

---

## 🔄 データフロー

### 1. ニュース収集・分析フロー (毎日深夜3時実行)
```
Node-RED (Lenovo)
  ↓ クローリング
自治体Webサイト
  ↓ 取得したHTML/PDF
Ollama (Lenovo)
  ↓ AI分析
PostgreSQL (Lenovo)
  ↓ 書き込み
完了通知 → Zoom Chat
```

### 2. ユーザーがダッシュボード閲覧
```
ユーザーのブラウザ
  ↓ HTTPS
AWS Frontend (Next.js)
  ↓ API Call (Cloudflare Tunnel経由)
Lenovo FastAPI
  ↓ SELECT
Lenovo PostgreSQL
  ↓ JSON返却
AWS Frontend → ブラウザ表示
```

---

## 💰 コスト比較

| 項目 | 現行 (全AWS) | 提案 (Hybrid) | 削減額 |
|------|-------------|-------------|--------|
| Lightsail | $10/月 | $10/月 | $0 |
| RDS (PostgreSQL) | $15/月 | **削除** | **-$15** |
| ElastiCache (Redis) | $12/月 | **削除** | **-$12** |
| EC2 for AI | $30/月 | **削除** | **-$30** |
| データ転送 | $3/月 | $1/月 | -$2 |
| **合計** | **$70/月** | **$11/月** | **-$59/月** |

**年間削減額**: 約 **$700 (約10万円)**

Lenovo Tiny の電気代（24時間稼働）: 約500円/月
**実質削減額**: 月約6,500円

---

## 🛠 実装ステップ

### Phase 1: Lenovo Tiny セットアップ (Day 1-2)
- [ ] Ubuntu 22.04 LTS インストール
- [ ] Docker & Docker Compose インストール
- [ ] UFW + Fail2ban セキュリティ設定
- [ ] プロジェクトクローン (`/opt/zoom-dx`)

### Phase 2: サービス起動 (Day 3)
- [ ] `docker-compose up -d` (全サービス起動)
- [ ] Ollama モデルダウンロード (`llama3`)
- [ ] データベース初期化 (init.sql実行)
- [ ] 自治体データインポート

### Phase 3: Cloudflare Tunnel設定 (Day 4)
- [ ] Cloudflareアカウント作成
- [ ] Tunnel作成・起動
- [ ] ドメイン設定 (`api.zoom-dx.your-domain.com`)

### Phase 4: AWS側の軽量化 (Day 5)
- [ ] Lightsail の PostgreSQL/Redis コンテナ削除
- [ ] `NEXT_PUBLIC_API_URL` を Cloudflare Tunnel URLへ変更
- [ ] フロントエンド再デプロイ

### Phase 5: 自動化設定 (Day 6-7)
- [ ] Node-RED フロー作成（クローリング）
- [ ] Cron設定 (毎日深夜3時実行)
- [ ] Zoom Chatへの通知設定

---

## 🚨 リスクと対策

| リスク | 対策 |
|--------|------|
| **停電** | UPS導入推奨 (約5,000円) |
| **ネット回線断** | AWS側でモックデータ返却 |
| **Lenovo故障** | 週次でS3バックアップ |
| **セキュリティ** | Cloudflare Tunnelで直接公開しない |

---

## 🎓 学習ポイント

この構成により、以下のスキルが習得できます：
- ✅ **Hybrid Cloud**: オンプレミス + クラウドの組み合わせ
- ✅ **Tunnel技術**: Cloudflare/ngrokの使い方
- ✅ **コスト最適化**: どこをクラウドに置き、どこをローカルにするか
- ✅ **AI運用**: ローカルLLMの性能チューニング

---

**次のアクション**: このプランでGoサインが出たら、Lenovo Tinyのセットアップを開始します！
