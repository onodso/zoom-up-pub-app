# Zoom製品群 完全機能ガイド

**更新日**: 2026年2月13日  
**対象**: Antigravity IDE開発チーム  
**目的**: すべてのZoom製品の機能を網羅的に整理し、自治体向け営業戦略と開発に活用する

---

## 📋 目次

1. [エグゼクティブサマリー](#executive-summary)
2. [Zoom Workplace - 統合プラットフォーム](#zoom-workplace)
3. [コミュニケーション製品](#communication-products)
   - [Zoom Meetings](#zoom-meetings)
   - [Zoom Phone](#zoom-phone)
   - [Zoom Team Chat](#zoom-team-chat)
   - [Zoom Webinars](#zoom-webinars)
   - [Zoom Events](#zoom-events)
4. [AI機能群](#ai-features)
   - [AI Companion (AIC)](#ai-companion)
   - [AI Concierge](#ai-concierge)
   - [Zoom Revenue Accelerator (ZRA)](#zoom-revenue-accelerator)
5. [生産性ツール](#productivity-tools)
   - [Zoom Docs](#zoom-docs)
   - [Zoom Whiteboard](#zoom-whiteboard)
   - [Zoom Hub](#zoom-hub)
   - [Zoom Clips](#zoom-clips)
   - [Zoom Scheduler](#zoom-scheduler)
   - [Zoom Tasks](#zoom-tasks)
6. [スペース&ハードウェア](#spaces-hardware)
   - [Zoom Rooms](#zoom-rooms)
   - [Zoom Spaces](#zoom-spaces)
7. [業種特化ソリューション](#industry-solutions)
   - [Zoom Contact Center (ZCC)](#zoom-contact-center)
   - [Zoom for Sales](#zoom-for-sales)
   - [Zoom for Education](#zoom-for-education)
   - [Zoom for Government](#zoom-for-government)
   - [Zoom for Healthcare](#zoom-for-healthcare)
8. [開発者向けツール](#developer-tools)
9. [自治体向け戦略的活用パターン](#strategic-patterns)
10. [API・データモデル・統合](#api-integration)
11. [参考文献](#references)

---

<a id="executive-summary"></a>
## 1. エグゼクティブサマリー

### Zoomエコシステムの進化

Zoomは単なるビデオ会議ツールから、**AI-First Collaboration Platform（Zoom Workplace）**へと進化しました。その構造は3層に分かれます:

```
┌─────────────────────────────────────────────┐
│   AI Layer (Intelligence)                   │
│   • AI Companion 3.0                        │
│   • AI Concierge                            │
│   • Zoom Revenue Accelerator                │
└─────────────────────────────────────────────┘
                    ↓ データ資産化
┌─────────────────────────────────────────────┐
│   Communication Layer                       │
│   • Zoom Meetings / Phone / Team Chat      │
│   • Webinars / Events / Contact Center     │
└─────────────────────────────────────────────┘
                    ↓ コラボレーション
┌─────────────────────────────────────────────┐
│   Productivity Layer                        │
│   • Zoom Docs / Whiteboard / Hub / Clips   │
│   • Scheduler / Tasks / Calendar / Mail    │
└─────────────────────────────────────────────┘
```

### データ資産化の概念

**Data Assetization（データ資産化）**とは:
- 音声・動画・テキスト等の「フロー情報」を構造化
- AIで分析・要約し、検索可能な「ストック情報」に変換
- 組織の知識ベースとして長期保存・活用

### 自治体向け価値提案

| 製品組み合わせ | 主な用途 | 価値 |
|---|---|---|
| **ZP + AIC** | 窓口電話、BCP | 通話要約、議事録自動化、低コスト |
| **ZP + ZRA** | 働き方改革 | 全文字起こし、会話分析、負担軽減 |
| **ZM + ZRA** | 教育DX | 授業品質可視化、GIGA端末活用 |
| **Full Stack** | 総合DX | オムニチャネル統合、先進自治体 |

---

<a id="zoom-workplace"></a>
## 2. Zoom Workplace - 統合プラットフォーム

### 概要

**Zoom Workplace**は、Zoomのすべてのコラボレーションツールを統合した単一プラットフォームです。2026年1月以降、UI刷新により、よりシンプルでモダンなデザインになりました。

### 主要機能

#### 2.1 Hub（ハブ）- 統合ワークスペース

- **説明**: すべてのZoomコンテンツ（会議、チャット、ドキュメント、ファイル）を一元管理
- **AI機能**: Hub AI
  - 自然言語でファイル検索・要約・生成
  - 例: 「先週の会議で議論されたコスト削減案をまとめて」
- **デフォルト有効化**: 2026年1月からオンラインユーザーはデフォルトで有効（2月には全ユーザーに展開予定）

#### 2.2 UI刷新（2026年1月）

##### Zoom Workplaceアプリ
- タブの切り替え・レイアウトのカスタマイズが容易
- 一貫性のあるデザイン

##### Zoom Meetings
- 簡略化されたツールバー
- 統合されたユーザー設定
- 整理されたホスト用ツール

##### Zoom Team Chat
- クリーンなデザイン（デスクトップ/モバイル/ウェブで統一）

#### 2.3 統合機能

- **シングルサインオン（SSO）**: Microsoft 365、Google Workspace連携
- **カレンダー統合**: Zoom Calendar、Outlook、Google Calendar
- **メール統合**: Zoom Mail（Gmail、Outlookも連携可能）
- **ファイルストレージ連携**: Google Drive、OneDrive、Zoom Hub

#### 2.4 Frontline向け拡張

- **対象**: 現場職員（自治体なら道路管理、福祉施設巡回など）
- **機能**:
  - Push-to-Talk（PTT）: ワンタッチ音声通信
  - モバイルビデオ通話
  - セキュアメッセージング
  - シフト管理（CSV一括アップロード対応）

---

<a id="communication-products"></a>
## 3. コミュニケーション製品

<a id="zoom-meetings"></a>
### 3.1 Zoom Meetings

#### 概要

世界標準のビデオ会議プラットフォーム。無料プランでは最大100名、40分まで。有料プランでは300名〜1,000名、時間無制限。

#### 主要機能（2026年最新）

##### 基本機能
- **HD ビデオ/オーディオ**: 1080p対応
- **画面共有**: 複数参加者同時共有可能
- **レコーディング**: クラウド/ローカル保存
- **バーチャル背景**: カスタム画像・動画対応
- **ブレイクアウトルーム**: 最大50ルーム

##### AI機能（AI Companion搭載）
- **リアルタイム字幕・翻訳**: 33言語対応
  - 日本語→英語、英語→日本語など
- **会議要約**: 自動生成、参加者に共有
- **スマートレコーディング**:
  - 自動チャプター生成
  - ハイライト抽出
  - トピックトラッキング
- **会議中質問**: 「今何の話をしていますか?」と聞ける
- **会議後検索**: 録画内のキーワード検索（トランスクリプトベース）

##### エンゲージメント機能
- **リアクション**: 👍👏❤️など
- **投票（Polls）**: 事前/会議中/事後に実施可能
- **Q&A**: 参加者からの質問を整理・回答
- **ホワイトボード**: 会議中にコラボレーション
- **注釈機能**: 画面共有に直接マーキング

##### ビューモード
- **Multi-speaker view**: 話している人を自動的に前面表示
- **ギャラリービュー**: 最大49名同時表示
- **Focus Mode**: ホストのみ全員表示、参加者は自分だけ表示（試験などに活用）

##### セキュリティ
- **待機室**: 参加者を事前承認
- **パスコード**: 会議ごとに設定
- **エンドツーエンド暗号化（E2EE）**: オプション有効化
- **録画暗号化**: クラウド保存時

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **庁内会議** | ZM + AIC要約 | 議事録作成時間▼50% |
| **住民説明会** | ZM + ウェビナー | 参加率▲30%、録画公開で透明性向上 |
| **教育委員会** | ZM + 翻訳字幕 | 外国籍保護者対応 |
| **災害対策本部** | ZM + ブレイクアウト | 部門別迅速協議 |

---

<a id="zoom-phone"></a>
### 3.2 Zoom Phone

#### 概要

クラウドベースの電話システム（UCaaS）。PBXの置き換え、BCP対策、コスト削減を実現。

#### 主要機能

##### 基本電話機能
- **内線通話**: Zoom Phone同士は無料
- **外線通話**: PSTN接続（050番号、市外局番対応）
- **代表番号**: 自動音声応答（IVR）
- **コールパーク/転送/保留**
- **ボイスメール**: 文字起こし付き
- **通話録音**: 自動/手動

##### AI機能（AI Companion搭載）

###### 通話要約（Call Summary）
- **機能**: 通話終了後、自動で要約とタスクを生成
- **ダウンロード制限**: 
  - AICのみ: 要約テキストのみ、直接ダウンロード不可
    - **回避策**: Zoom Docs変換→PDF/Word出力、コピペ、メール共有、API取得
  - ZRA併用: 全文字起こしダウンロード可能

###### ボイスメール優先度付け（Voicemail Prioritization）
- **機能**: 文字起こしから緊急度を判定し、重要な順に表示
- **活用**: 担当者不在時の迅速対応

###### SMS要約（日本未対応）
- **機能**: SMSスレッドを要約し、引き継ぎ効率化
- **制約**: 日本ではSMS機能自体が未提供

##### ハードウェア連携
- **デスクフォン**: Poly、Yealink等の認定デバイス
- **ソフトフォン**: PC/Mac/スマホアプリ
- **Zoom Rooms**: 会議室からZoom Phone通話

##### セキュリティ・信頼性
- **稼働率**: 99.999%（年間5.26分停止）
- **Local Survivability**: インターネット切断時も通話継続
- **Zoom Node**: 拠点ごとにゲートウェイ設置可能
- **E911**: 緊急通報対応（米国）

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **窓口電話** | ZP + AIC要約 | 対応記録自動化、引き継ぎ円滑化 |
| **BCP対策** | ZP + クラウド | 災害時も在宅勤務で電話対応 |
| **コスト削減** | レガシーPBX廃止 | TCO▼40%、保守費用削減 |
| **庁内内線** | 050番号統一 | 部署間無料通話、モバイルも内線化 |

#### ZRAとの組み合わせ

**Pattern 2: ZP + ZRA Booster**
- **対象自治体**: 財政力あり、議事録外注費が年間300万円以上
- **提案内容**:
  - ZPで基本電話機能
  - ZRAで全通話自動文字起こし・分析
  - AICは無料特典として訴求
- **ROI**:
  - 議事録外注費削減: ¥3,000,000/年
  - 職員残業削減: 10分/日 × 240日 = ¥80,000/年/人
  - 非定量的: 窓口対応品質向上、クレーム検知

---

<a id="zoom-team-chat"></a>
### 3.3 Zoom Team Chat

#### 概要

業務用インスタントメッセージング。Slack、Microsoft Teamsの競合製品。

#### 主要機能

##### 基本機能
- **1対1チャット**
- **グループチャット**: 最大1,000名
- **チャンネル**: 公開/非公開
- **スレッド**: 話題ごとに整理
- **ファイル共有**: 最大50MB（無料）、1GB（有料）
- **絵文字・リアクション**
- **検索**: 過去のメッセージ・ファイルを横断検索

##### AI機能（AI Companion搭載）

###### チャット要約（Chat Thread Summary）
- **機能**: 長いスレッドを数行に要約
- **例**: 100件のメッセージ→「予算案について、A部長が承認。実施は来月」

###### 下書き支援（Draft Response）
- **機能**: 返信文をAIが提案
- **トーン調整**: フォーマル/カジュアル/励まし等を選択可能

##### コラボレーション機能
- **Zoom DocsをチャットにEmbed**
- **Zoom Whiteboardを共同編集**
- **Zoom Meetingをワンクリック開始**
- **タブ機能**: リンク、ホワイトボード、リソースをピン留め

##### 統合
- **Slack連携**: Zoom AI Companion in Slackアプリ
- **Microsoft Teams連携**: 通知・カレンダー同期
- **サードパーティアプリ**: Salesforce、Jira、Asana等

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **部署間連携** | チャンネル作成 | メールより迅速、履歴共有 |
| **災害時連絡** | 一斉通知チャンネル | 迅速な情報共有 |
| **プロジェクト管理** | スレッド + Docs | ドキュメント・議論を一元化 |
| **外部連携** | ゲストアクセス | 業者とのやり取りを記録 |

---

<a id="zoom-webinars"></a>
### 3.4 Zoom Webinars

#### 概要

大規模オンラインセミナー向けプラットフォーム。参加者は「視聴専用」、パネリストのみ発言可能。

#### 主要機能

##### 規模
- **最小**: 500名
- **最大**: 50,000名（View-Only Webinar）
- **パネリスト**: 最大100名

##### インタラクション機能
- **Q&A**: 参加者からの質問を整理・回答
- **投票**: リアルタイム集計
- **挙手**: パネリストに昇格
- **チャット**: 全員/パネリストのみ

##### 登録・管理
- **登録フォーム**: カスタマイズ可能
- **承認フロー**: 手動/自動
- **リマインダー**: 自動メール送信
- **録画配信**: オンデマンド視聴

##### AI機能（AI Companion搭載）
- **ウェビナー要約**: 自動生成
- **Q&A自動分類**: 類似質問をグループ化

##### 新機能（2026年1月）

###### 学習証明書（Learning Certificates）
- **機能**: 
  - 特定条件クリア者に証明書発行（例: 60分以上視聴、クイズ正解）
  - デザインカスタマイズ可能
  - 自動メール送信
- **用途**: 研修、資格講座

###### 企業インサイト（Company Insights）
- **機能**: 参加者のメールドメインで企業別集計
- **用途**: B2B営業、ターゲット企業の興味度把握

###### エンゲージメントスコア（Engagement Score）
- **機能**: チャット、Q&A、投票への参加度を0〜10点でスコア化
- **用途**: ホットリード特定

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **住民説明会** | ウェビナー500名 | オンライン参加率▲、録画公開で透明性 |
| **職員研修** | 学習証明書 | 受講管理自動化 |
| **企業誘致セミナー** | 企業インサイト | 興味企業の特定、フォローアップ |
| **オープンデータ講座** | エンゲージメントスコア | 熱心な参加者にコミュニティ招待 |

---

<a id="zoom-events"></a>
### 3.5 Zoom Events

#### 概要

大規模仮想イベント・ハイブリッドイベント向けプラットフォーム。Webinarsより高度な機能（複数セッション、ネットワーキング、展示ブース等）を提供。

#### 主要機能

##### イベント構成
- **Multi-Session**: 複数の同時セッション（タイムテーブル形式）
- **Lobby（ロビー）**: 参加者を迎える動的スペース
- **ブレイクアウト・ネットワーキング**: 1対1マッチング
- **Expo Booths（展示ブース）**: スポンサー・出展者エリア

##### チケット管理
- **チケットタイプ**: Early Bird、VIP、一般など
- **決済連携**: Stripe等
- **割引コード**

##### 分析
- **Cross-Event Analytics（2025年12月〜）**:
  - 複数イベントのトレンド分析
  - どのトピック/形式が人気か可視化
  - ROI計算

##### AI機能（AI Companion搭載）
- **イベント要約**: 全セッションの総括
- **Q&A自動分類**

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **地域フェスティバル** | ハイブリッド開催 | 遠方住民も参加可能 |
| **企業向けカンファレンス** | 展示ブース | 地元企業PRの場 |
| **オープンデータDay** | Multi-Session | 初心者〜上級者向け同時開催 |
| **DX推進フォーラム** | ネットワーキング | 自治体間の知見共有 |

---

<a id="ai-features"></a>
## 4. AI機能群

<a id="ai-companion"></a>
### 4.1 AI Companion (AIC)

#### 概要

Zoom製品全体に組み込まれた無料AIアシスタント。有料プランユーザーは追加費用なしで利用可能。

#### 提供形態

##### 標準版（無料）
- Zoom Workplace内で利用
- 会議要約、チャット下書き、Docs生成等

##### Custom AI Companion（有料アドオン）
- **Deep Research Mode**: 複数ドキュメント・会議・Web検索を統合分析
- **カスタムモデル**: 企業独自のLLMを統合可能
- **Slackアプリ**: Slack内でAI Companion利用

##### AI Companion 3.0（2025年12月〜）

###### Conversational Work Surface（会話型ワークスペース）
- **説明**: ウェブ上の中央ハブ。Zoom Docs、会議インサイト、Web検索を統合
- **用途**: AIとのブレインストーミング、タスク完了
- **URL**: [ai.zoom.us](https://ai.zoom.us)

###### Agentic Retrieval（エージェント型検索）
- **説明**: Zoom、Google Drive、OneDriveを横断検索
- **Gmail/Outlookアカウント連携**: メール内容も検索対象（2026年1月〜）
- **文脈理解**: 「先週のプロジェクト会議の決定事項」など自然言語で検索

###### Calendar Integration（カレンダー統合）
- **機能**: AI Companionウェブ画面から直接会議参加、会議後アセット（要約・録画）にアクセス

###### Writing Mode（執筆モード）
- **機能**: ドキュメントをAIと並べて作成・洗練
- **コンテキスト活用**: 過去の会議・他のDocsから関連情報を引用

###### Deep Research Mode（深掘りリサーチ）
- **機能**: 複数のドキュメント、会議、Web情報を分析し包括的レポート生成
- **制約**: Custom AI Companionライセンスが必要
- **用途**: 戦略企画、市場分析

#### 各製品での機能

##### Zoom Meetings
- **会議要約**: 自動生成、次のステップ抽出
- **会議中質問**: 「今何の話?」「決定事項は?」
- **スマートレコーディング**: チャプター、ハイライト、トピック抽出

##### Zoom Phone
- **通話要約**: 次のアクション付き
- **ボイスメール優先度付け**: タスク抽出
- **SMS要約**: 日本未対応

##### Zoom Team Chat
- **スレッド要約**
- **下書き支援**: トーン調整

##### Zoom Docs
- **AI執筆アシスタント**: Writing Mode、Deep Research Mode
- **データテーブル自動入力**: 会議内容からテーブル列を埋める
- **Help Me Read**: 長文の概要・マインドマップ生成

##### Zoom Whiteboard
- **コンテンツ生成**: アイデアをSticky、テーブル、マインドマップとして生成
- **会議/Docs/Chatからホワイトボード生成**: 会話を視覚化
- **AI画像変換**: 物理ホワイトボードの写真をデジタル化

##### Zoom Hub
- **Hub AI**: ファイル横断検索・要約・生成

#### 制約事項

##### ダウンロード制限
- **会議要約・通話要約**: 直接ダウンロードボタンなし
- **回避策**:
  1. Zoom Docs変換→PDF/Word出力
  2. コピー&ペースト
  3. メール共有
  4. API取得

##### 話者識別
- **会議室マイク共有**: 個々の話者識別不可（「会議室A」として処理）
- **解決策**: Intelligent Director機能付きZoom Roomsハードウェア

##### 多言語対応
- **サポート言語**: 日本語、英語、スペイン語、フランス語、ドイツ語、ポルトガル語、簡体字中国語、イタリア語
- **精度低下要因**: 専門用語、方言、音質不良

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **庁議** | 会議要約自動生成 | 議事録作成時間▼50% |
| **窓口対応記録** | 通話要約 | 引き継ぎ円滑化、クレーム分析 |
| **政策立案** | Deep Research Mode | 複数資料を統合分析 |
| **住民問い合わせ** | チャット下書き | 迅速・丁寧な返信 |

---

<a id="ai-concierge"></a>
### 4.2 AI Concierge（AI コンシェルジュ）

#### 概要

Zoom Phone専用の24時間365日対応AI受付。自然言語理解で問い合わせを自動対応・適切部門へ転送。

#### 主要機能

##### インテントベースルーティング
- **説明**: 発話内容を解析し、適切な部署へ自動転送
- **例**:
  - 「住民票の発行について」→市民課
  - 「水道料金の支払い」→水道局
  - 「ゴミ収集日」→環境課

##### ナレッジベース参照（Deflection）
- **説明**: 定型質問に自動応答
- **例**:
  - 「営業時間は?」→「平日9時〜17時です」
  - 「駐車場はある?」→「庁舎南側に50台分あります」

##### ノーコード設定（AI Studio）
- **説明**: プログラミング不要でシナリオ作成
- **権限委譲**: 各部署で独自のナレッジ追加可能

##### エスカレーション
- **説明**: 複雑な問い合わせ・クレームは人間オペレーターへ
- **感情検知**: 怒り・不安を検出して優先転送

#### 制約事項

##### 複雑な感情労働
- **不可**: 複雑なクレーム対応、微妙なニュアンスの会話
- **推奨**: 定型質問・ルーティング業務に特化

##### ライセンス
- **追加料金**: Zoom Virtual Agent等の追加ライセンスが必要な場合あり

##### 日本での制約
- **SMS連携不可**: 日本ではZoom PhoneのSMS機能自体が未提供

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **夜間・休日問い合わせ** | AI Conciergeが自動応答 | 住民満足度向上、職員負担軽減 |
| **定型質問（営業時間等）** | ナレッジベース | オペレーター負荷▼30% |
| **多言語対応** | 自動翻訳連携 | 外国籍住民サポート |
| **災害時FAQ** | 緊急ナレッジ追加 | 迅速な情報提供 |

#### 実装パターン: 大分モデル2.0との統合

**教育委員会の保護者問い合わせ**
- AI Concierge: 「学校休校情報」「給食アレルギー対応」等の定型質問
- ZRA: 複雑な相談（いじめ、進路）の内容分析・フォローアップ

---

<a id="zoom-revenue-accelerator"></a>
### 4.3 Zoom Revenue Accelerator (ZRA)

#### 概要

営業・顧客対応向けの高度な会話分析プラットフォーム。自治体では「議事録作成」「窓口対応分析」「教育品質向上」に活用可能。

#### 主要機能（2026年最新）

##### 詳細な会話分析

###### 基本メトリクス
- **Talk/Listen Ratio（話す/聞く比率）**: 営業なら30/70が理想
- **話速（Words per Minute）**: 速すぎ/遅すぎを検知
- **フィラーワード頻度**: 「えー」「あのー」のカウント
- **質問回数**: 良い質問（Probing Questions）の回数

###### 感情分析（Sentiment Analysis）
- **BERT等の自然言語処理**: 会話全体のポジティブ/ネガティブ推移を可視化
- **平均スコア**: 会話ごとの感情スコア
- **トピック別感情**: 「料金」「サポート」等の話題ごとの感情

###### トピックトラッキング
- **キーワード言及**: 競合社名、価格、懸念事項の言及タイミング特定
- **例**: 「Teams」が何回言及されたか、どのタイミングか

##### リスクシグナル検知（Risk Signal Detection）
- **自動検知項目**:
  - ネクストステップ未設定
  - 決裁権者不在
  - 予算言及なし
  - ネガティブ感情急上昇
- **アラート**: 自動通知（メール、Slack、Teams Chat）

##### 全文文字起こし（Full Transcript Download）
- **説明**: 通話・会議の完全なトランスクリプトをダウンロード可能
- **AICとの違い**: AICは要約のみ、ZRAは全文
- **制約**: 一括ダウンロード不可→カスタムアプリ（Zoom Phone API/ZRA API）で対応

##### CRM連携
- **対象**: Salesforce、HubSpot
- **構造化データ**: CRMプランに応じて構造化したデータ（商談名、感情スコア、リスクフラグ等）を自動同期
- **非対象CRM**: 構造化されず一括データとして渡す
- **API連携**: カスタムCRM・BIツールへのプログラマティック同期

##### カスタマイズ要約（Custom Summary）
- **説明**: 欲しい項目を自然言語で指定し、思い通りの要約を生成
- **例**: 
  - 「授業での生徒の質問とその回答を抽出」
  - 「クレームの原因と対応策を要約」

##### 複数のカスタマイズ要約（Multiple Summaries）
- **説明**: タグや会話タイトルで複数の要約テンプレートを任意の会話に自動適用
- **例**:
  - タグ「営業」→営業用要約
  - タグ「サポート」→サポート用要約

##### Playbook機能
- **説明**: 最大3つのPlaybookを作成。9つの要素を指定して会話から自動抽出
- **要素例**:
  - 決裁権者の有無
  - 予算の言及
  - 競合言及
  - ネクストステップ
  - 攻撃的言動（教育・窓口で活用）
  - 授業の雰囲気（教育向け）
  - 先生の進め方（教育向け）
- **NLPベース**: 自然言語処理で柔軟に検出

##### Scorecard機能
- **説明**: 会話品質を定量評価（100点満点等）
- **カスタマイズ**: 評価項目を独自に設定
- **例**（教育向け）:
  - 小学校: 「わかりやすさ」「児童参加度」「ユニバーサルデザイン配慮」
  - 中学校: 「論理展開」「質問の質」「発展的内容」
  - 高校: 「大学入試対応」「探究心喚起」「キャリア意識」
- **自動次のアクション生成**: スコアに基づき改善提案
- **経年グラフ**: 成長を可視化

##### Indicator機能
- **説明**: リアルタイムNG検出
- **検出対象**:
  - NGワード（差別用語、禁止用語）
  - トーンアラート（攻撃的、威圧的）
  - 生徒の安全監視（いじめ、暴力関連）
- **即座フォローアップ**: 管理者に通知

#### ストレージとアクセス制御

##### データ保存
- **ZRAライセンス**: 分析メタデータ・トランスクリプト無制限保存
- **映像**: 短期削除（例: 30日）
- **分析データ**: 数年保持可能（規約に応じて）

##### RBAC（Role-Based Access Control）
- **User**: 自分の会話のみ
- **Manager**: 部下の会話
- **Exec**: 全社の会話

##### 自動録画・同意取得
- **自動録画**: ZRA分析には録画が必須
- **同意ポップアップ**: 参加者に通知

#### 外部参加者識別の限界
- **課題**: カレンダー連携で社内外を判定するが、外部ゲストが社内アカウントでログインすると誤認識
- **対策**: 手動タグ付け、API連携でCRMの取引先データと照合

#### Botレコーダー統合
- **説明**: ZRAのRecorder BotがMicrosoft Teams、Google Meetに参加し、音声/動画をキャプチャしてZRAで分析
- **用途**: 他社ツール利用時もZRAで統合分析

#### 自治体向けユースケース

##### 議事録自動化
- **対象**: 財政力指数 ≥ 0.9、議事録外注費 ≥ ¥3,000,000/年
- **効果**: 
  - 外注費削減: ¥3,000,000/年→¥0
  - 職員負担軽減: リアルタイム文字起こしで速記不要
  - 検索可能: 過去の議事録からキーワード検索

##### 窓口対応品質向上
- **分析項目**:
  - 話速、フィラーワード
  - 感情推移（クレーム検知）
  - NG言動検出
- **効果**:
  - 優良対応者のパターン分析→マニュアル化
  - クレーム予兆検知→早期対応

##### 教育DX（大分モデル2.0）

###### 概要
- **ビジョン**: 遠隔授業から「育てる」へ
- **大分県遠隔教育モデル × ZRA**

###### 主要機能

**Custom Summarization（カスタム要約）**
- 深い洞察抽出: オープンクエスチョンの検出
- 足場がけ（Scaffolding）の分析
- Instruction/Inquiry Ratio（指導/探究比率）: Talk/Listen Ratioの教育版
- 具体例の提示検出
- ユニバーサルデザイン評価

**Playbook（標準授業パターン）**
- ベテラン教員の授業パターンをモデル化
- 若手教員への知見伝達
- 県全体での授業品質均質化
- 教科別ベストプラクティス共有

**Scorecard（段階別スコア）**
- 小学校・中学校・高校それぞれの評価項目
- 100点満点での授業品質定量化
- 自動次のアクション生成（「もっと生徒の発言を引き出しましょう」等）
- 成長グラフ（縦断的分析）

**Indicator（NG検出）**
- リアルタイムNGワード検出
- トーンアラート（威圧的、暴力的）
- 生徒の安全監視（いじめ関連ワード）
- 管理職へ即座通知・フォローアップ

###### ワークフロー
1. **授業配信**: Zoom Roomsで遠隔授業
2. **自動録画・文字起こし**: ZRAが自動処理
3. **AIによる5分要約**: 管理職が迅速チェック
4. **Custom Summary**: 深い洞察抽出
5. **Playbook適用**: 授業パターン判定
6. **Scorecard評価**: 定量スコア化
7. **Indicator検出**: NG事項があれば即座通知
8. **ダッシュボード表示**: 県教育委員会が俯瞰
9. **セキュアストレージ**: 日本データセンターに保存

###### ステークホルダー別メリット

**教員**
- 客観的フィードバック
- ベストプラクティス学習
- 記録業務削減（10分/日→年間¥80,000相当）

**管理職・教育委員会**
- 県全体の授業品質可視化
- データドリブンな教員研修
- 保護者への説明責任

**生徒・保護者**
- 授業品質向上
- 安全な学習環境（いじめ検知）
- 録画で復習可能

###### 全国展開構想
- **大分県→他県**: モデルの横展開
- **GIGA端末更新期**: ZM + ZRAセット提案
- **文部科学省「Next High School」「スマートスクール」**: 補助金活用

#### コスト・ROI

##### ライセンス費用
- **高額**: カスタム見積もり（数百万円〜/年規模）
- **対象**: 財政力ある自治体、教育DX予算確保済み

##### ROI計算（自治体向け）

**議事録作成削減**
- 外注費: ¥3,000,000/年→¥0
- 職員残業削減: 10分/日 × 240日 × 時給¥2,000 = ¥80,000/年/人
- 50人規模部署: ¥4,000,000/年

**教育DX**
- 非定量的: 授業品質向上、生徒の学力向上、教員のモチベーション向上
- 長期的データ資産: 過去の授業を分析し、カリキュラム改善

**投資判断閾値**
- 財政力指数 ≥ 0.9
- 議事録外注費 ≥ ¥3,000,000/年
- 教育DX予算確保済み

---

<a id="productivity-tools"></a>
## 5. 生産性ツール

<a id="zoom-docs"></a>
### 5.1 Zoom Docs

#### 概要

Zoom統合のクラウドベース文書作成ツール。Google Docs、Notion、Confluenceの競合製品。AI Companion 3.0搭載。

#### 主要機能

##### 基本編集機能
- **リッチテキスト編集**: 見出し、箇条書き、番号付きリスト
- **テーブル**: データテーブル（後述）
- **コードブロック**: シンタックスハイライト
- **画像・動画埋め込み**
- **リンク**: 外部URL、Zoom会議、他のDocs

##### AI機能（AI Companion 3.0搭載）

###### Writing Mode（執筆モード）
- **並行作成**: AIと並べてドキュメント作成
- **コンテキスト活用**: 過去の会議・他のDocsから引用
- **リファイン**: 文章の改善提案

###### Deep Research Mode（深掘りリサーチ）
- **包括的レポート生成**: 複数のドキュメント・会議・Web情報を統合分析
- **制約**: Custom AI Companionライセンス必要

###### Help Me Read（読解支援）
- **概要生成**: 長文を数行に要約
- **マインドマップ**: 構造を可視化
- **キーアーギュメント**: 重要な主張を抽出

###### データテーブル自動入力
- **説明**: 会議内容からテーブルの列を自動入力
- **例**: 
  - 会議で「A課: 予算100万円、B課: 予算150万円」→テーブルに自動反映
  - フィードバック報告書、会議議事録、プロジェクトトラッカーに活用

##### コラボレーション機能
- **リアルタイム共同編集**: 複数人が同時編集
- **コメント**: 特定箇所にコメント
- **@メンション**: 担当者を指定
- **バージョン履歴**: 過去版への復元
- **変更通知購読**: ドキュメント更新時に通知

##### ページレベル共有（2025年12月〜）
- **説明**: ドキュメント全体ではなく、特定ページのみを共有
- **用途**: 機密情報を含むドキュメントの一部だけを外部共有

##### エクスポート
- **形式**: PDF、Word、Markdown

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **政策立案** | Deep Research Mode | 複数資料を統合分析、包括的レポート |
| **部署間共同編集** | リアルタイム編集 | メール添付不要、常に最新版 |
| **議事録作成** | 会議要約→Docs | AI要約をそのままドキュメント化 |
| **外部委託** | ページレベル共有 | 機密部分を除いて業者に共有 |

---

<a id="zoom-whiteboard"></a>
### 5.2 Zoom Whiteboard

#### 概要

オンライン・オフライン両用のインタラクティブホワイトボード。Miro、Mural、Microsoft Whiteboardの競合製品。

#### 主要機能

##### 基本ツール
- **描画ツール**: ペン、ハイライター、消しゴム
- **図形**: 四角、円、矢印
- **スティッキーノート**: 色分け可能
- **テキストボックス**
- **画像挿入**
- **Smart Connectors（スマートコネクタ）**: 図形を自動接続

##### AI機能（AI Companion搭載）

###### コンテンツ生成
- **説明**: アイデアをSticky、テーブル、マインドマップとして生成
- **例**: 「地域活性化のアイデアを5つ出して」→5つのSticky自動生成

###### 会議/Docs/Chatからホワイトボード生成（2025年12月〜）
- **説明**: 会議内容や既存ドキュメントを視覚化したホワイトボードを自動作成
- **用途**: 空白のキャンバスから始めるのではなく、既存の議論を整理

###### AI画像変換（2026年1月〜）
- **説明**: 物理ホワイトボードの写真をデジタル化し、オブジェクトを識別
- **用途**: 会議室のホワイトボードをそのまま共有、後から編集

##### コラボレーション機能
- **リアルタイム共同編集**: 複数人が同時編集
- **コメント**: 特定箇所にコメント
- **投票**: アイデアに投票
- **タイマー**: ブレインストーミングの時間管理

##### Individual Whiteboard Mode（個別ホワイトボードモード、2025年12月〜）
- **説明**: 各参加者に個別キャンバスを提供
- **用途**: 集中ブレインストーミング、試験、評価
- **ファシリテーター**: リアルタイムで進捗確認、個別フィードバック

##### 会議中注釈をホワイトボードに保存（2025年12月〜）
- **説明**: 画面共有中の注釈をワンクリックでZoom Whiteboardに変換
- **用途**: 一時的なマーキングを恒久的な資料化

##### Zoom Rooms連携
- **Zoom Room for Touch**: タッチスクリーンでホワイトボード操作
- **会議前後**: 会議外でもホワイトボードにアクセス・編集

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **政策ブレスト** | リアルタイム共同編集 | 遠隔地の職員も参加、アイデア可視化 |
| **ワークショップ** | Individual Mode | 参加者が個別に考え、後で共有 |
| **住民参加型企画** | 投票機能 | 優先順位付け |
| **災害対策シミュレーション** | 図形・コネクタ | フローチャート作成 |

---

<a id="zoom-hub"></a>
### 5.3 Zoom Hub

#### 概要

すべてのZoomコンテンツ（会議、チャット、Docs、ファイル）を一元管理するナビゲーションセンター。

#### 主要機能

##### コンテンツ管理
- **Recent（最近）**: 最近アクセスしたコンテンツ
- **Shared with Me（共有）**: 他人から共有されたコンテンツ
- **Favorites（お気に入り）**: ピン留め
- **フォルダ**: カスタムフォルダ作成

##### 検索
- **横断検索**: 会議録画、Docs、チャット、ファイルを一度に検索
- **フィルタ**: タイプ、日付、作成者で絞り込み

##### Hub AI（2025年12月〜）
- **説明**: AI Companionを直接Hub内で使用
- **機能**:
  - ファイル横断検索
  - 要約生成
  - 新規コンテンツ生成
- **例**: 「先月の会議で議論された予算案をまとめて」→関連Docs・会議要約を統合

##### Hub Auto-Enabled（2026年1月〜）
- **説明**: オンラインユーザーはデフォルトで有効（2月には全ユーザーに展開予定）
- **ホームベース**: 作業の起点

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **職員の日次業務** | Hubをホーム画面 | 必要な情報に即座アクセス |
| **プロジェクト管理** | フォルダで整理 | 関連資料を一箇所に集約 |
| **ナレッジマネジメント** | Hub AI横断検索 | 過去の知見を即座に発掘 |
| **外部委託管理** | 共有フォルダ | 業者との資料受け渡し |

---

<a id="zoom-clips"></a>
### 5.4 Zoom Clips

#### 概要

画面録画・ビデオメッセージツール。Loom、Vidyardの競合製品。

#### 主要機能

##### 録画
- **画面+カメラ**: 同時録画
- **画面のみ/カメラのみ**: 選択可能
- **編集**: トリミング、タイトル挿入

##### 共有
- **リンク共有**: 短縮URL自動生成
- **埋め込み（2026年1月〜）**: サードパーティサイト、イントラネット、学習プラットフォームに埋め込み可能
- **ダウンロード**: MP4形式

##### 分析
- **視聴分析**: 視聴回数、視聴完了率、エンゲージメント（いいね、コメント）
- **インタラクション行動**: どの部分で再生を停止/巻き戻ししたか

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **住民向け手続き説明** | 画面録画で手順を解説 | 窓口問い合わせ削減 |
| **職員向け研修** | 研修動画を録画・共有 | 非同期学習、時間節約 |
| **議会報告動画** | 首長メッセージを録画 | 住民への情報発信 |
| **オープンデータ活用例** | データ分析手順を録画 | データ利活用促進 |

---

<a id="zoom-scheduler"></a>
### 5.5 Zoom Scheduler

#### 概要

アポイント調整ツール。Calendly、Microsoft Bookingsの競合製品。

#### 主要機能

##### スケジュール共有
- **空き時間表示**: カレンダー連携で自動表示
- **予約ページ**: カスタマイズ可能
- **タイムゾーン対応**: 国際対応

##### 自動化
- **確認メール**: 予約確定時に自動送信
- **リマインダー**: 前日・1時間前に通知
- **Zoom会議自動作成**: 予約確定時にミーティングリンク生成

##### 情報収集
- **カスタムフォーム**: 予約時に質問を追加
- **例**: 「相談内容を記入してください」

##### カレンダー統合
- **対応**: Zoom Calendar、Google Calendar、Outlook、iCloud

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **住民相談予約** | Scheduler公開 | 電話予約不要、24時間受付 |
| **企業誘致商談** | 空き時間共有 | 調整メール往復削減 |
| **オンライン申請サポート** | Zoom会議自動作成 | ワンクリックで支援開始 |

---

<a id="zoom-tasks"></a>
### 5.6 Zoom Tasks（タスク管理）

#### 主要機能

##### タスク作成
- **手動作成**: チャットやDocsから直接作成
- **自動作成（Zoom Phone + AI Companion）**: 通話要約・ボイスメールからタスク抽出（2025年12月〜）

##### タスク管理
- **担当者割り当て**
- **期限設定**
- **優先度**: 高/中/低
- **ラベル/タグ**
- **添付ファイル**: Docs、画像等

##### 通知
- **リマインダー**: 期限前通知
- **変更通知**: 担当変更・コメント追加時

##### 統合
- **Team Chat**: チャットからタスク作成
- **Zoom Meetings**: 会議中にタスク作成
- **カレンダー**: タスクをカレンダー表示

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **プロジェクト管理** | タスク分割・割り当て | 進捗可視化 |
| **窓口フォローアップ** | 通話要約→自動タスク | 対応漏れ防止 |
| **部署間協業** | 共有タスクリスト | 責任明確化 |

---

<a id="spaces-hardware"></a>
## 6. スペース&ハードウェア

<a id="zoom-rooms"></a>
### 6.1 Zoom Rooms

#### 概要

会議室をビデオ会議化するハードウェア・ソフトウェアソリューション。

#### 構成

##### 必須コンポーネント
1. **Zoom Roomsコントローラー**: タブレット（iPad、Android）またはタッチパネル
2. **カメラ**: PTZ（パン・チルト・ズーム）カメラ推奨
3. **マイク**: 天井マイク、テーブルマイク
4. **スピーカー**: 全指向性スピーカー
5. **ディスプレイ**: HDMI接続のモニター・プロジェクター

##### オプション
- **Zoom Rooms Appliance**: 専用ハードウェア（Mini PC等）
- **Zoom for Touch**: タッチスクリーン一体型

#### 主要機能

##### ワンタッチ参加
- **カレンダー連携**: 会議開始時刻に「参加」ボタン表示
- **QRコード**: スマホでスキャンして参加

##### Intelligent Director
- **説明**: 複数のカメラで話者を自動追跡・切り替え
- **用途**: 大人数会議でも話者を明確に表示
- **話者識別**: AI Companionと連携し、個別の話者として認識

##### 音声コマンド（Hey Zoomie）
- **対応コマンド（2025年12月拡張）**:
  - 「Hey Zoomie, start a meeting」（会議開始）
  - 「Hey Zoomie, turn up the volume」（音量上げ）
  - 「Hey Zoomie, turn on captions」（字幕オン）
  - 「Hey Zoomie, how do I share my screen?」（使い方質問）

##### Zoom Phone連携
- **説明**: Zoom Roomsから電話発信・受信
- **用途**: 会議室から外線通話

##### ホワイトボード共有
- **説明**: 物理ホワイトボードをカメラで撮影→自動補正→共有
- **AI画像変換**: デジタル化してZoom Whiteboardへ

##### インターオペラビリティ（Interop）
- **Microsoft Teams**: Zoom RoomsからTeams会議に参加
- **Google Meet**: Zoom RoomsからMeet会議に参加
- **Webex**: Zoom RoomsからWebex会議に参加
- **Cisco Rooms統合（2026年1月〜）**: Cisco RoomsハードウェアでZoom Meetings利用可能

#### 認定ハードウェア

##### カメラ
- Logitech Rally、Poly Studio
- AVer CAM520 Pro
- Neat Bar、Neat Board

##### マイク・スピーカー
- Shure MXA910（天井マイク）
- Logitech Rally Mic Pod
- Poly Sync 60

##### コントローラー
- Logitech Tap
- Poly TC8
- DTEN D7X（タッチスクリーン一体型）

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **庁議室** | Zoom Rooms設置 | ワンタッチ会議開始、遠隔拠点接続 |
| **議会中継** | PTZカメラ + Intelligent Director | 話者自動追跡、議事録連携 |
| **教育委員会** | Zoom Rooms for Touch | 遠隔授業配信（大分モデル） |
| **外部連携** | Interop | Teams/Meet利用者とも会議可能 |

---

<a id="zoom-spaces"></a>
### 6.2 Zoom Spaces

#### 概要

Zoom Roomsの上位概念。ワークスペース全体（会議室、ホットデスク、フォンブース等）を統合管理。

#### 主要機能

##### Workspace Reservation（ワークスペース予約）
- **説明**: 会議室・デスクを事前予約
- **チェックイン/チェックアウト**: 実際の利用状況を追跡
- **分析**: 稼働率を可視化し、スペース最適化

##### デジタルサイネージ
- **説明**: 会議室前のディスプレイに予約状況表示
- **QRコード**: 部屋の詳細情報にアクセス

##### ホットデスク管理
- **説明**: フリーアドレス席を予約・管理

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **庁舎会議室** | 予約システム統合 | ダブルブッキング防止、稼働率向上 |
| **コワーキングスペース** | ホットデスク予約 | 住民・企業への貸出管理 |

---

<a id="industry-solutions"></a>
## 7. 業種特化ソリューション

<a id="zoom-contact-center"></a>
### 7.1 Zoom Contact Center (ZCC)

#### 概要

クラウドベースのオムニチャネルコンタクトセンター。音声、ビデオ、チャット、SMS、メール、SNSを統合。

#### 主要機能

##### チャネル
- **音声通話**: インバウンド/アウトバウンド
- **ビデオエンゲージメント**: 顔の見える対応
- **ウェブチャット**: ウェブサイトに埋め込み
- **SMS**: テキストメッセージ（日本は制約あり）
- **メール**: メールチケット管理
- **SNS**: Facebook、Instagram、LINE（パートナー連携）
- **Telegram（2025年12月〜）**: ダイレクトメッセージ統合

##### IVR（Interactive Voice Response）
- **フローエディタ**: ドラッグ&ドロップでシナリオ作成
- **自然言語理解**: 音声認識でメニュー選択

##### Zoom Virtual Agent（仮想エージェント）

###### 概要
- **説明**: AIチャットボット・音声ボット
- **用途**: 定型質問自動応答、ルーティング

###### 主要機能（2025年12月〜2026年1月拡張）

**Epic統合（SpinSci経由）**
- **説明**: Epic EHR（電子カルテ）と連携
- **用途**: 予約、処方箋更新等を自動化
- **対象**: 医療機関

**Coval（ISV Exchange）**
- **説明**: AI検証・テスト・モニタリングツール
- **用途**: Virtual Agentの品質保証

**Agent Tracing（エージェント追跡）**
- **説明**: Virtual Agentの処理過程を可視化
- **用途**: トラブルシューティング、フロー最適化

**Analytics Enhancements（分析強化）**
- **新メトリクス**:
  - 非インタラクティブセッション数
  - メッセージボリューム
  - ユーザー直接フィードバック
- **用途**: エンゲージメント品質把握、ドロップオフ検知

**Change Log（変更ログ）**
- **説明**: Virtual Agentの変更履歴を記録
- **用途**: 誰が何を変更したか追跡、監査

**Enhanced Knowledge Coaching（ナレッジコーチング強化）**
- **説明**: ユーザークエリをクラスタリングし、ナレッジベースの不足箇所を特定
- **用途**: ボットが答えられない質問を把握→ナレッジ追加

**チャット添付ファイル対応**
- **説明**: Zendesk、Intercomでファイル共有可能
- **用途**: スクリーンショット、フォーム等の共有

**多言語拡張**
- **新言語**: スペイン語、カタロニア語、ベトナム語、アラビア語
- **用途**: グローバル対応

##### CRM統合
- **Salesforce CTI**: クリックtoダイヤル、画面ポップ
- **HubSpot**: 通話ログ自動記録
- **Zendesk**: チケット連携

##### Quality Management（QM、品質管理）
- **通話評価**: スコアカード作成
- **コーチングセッション（2025年12月〜）**: スコアカードからコーチングモジュール自動生成

##### Workforce Management（WFM、労働力管理）
- **シフト管理**: エージェントのスケジュール作成
- **Zoom Workplaceアプリ統合（2025年12月〜）**: スケジュール確認、休暇申請、エージェントボード表示

##### Real-Time Translation（リアルタイム翻訳、2025年12月〜）
- **説明**: SMS、ウェブチャット、SNSのメッセージをリアルタイム翻訳
- **用途**: グローバル顧客対応、エージェントは母国語で対応

##### その他新機能（2025年12月〜2026年1月）

**コールバック用音声メッセージ録音**
- **説明**: 顧客がコールバック希望時に、短い音声メッセージを録音
- **用途**: エージェントが事前に問題を把握→効率的対応

**グループSMSメッセージ**
- **説明**: SMSスレッドに最大8名の参加者追加
- **用途**: 専門家・家族を巻き込んだサポート

**CTIメールチャネル対応**
- **説明**: SalesforceのCTIコネクタ内でメール送受信・管理
- **用途**: エージェントがワークスペースを離れずメール対応

**転送先キュー可視化**
- **説明**: 転送前に対象キューのエージェント稼働状況を確認
- **用途**: ブラインド転送を回避、顧客待機時間削減

**モバイルアプリでビデオ対応**
- **説明**: Zoom Contact Centerモバイルアプリでビデオ通話発着信
- **用途**: 外出先でもビデオサポート

**コブラウズ（Cobrowse）モバイル対応**
- **説明**: iOS/Androidモバイルブラウザでのコブラウズ
- **用途**: モバイルユーザーへのリアルタイムガイド

**メッセージ・メール用Wrap-Up時間**
- **説明**: メッセージ・メール対応後、エージェントに後処理時間を設定
- **用途**: 事務作業完了、メンタルリセット

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **住民問い合わせ** | オムニチャネル対応 | 電話・チャット・メールを統合管理 |
| **夜間対応** | Virtual Agent | 24時間自動応答 |
| **外国籍住民** | リアルタイム翻訳 | 多言語サポート |
| **福祉相談** | ビデオエンゲージメント | 顔の見える相談、信頼構築 |
| **災害時ホットライン** | IVRで自動振り分け | 迅速なトリアージ |

---

<a id="zoom-for-sales"></a>
### 7.2 Zoom for Sales

#### 概要

営業チーム向けの統合ソリューション。Zoom Revenue Accelerator + Zoom Phone + CRM連携。

#### 主要機能（2025年12月〜2026年1月）

##### Channel Notifications for ZRA
- **説明**: 商談成約、リスク、新録画等の通知をZoom Team ChatまたはSlackの共有チャンネルへ
- **用途**: チーム全体で即座に情報共有

##### HubSpot Integration for Auto Dialer
- **説明**: HubSpotのコンタクトセグメントをAuto Dialerに直接取り込み、通話・会議・メールを自動CRM記録
- **用途**: タブ切り替え不要、営業効率化

##### CRM APIs for Revenue Accelerator
- **説明**: ZRAの商談・コンタクト・リードデータをCRM・BIツールにプログラマティック同期
- **用途**: 手動エクスポート不要、リアルタイムパイプライン可視化

##### Log Non-Recorded Calendar Events in Salesforce
- **説明**: 録画されていない会議もSalesforceに自動記録
- **用途**: 完全な商談タイムライン、正確な予測

##### Modifiable Custom Briefs
- **説明**: 会議要約を微調整またはAI Companionに再生成指示
- **用途**: 内部報告用/顧客共有用にカスタマイズ

##### Scheduled Callbacks for Auto Dialer
- **説明**: 特定日時にコールバック予約
- **用途**: 約束した時間に確実に再接続

##### Auto Dialer: Japan Expansion
- **説明**: 日本の電話番号へのアウトバウンドコール対応
- **用途**: 日本市場での営業活動

#### 自治体向けユースケース（企業誘致部門）

| シーン | 活用方法 | 効果 |
|---|---|---|
| **企業誘致営業** | Auto Dialer + ZRA | 通話分析、成功パターン把握 |
| **商談管理** | Salesforce連携 | 進捗可視化、リスク早期検知 |
| **プレゼン分析** | ZRA会話分析 | 企業の関心事項を定量化 |

---

<a id="zoom-for-education"></a>
### 7.3 Zoom for Education

#### 概要

教育機関向けの特化機能。K-12（小中高）、高等教育、EdTech企業向け。

#### 主要機能

##### Education向け会議機能
- **授業テンプレート**: 出欠管理、小テスト統合
- **ブレイクアウトルーム**: グループワーク
- **ホワイトボード**: 協働学習
- **投票・Q&A**: 理解度チェック
- **Focus Mode**: 生徒は自分だけ表示（試験等）

##### LMS連携
- **Canvas Connector（2026年1月〜）**:
  - 学生・教員がAI Companionパネルから課題、成績、お知らせを検索
  - 例: 「金曜日に何が締切?」
- **Moodle、Blackboard、Google Classroom**: 会議リンク自動挿入

##### Zoom Revenue Accelerator for Education（大分モデル2.0）
- **授業品質可視化**: Talk/Listen比率、質問の質、感情分析
- **Custom Summary**: オープンクエスチョン検出、足場がけ分析
- **Playbook**: 標準授業パターン、ベテラン教員のモデル化
- **Scorecard**: 小中高別の評価項目、100点満点スコア
- **Indicator**: リアルタイムNG検出、いじめ関連ワード監視

##### Clinical Notes Enhancements（医療教育向け、2026年1月〜）
- **説明**: 臨床ノートをモバイルで下書き・レビュー、EHRへ直接送信
- **用途**: ベッドサイドで記録、残業削減

#### 自治体向けユースケース（教育委員会）

| シーン | 活用方法 | 効果 |
|---|---|---|
| **遠隔授業** | Zoom Rooms + ZRA | 授業品質可視化、教員育成 |
| **GIGA端末活用** | Zoom Meetings | 1人1台端末での双方向授業 |
| **保護者会** | ウェビナー | オンライン参加、録画公開 |
| **教員研修** | Zoom Clips | 優良授業例を録画・共有 |
| **特別支援教育** | 個別指導ビデオ | 保護者とのコミュニケーション強化 |

---

<a id="zoom-for-government"></a>
### 7.4 Zoom for Government

#### 概要

政府・公共機関向けの高セキュリティ版Zoom。米国FedRAMP、CJIS、ILレベル認証取得。

#### 主要機能

##### セキュリティ
- **FedRAMP Moderate**: 米国連邦政府基準
- **CJIS**: 刑事司法情報システム対応
- **IL-4認証（Zoom for Defense、2025年12月〜）**: 米国国防総省向け、NIPRNet対応

##### データ主権
- **米国データセンター**: データは米国内に保存
- **日本データセンター**: 日本政府機関向けオプション

##### Zoom Workplace for Frontline (Government)（2026年1月〜）
- **説明**: 現場職員向けPush-to-Talk、ビデオ通話、セキュアメッセージング
- **用途**: 警察、消防、道路管理等

#### 日本の自治体への適用

- **LGWAN（総合行政ネットワーク）**: 原則外部サービス不可
- **対応策**:
  1. **ハイブリッド**: 庁内LANでZoom Rooms、外部接続はLGWAN-ASP経由
  2. **ZRA活用**: インターネット経由でZRAにアクセス、分析データは閉域網に保存
  3. **Zoom Phone**: 050番号でBCP対策、LGWANと併用

#### 自治体向けユースケース

| シーン | 活用方法 | 効果 |
|---|---|---|
| **首長・幹部会議** | 高セキュリティ版 | 機密情報の安全な共有 |
| **防災無線代替** | Frontline PTT | 現場職員との即時通信 |
| **LGWAN対応** | ハイブリッド構成 | 規制遵守しつつDX推進 |

---

<a id="zoom-for-healthcare"></a>
### 7.5 Zoom for Healthcare

#### 概要

医療機関向けの遠隔医療ソリューション。HIPAA準拠。

#### 主要機能

##### Telehealth（遠隔医療）
- **バーチャル待合室**: 患者待機スペース
- **HIPAA準拠**: 患者情報保護
- **処方箋統合**: 電子処方箋システム連携
- **EHR連携**: Epic、Cerner等と連携

##### Clinical Notes（臨床ノート、2026年1月拡張）
- **モバイル対応**: ベッドサイドで下書き・レビュー
- **EHR直接送信**: AI生成ドキュメントをEHRへ
- **用途**: 記録業務の時間外削減

##### Zoom Virtual Agent: Epic Integration (SpinSci経由)
- **説明**: Epic EHRと連携した自動予約・処方箋更新
- **用途**: 患者セルフサービス、スタッフ負担軽減

#### 自治体向けユースケース（保健所、市立病院）

| シーン | 活用方法 | 効果 |
|---|---|---|
| **遠隔診療** | Telehealth | へき地医療、通院困難者支援 |
| **健康相談** | ビデオ通話 | 保健師との顔の見える相談 |
| **Virtual Agent** | 予約自動化 | 24時間予約受付 |

---

<a id="developer-tools"></a>
## 8. 開発者向けツール

### 8.1 Zoom API

#### 主要API

##### Zoom Meetings API
- **エンドポイント**:
  - `POST /users/{userId}/meetings`: 会議作成
  - `GET /meetings/{meetingId}`: 会議情報取得
  - `GET /users/{userId}/recordings`: 録画一覧
  - `GET /meetings/{meetingId}/recordings`: 特定会議の録画

##### Zoom Phone API
- **エンドポイント**:
  - `GET /phone/users/{userId}/call_logs`: 通話履歴
  - `GET /phone/users/{userId}/recordings`: 通話録音
  - `POST /phone/users/{userId}/calls`: 通話開始

##### Zoom Revenue Accelerator API
- **エンドポイント**:
  - `GET /revenue_accelerator/conversations`: 会話一覧
  - `GET /revenue_accelerator/conversations/{conversationId}`: 会話詳細
  - `GET /revenue_accelerator/analytics`: 分析データ
  - `GET /revenue_accelerator/transcripts/{conversationId}`: トランスクリプトダウンロード

##### AI Companion API
- **エンドポイント**:
  - `GET /meetings/{meetingId}/meeting_summary`: 会議要約
  - `GET /phone/users/{userId}/call_summary`: 通話要約

### 8.2 Zoom SDK

#### Video SDK
- **用途**: カスタムビデオアプリへのZoom機能埋め込み
- **機能**: ビデオ通話、画面共有、レコーディング、AI Companion
- **Real-Time Media Streams (RTMS)（2025年12月〜）**:
  - ライブ音声、ビデオ、トランスクリプトのストリームにアクセス
  - 用途: リアルタイム家庭教師AI、医療ボット等

#### Meeting SDK
- **用途**: 既存アプリへZoom会議機能統合
- **プラットフォーム**: Web、iOS、Android、Windows、macOS

#### Zoom Apps SDK
- **用途**: Zoom内で動作するアプリ開発
- **例**: CRMアプリ、プロジェクト管理アプリ、投票アプリ

### 8.3 Webhooks

#### イベント通知
- **会議開始・終了**: `meeting.started`, `meeting.ended`
- **参加者参加・退出**: `meeting.participant_joined`, `meeting.participant_left`
- **録画完了**: `recording.completed`
- **通話終了**: `phone.callee_ended`
- **ZRA分析完了**: `revenue_accelerator.conversation_analyzed`

### 8.4 Antigravity開発での活用

#### データモデル例（Python）

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class Municipality:
    """自治体マスター"""
    lg_code: str  # 自治体コード
    name: str  # 自治体名
    fin_index: float  # 財政力指数
    staff_num: int  # 職員数
    transcription_budget: int  # 議事録予算（円/年）
    mayor_priority: str  # 首長の優先施策（DX、防災等）
    gov_alignment: bool  # 国策との整合性
    edu_giga_status: str  # GIGA端末状況
    network_policy: str  # LGWAN接続ポリシー
    m365_level: str  # Microsoft 365ライセンス（None/E3/E5）
    pbx_expiry: Optional[datetime]  # PBX更新期限
    target_pattern: str  # 勝利パターン（ZP/ZP+ZRA/ZM+ZRA/Full）
    winning_logic: str  # 提案ロジック

@dataclass
class CallRecord:
    """通話・会議記録（Zoom Phone + AI Companion + ZRA）"""
    call_id: str
    user_id: str
    duration: int  # 秒
    timestamp: datetime
    aic_summary: Optional[str]  # AI Companion要約
    zra_transcript: Optional[str]  # ZRA全文字起こし
    zra_metrics: Optional[Dict]  # Talk/Listen比率等
    sentiment_score: Optional[float]  # 感情スコア（-1〜1）
    risk_signals: List[str]  # リスクフラグ
    playbook_results: Optional[Dict]  # Playbook抽出結果
    scorecard_score: Optional[float]  # Scorecard評価

@dataclass
class MeetingRecord:
    """会議記録（Zoom Meetings + AI Companion + ZRA）"""
    meeting_id: str
    topic: str
    duration: int
    timestamp: datetime
    participants: List[str]
    aic_summary: Optional[str]
    zra_transcript: Optional[str]
    zra_metrics: Optional[Dict]
    sentiment_score: Optional[float]
    topics_discussed: List[str]  # トピック
    action_items: List[str]  # アクションアイテム
    recording_url: Optional[str]
```

#### API統合例（Python + FastAPI）

```python
from fastapi import FastAPI, HTTPException
import httpx
from typing import List

app = FastAPI()

ZOOM_API_BASE = "https://api.zoom.us/v2"
ZOOM_ACCESS_TOKEN = "your_zoom_access_token"

async def get_zoom_phone_call_logs(user_id: str) -> List[dict]:
    """Zoom Phone通話履歴取得"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ZOOM_API_BASE}/phone/users/{user_id}/call_logs",
            headers={"Authorization": f"Bearer {ZOOM_ACCESS_TOKEN}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Zoom API error")
        return response.json()["call_logs"]

async def get_zra_conversation(conversation_id: str) -> dict:
    """ZRA会話詳細取得"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ZOOM_API_BASE}/revenue_accelerator/conversations/{conversation_id}",
            headers={"Authorization": f"Bearer {ZOOM_ACCESS_TOKEN}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="ZRA API error")
        return response.json()

@app.get("/api/call_analysis/{user_id}")
async def analyze_user_calls(user_id: str):
    """ユーザーの通話をZRA分析"""
    call_logs = await get_zoom_phone_call_logs(user_id)
    analysis_results = []
    for call in call_logs:
        if call.get("zra_conversation_id"):
            zra_data = await get_zra_conversation(call["zra_conversation_id"])
            analysis_results.append({
                "call_id": call["id"],
                "duration": call["duration"],
                "summary": call.get("aic_summary"),
                "transcript": zra_data.get("transcript"),
                "metrics": zra_data.get("metrics"),
                "sentiment": zra_data.get("sentiment_score")
            })
    return {"user_id": user_id, "total_calls": len(call_logs), "analyses": analysis_results}
```

#### 権限管理（RBAC）

```python
from enum import Enum

class UserRole(Enum):
    MUNICIPAL_STAFF = "municipal_staff"  # 自治体職員（自分の会話のみ）
    DEPARTMENT_MANAGER = "department_manager"  # 部課長（部下の会話）
    MAYOR_OFFICE = "mayor_office"  # 市長室（全会話）
    ZOOM_SALES = "zoom_sales"  # Zoom営業（自治体の勝利パターン分析）

def can_access_conversation(user_role: UserRole, target_user_id: str, requester_id: str) -> bool:
    """会話アクセス権限チェック"""
    if user_role == UserRole.MAYOR_OFFICE or user_role == UserRole.ZOOM_SALES:
        return True
    elif user_role == UserRole.DEPARTMENT_MANAGER:
        # 部下リストから判定（実装略）
        return target_user_id in get_subordinates(requester_id)
    else:
        return target_user_id == requester_id
```

---

<a id="strategic-patterns"></a>
## 9. 自治体向け戦略的活用パターン

### 9.1 4つの勝利パターン（再掲・詳細版）

| パターン | ターゲット | ソリューション | 提案の鍵 | 予算規模 |
|---|---|---|---|---|
| **Pattern 1: ZP Blue Ocean** | M365 E3以下、PBXなし、財政標準 | Zoom Phone (ZP) | 低コスト、高機能、BCP「Teamsに電話ないですよね?」 | 小〜中 |
| **Pattern 2: ZRA Booster** | 財政力あり、議事録・窓口負担大 | ZP + ZRA | 働き方改革、議事録外注費削減、窓口対応品質向上、AIC無料訴求 | 中〜大 |
| **Pattern 3: Education DX** | 教育委員会、GIGA端末更新期 | ZM + ZRA | 教育の質可視化（大分モデル2.0）、遠隔授業、教員育成 | 中 |
| **Pattern 4: Surgical Strike** | M365 E5、PBXあり、二重投資嫌い | ZRA単体/特定部署 | 局所最適化、Teams Phoneでは不可能な高度分析、教育または窓口特化 | 小〜中 |

### 9.2 M365戦略との関係

#### M365ライセンスレベル別アプローチ

##### M365なし（Blue Ocean）
- **戦略**: ZP/ZRA/ZMフルスタック提案
- **強み**: Microsoft依存なし、Zoomのみで完結
- **訴求**: コスト最適、統合プラットフォーム

##### M365 ≤ E3
- **戦略**: Teams Phone機能なし→ZP統合提案
- **強み**: TeamsとZoomの共存（Teams会議 + Zoom Phone）
- **訴求**: 「Teamsに電話機能を追加しませんか?」

##### M365 = E5
- **戦略**: 差別化・特化型
- **強み**: ZRAの高度分析（Teams Phoneにはない）
- **訴求**: 
  - **教育**: ZM + ZRAで授業品質可視化
  - **窓口**: ZP + ZRAで対応分析・クレーム検知
  - **議事録**: ZRA文字起こし・分析

### 9.3 データ獲得優先順位

#### Phase 1: Base Data（無料API）
- **e-Stat（総務省統計局）**: 財政力指数、職員数、人口、標準財政規模
- **DNS/Web検索**: M365利用有無、E5フラグ

#### Phase 2: Budget Layer（予算・補助金）
- **デジタル庁MCP**: 補助金情報
- **自治体予算PDF/HTML**: 予算書スクレイピング→用途分類

#### Phase 3: Intelligence Layer（インテント）
- **Google Custom Search API**: 首長発言、入札情報
- **AI分析**: 4つの勝利パターンへ自動分類

### 9.4 用途分類（5カテゴリ）

1. **働き方改革**: テレワーク、会議効率化、時間削減
2. **窓口DX**: 住民サービス、オンライン申請、AI対応
3. **BCP・防災**: 災害対策、遠隔勤務、安否確認
4. **内部ICT統合**: 既存システム連携、データ統合
5. **遠隔教育**: GIGA端末、オンライン授業、教育品質

**重要**: 用途に合致しない予算は得点ゼロ（Antigravity設計思想）

### 9.5 Sales Playbook自動生成

#### 優先順位（Tab 5）

1. **ZP（Zoom Phone）**: 窓口DXの核、AI Concierge含む（SMS除く）
2. **ZP + ZRA**
3. **ZM + ZRA**
4. **ZM + ZR + ZRA**
5. **All-in（ZM + ZP + AI Concierge + AIC + ZRA）**

#### 自動生成項目

- **提案根拠**: なぜこの自治体にこの製品か（予算・発言・財政力から）
- **ターゲット部署**: どこにアプローチすべきか
- **次のアクション**: 初回アポ取得の推奨手法
- **想定反論と対処**: 「予算がない」「Teams使ってる」等への返し

#### 例（Pattern 2: ZP + ZRA Booster）

**提案根拠**:
- 財政力指数 0.95（高）
- 議事録外注費 ¥3,500,000/年（高額）
- 窓口クレーム対応の負担増（首長発言で言及）

**ターゲット部署**:
- 情報政策課（予算元）
- 総務課（働き方改革担当）
- 市民課（窓口DX当事者）

**次のアクション**:
1. 情報政策課長にメール（大分モデル2.0資料添付）
2. ZRA ROI試算書提出（議事録削減 + 残業削減）
3. デモ実施（実際の議会録画をZRA分析→効果実感）

**想定反論と対処**:
- 「予算が高い」→ROI試算で3年で回収
- 「既存の議事録業者がいる」→品質・検索性で差別化
- 「Teams使ってる」→ZRAはTeams Phoneにない高度分析

---

<a id="api-integration"></a>
## 10. API・データモデル・統合

### 10.1 主要APIエンドポイント（再掲）

#### Zoom Meetings API
- `GET /users/{userId}/meetings`: ユーザーの会議一覧
- `GET /meetings/{meetingId}/recordings`: 会議録画
- `GET /past_meetings/{meetingId}/participants`: 参加者リスト

#### Zoom Phone API
- `GET /phone/users/{userId}/call_logs`: 通話履歴
- `GET /phone/users/{userId}/recordings`: 通話録音
- `GET /phone/call_history`: 組織全体の通話履歴

#### Zoom Revenue Accelerator API
- `GET /revenue_accelerator/conversations`: 会話一覧
- `GET /revenue_accelerator/conversations/{conversationId}`: 会話詳細
- `GET /revenue_accelerator/conversations/{conversationId}/transcript`: トランスクリプト
- `GET /revenue_accelerator/analytics`: 集約分析データ
- `POST /revenue_accelerator/custom_summaries`: カスタム要約作成
- `GET /revenue_accelerator/playbooks`: Playbook一覧
- `GET /revenue_accelerator/scorecards`: Scorecard一覧

#### AI Companion API
- `GET /meetings/{meetingId}/meeting_summary`: 会議要約
- `GET /phone/users/{userId}/calls/{callId}/summary`: 通話要約

### 10.2 Webhook設定

#### 会議イベント
```json
{
  "event": "meeting.ended",
  "payload": {
    "meeting_id": "123456789",
    "topic": "庁議",
    "start_time": "2026-02-13T10:00:00Z",
    "duration": 90,
    "participants_count": 12
  }
}
```

#### 通話終了イベント
```json
{
  "event": "phone.call_ended",
  "payload": {
    "call_id": "987654321",
    "caller": "+81-50-1234-5678",
    "callee": "+81-50-8765-4321",
    "duration": 300,
    "aic_summary_available": true,
    "zra_conversation_id": "conv_abc123"
  }
}
```

#### ZRA分析完了イベント
```json
{
  "event": "revenue_accelerator.conversation_analyzed",
  "payload": {
    "conversation_id": "conv_abc123",
    "transcript_url": "https://api.zoom.us/v2/revenue_accelerator/conversations/conv_abc123/transcript",
    "metrics": {
      "talk_listen_ratio": 0.35,
      "sentiment_score": 0.72,
      "risk_signals": ["next_step_missing"]
    }
  }
}
```

### 10.3 ストレージ戦略

#### 短期ストレージ（30日）
- **対象**: 録画・録音の生データ（映像・音声）
- **理由**: ストレージコスト削減
- **削除前**: ZRA分析完了、トランスクリプト保存

#### 長期ストレージ（数年）
- **対象**: トランスクリプト、要約、分析データ、メトリクス
- **理由**: トレンド分析、長期的知見抽出
- **例**: 
  - 過去3年間の窓口クレーム分析
  - 教員の成長曲線（Scorecard経年比較）

#### バックアップ・アーカイブ
- **対象**: 重要会議（議会、首長会議）の録画
- **ストレージ**: AWS S3 Glacier、Azure Archive Storage
- **アクセス**: 必要時にリストア

### 10.4 セキュリティとコンプライアンス

#### 暗号化
- **通信**: TLS 1.2以上
- **保存**: AES-256

#### アクセス制御
- **RBAC**: ロールベースアクセス制御（前述）
- **MFA**: 多要素認証
- **SSO**: SAML 2.0、OAuth 2.0

#### 監査ログ
- **記録項目**: ユーザーID、アクション、タイムスタンプ、IPアドレス
- **保存期間**: 3年（日本の行政文書保存規則に準拠）

#### コンプライアンス
- **GDPR**: EU居住者データ保護（該当する場合）
- **個人情報保護法**: 日本の法規制遵守
- **自治体情報セキュリティポリシー**: 各自治体の規程に準拠

---

<a id="references"></a>
## 11. 参考文献

### Hub内ドキュメント

1. **Zoom製品群とAI活用戦略.pdf** (Hub)
   - ZoomエコシステムのAI統合戦略
   - データ資産化の概念
   - AIC、AI Concierge、ZRAの詳細比較

2. **oita_model_2_education_dx_20260129134628.pdf** (Hub)
   - 大分モデル2.0：ZRAによる教育DX革命
   - Custom Summary、Playbook、Scorecard、Indicatorの教育向け活用

3. **zoom_phone_aic_vs_zra_comparison.md** (/Antigravity関連/)
   - AI CompanionとZRAの詳細比較
   - 自治体・教育・営業向けメリット（各20項目）
   - 実装ノート、API、データモデル

4. **Zoom Revenue Accelerator - 基本機能紹介及び設定手順書.pdf** (AIドライブ)
5. **Zoom Revenue Accelerator -CSM_日本語マニュアル-.pdf** (AIドライブ)
6. **Zoom Revenue Accelerator 包括的調査報告書.pdf** (AIドライブ)
7. **Zoom Technical Library＿AI.pdf** (AIドライブ)

### セッション履歴

- Session 1634a73e-73c5-4f27-9a10-99c24c515952: Zoom-ai-coreアプリの概要解説
- Session 7853d3e9-e9a8-4bac-9b07-d2828f902ab5: Genspark AI キカガクアプリ自動デザイン
- Session 84b19b4c-eba5-4a6f-82df-e25052a7f763: Zoom公共営業「売れる順診断」開発・運用戦略策定
- Session 5bb9efd1-b82c-4baa-a13c-4ada2187f357: Tab5 B方式・価値KPI序列・制約事項の再確認

### 外部リソース

1. **Zoom公式サイト**
   - https://www.zoom.com/en/products/collaboration-tools/features/
   - https://www.zoom.com/en/products/whats-new/

2. **Zoom製品別ページ**
   - Zoom Meetings: https://www.zoom.com/en/products/virtual-meetings/
   - Zoom Phone: https://www.zoom.com/en/products/voip-phone/
   - Zoom Webinars: https://www.zoom.com/en/products/webinars/
   - Zoom Events: https://www.zoom.com/en/products/event-platform/
   - Zoom Contact Center: https://www.zoom.com/en/products/contact-center/
   - Zoom Workplace: https://www.zoom.com/en/products/collaboration-tools/

3. **AI Companion**
   - https://ai.zoom.us/
   - https://www.zoom.com/en/products/ai-assistant/

4. **Zoom開発者ドキュメント**
   - https://developers.zoom.us/docs/
   - https://developers.zoom.us/docs/api/
   - https://developers.zoom.us/docs/video-sdk/
   - https://developers.zoom.us/docs/rooms/

5. **外部調査（2026年最新）**
   - G2 Zoom Reviews: https://www.g2.com/products/zoom-meetings/reviews
   - Gartner Magic Quadrant for UCaaS

---

## 付録: 用語集

| 用語 | 説明 |
|---|---|
| **AIC** | AI Companion。無料のAIアシスタント |
| **ZRA** | Zoom Revenue Accelerator。有料の高度会話分析 |
| **ZP** | Zoom Phone。クラウド電話システム |
| **ZM** | Zoom Meetings。ビデオ会議 |
| **UCaaS** | Unified Communications as a Service。統合通信サービス |
| **RBAC** | Role-Based Access Control。ロールベースアクセス制御 |
| **IVR** | Interactive Voice Response。自動音声応答 |
| **PTT** | Push-to-Talk。ワンタッチ音声通信 |
| **E2EE** | End-to-End Encryption。エンドツーエンド暗号化 |
| **LMS** | Learning Management System。学習管理システム |
| **EHR** | Electronic Health Record。電子カルテ |
| **LGWAN** | 総合行政ネットワーク |
| **GIGA** | GIGAスクール構想。1人1台端末 |
| **M365** | Microsoft 365 |
| **BCP** | Business Continuity Plan。事業継続計画 |
| **DX** | Digital Transformation。デジタルトランスフォーメーション |
| **Talk/Listen Ratio** | 話す時間/聞く時間の比率 |
| **Playbook** | 会話から特定項目を自動抽出する設定 |
| **Scorecard** | 会話品質を定量評価する仕組み |
| **Indicator** | リアルタイムNG検出 |
| **Deflection** | AIによる自動応答（人間エージェントへの転送を回避） |

---

## 最後に

このドキュメントは、Antigravity IDE開発チームがZoom製品群のすべての機能を理解し、自治体向け営業戦略に活用するために作成されました。

### 次のアクション

1. **Antigravity IDEへ渡す**: このmdファイルをAntigravityプロジェクトに統合
2. **API実装**: Zoom Phone、ZRA、AI Companion APIをAntigravityバックエンドに統合
3. **データモデル実装**: Municipality、CallRecord、MeetingRecord等のデータベーススキーマ作成
4. **UI開発**: 6タブ構成（ヒートマップ、自治体診断、勝利パターン、予算、Playbook、技術可視化）+Admin
5. **夜間バッチ**: 1,918自治体の軽量チェック→深掘りクロール→スコアリング+Playbook生成
6. **テスト**: 大分県、財政力指数上位自治体でPilot実施
7. **展開**: 全国1,918自治体へスケール

---

**作成者**: Genspark AI  
**更新日**: 2026年2月13日  
**バージョン**: 1.0  
**問い合わせ**: Antigravity IDE開発チーム

---

