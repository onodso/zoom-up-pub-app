# 📊 Lenovo Tiny AI Engine セットアップ完了報告

**作成日時:** 2026-02-08  
**実施者:** Antigravity AI Agent  
**対象デバイス:** Lenovo Tiny (Windows 11)  
**プロジェクト:** Zoom UP Public App - Local Gov DX Intelligence

---

## 🎯 目的

AWS Lightsail のコスト削減のため、重い AI 処理（Ollama / LLM推論）をローカルデバイス（Lenovo Tiny）に移行し、ハイブリッドクラウドアーキテクチャを実現する。

---

## ✅ 実施内容

### 1. **環境構築**
| 項目 | 詳細 | ステータス |
|------|------|----------|
| OS | Windows 11 | ✅ |
| Docker | Docker Desktop 29.2.0 | ✅ |
| WSL2 | メモリ8GB割り当て (.wslconfig設定) | ✅ |
| Tailscale | MacとLenovo Tiny間の接続 (100.107.246.40) | ✅ |

### 2. **AI Engine（Ollama）**
| 項目 | 詳細 | ステータス |
|------|------|----------|
| Ollama (Windows版) | v0.15.4 ネイティブインストール | ✅ |
| AI Model | Llama3.2:1b (1.3GB、軽量版) | ✅ |
| 動作確認 | 日本語推論テスト成功 | ✅ |

### 3. **Dockerコンテナ群**
| サービス | イメージ | ポート | ステータス |
|---------|----------|--------|----------|
| **FastAPI** | zoom-dx-app-api (自作) | 8000 | ✅ Running |
| **PostgreSQL** | timescale/timescaledb:latest-pg16 | 5432 | ✅ Healthy |
| **Redis** | redis:7.2-alpine | 6379 | ✅ Healthy |
| **Ollama (Docker)** | ollama/ollama:latest | 11434 | ✅ Running |
| **Node-RED** | nodered/node-red:latest | 1880 | ✅ Running |

> **補足**: Ollamaは**Docker版**と**Windows Native版**の両方がインストールされています。
> - **Docker版 (ollama:11434)**: docker-compose経由で起動
> - **Windows版 (ollama)**: コマンドラインから直接実行可能

### 4. **データベースセットアップ**
```bash
# 11テーブル正常作成
postgres=> \dt
               List of relations
 Schema |      Name       | Type  |   Owner
--------+-----------------+-------+------------
 public | access_logs     | table | zoom_admin
 public | ai_analyses     | table | zoom_admin
 public | batch_logs      | table | zoom_admin
 public | budgets         | table | zoom_admin
 public | error_logs      | table | zoom_admin
 public | municipalities  | table | zoom_admin
 public | news_statements | table | zoom_admin
 public | playbooks       | table | zoom_admin
 public | scores          | table | zoom_admin
 public | tenders         | table | zoom_admin
 public | users           | table | zoom_admin
```

### 5. **接続確認（Tailscale経由）**

**Mac側からのアクセステスト:**
```bash
# Mac Terminal
curl http://100.107.246.40:8000/docs
# Result: ✅ Swagger UI HTML正常受信
```

**Swagger UI エンドポイント確認:**
- 認証: `/api/auth/login`, `/api/auth/me`
- 自治体: `/api/municipalities/`, `/api/municipalities/{code}`, `/api/municipalities/regions/list`

---

## 🏗️ アーキテクチャ図

```
┌────────────────────────────┐      Tailscale VPN       ┌────────────────────────────┐
│     Mac (開発環境)          │◄──────────────────────►│   Lenovo Tiny (AI Engine)  │
│                            │     100.107.246.40       │                            │
│  ┌──────────────────────┐  │                          │  ┌──────────────────────┐  │
│  │  Next.js Frontend    │  │                          │  │  Docker Containers   │  │
│  │  localhost:3000      │──┼─────── API Call ────────►│  │  ┌────────────────┐  │  │
│  └──────────────────────┘  │                          │  │  │ FastAPI :8000  │  │  │
│                            │                          │  │  ├────────────────┤  │  │
│  ┌──────────────────────┐  │                          │  │  │ Postgres :5432 │  │  │
│  │  開発ツール           │  │                          │  │  ├────────────────┤  │  │
│  │  - Antigravity       │  │                          │  │  │ Redis :6379    │  │  │
│  │  - Claude Code       │  │                          │  │  ├────────────────┤  │  │
│  └──────────────────────┘  │                          │  │  │ Ollama :11434  │  │  │
│                            │                          │  │  ├────────────────┤  │  │
└────────────────────────────┘                          │  │  │ Node-RED :1880 │  │  │
                                                        │  │  └────────────────┘  │  │
                                                        │  └──────────────────────┘  │
                                                        │                            │
                                                        │  ┌──────────────────────┐  │
                                                        │  │ Ollama (Windows版)   │  │
                                                        │  │ - Llama3.2:1b (1.3GB)│  │
                                                        │  │ - Llama3 (4.7GB) DL済│  │
                                                        │  └──────────────────────┘  │
                                                        └────────────────────────────┘
```

### Mermaid Diagram

```mermaid
graph LR
    subgraph Mac [Mac (開発環境)]
        FE[Next.js Frontend<br>localhost:3000]
        Dev[開発ツール<br>Antigravity / Claude Code]
    end

    subgraph Network [Tailscale VPN (100.107.246.40)]
        FE -- API Request --> API
        Dev -- SSH / Docker --> Lenovo
    end

    subgraph Lenovo [Lenovo Tiny (AI Engine)]
        subgraph Docker [Docker Containers]
            API[FastAPI :8000]
            DB[(Postgres :5432)]
            Redis[(Redis :6379)]
            OllamaD[Ollama :11434]
            NodeRED[Node-RED :1880]
        end
        OllamaW[Ollama (Windows Native)<br>Llama3.2:1b]
    end

    API --> DB
    API --> Redis
    API --> OllamaD
    NodeRED -.-> API
```

---

## 📈 成果とメリット

### コスト削減効果（試算）
| 項目 | AWS Lightsail | Lenovo Tiny | 削減額/月 |
|------|---------------|-------------|-----------|
| Ollama (AI推論) | $20/月 | 電気代 ~$3/月 | **$17** |
| PostgreSQL (大量データ) | $10/月 | 電気代込み | **$10** |
| **合計** | $30/月 | ~$3/月 | **$27/月** |

> **電気代試算**: Lenovo Tiny (35W) × 24h × 30日 = 25.2kWh ≈ ¥700/月 (~$5)
> ただし常時稼働でない場合は更に低くなる

**年間削減額**: **$324 (約45,000円)**

### 技術的メリット
1. **低レイテンシ**: Mac↔Lenovo TinyはTailscaleで直接通信（AWS経由不要）
2. **スケーラビリティ**: Lenovo Tinyの16GB RAMを最大活用可能
3. **データプライバシー**: 自治体データをローカル処理（クラウド非送信）

---

## 🚧 今後のタスク

### Phase 6: AWS↔Lenovo Tiny 連携
- [ ] Cloudflare Tunnel セットアップ
- [ ] AWS Lightsail → Lenovo Tiny へのワークロード移行
- [ ] 自動クローリング & AI分析（Daily Cron）

### Phase 7: 運用監視
- [ ] Lenovo Tiny ヘルスチェック
- [ ] ログ監視（Sentry / CloudWatch）
- [ ] バックアップ戦略（DB スナップショット）

---

## 📝 トラブルシューティング記録

### 発生した問題と解決策

#### 1. Docker Desktop起動失敗（WSL2メモリ不足）
**症状**: `model requires more system memory (4.6 GiB) than is available (2.0 GiB)`

**原因**: Docker DesktopのWSL2デフォルトメモリ割り当てが2GBだった

**解決策**:
```powershell
# C:\Users\onodera\.wslconfig ファイル作成
[wsl2]
memory=8GB
processors=4
swap=4GB
localhostForwarding=true

# WSL再起動
wsl --shutdown
```

#### 2. Llama3モデルのサイズ問題
**症状**: Full Llama3モデル（4.7GB）がメモリ不足で動作しない

**解決策**: 軽量版 `Llama3.2:1b` (1.3GB) に変更
```powershell
ollama pull llama3.2:1b
ollama run llama3.2:1b "テスト"
```

#### 3. Node-REDポート競合
**症状**: `port 1880 already allocated`

**解決策**: 競合プロセス（Docker関連）を停止
```powershell
taskkill /PID 11804 /F
taskkill /PID 12640 /F
```

---

## 🔗 関連リソース

- **GitHubリポジトリ**: [https://github.com/onodso/zoom-up-pub-app](https://github.com/onodso/zoom-up-pub-app)
- **Swagger UI (Lenovo Tiny)**: http://100.107.246.40:8000/docs
- **AWS Lightsail Dashboard**: https://lightsail.aws.amazon.com/
- **Tailscale Admin**: https://login.tailscale.com/admin/machines

---

## ✅ セットアップ完了チェックリスト

- [x] Docker Desktop インストール・起動
- [x] WSL2 メモリ設定（8GB）
- [x] Ollama (Windows版) インストール
- [x] Llama3.2:1b モデルダウンロード
- [x] docker-compose.lenovo.yml 実行
- [x] PostgreSQL テーブル作成確認
- [x] Swagger UI 動作確認
- [x] Tailscale接続確認（Mac→Lenovo Tiny）
- [x] API エンドポイントテスト

---

**担当者サイン**: Antigravity AI Agent  
**承認者**: N/A  
**次回確認日**: 2026-02-15（1週間後）
