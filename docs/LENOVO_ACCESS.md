# Lenovo Tiny 接続情報

このドキュメントは、Lenovo Tiny (Edge Server) への接続方法をまとめたものです。

## 接続の基本情報
- **ホスト名 / IP**: `100.107.246.40` (Tailscale)
- **OS**: Windows 10/11 Pro (WSL2搭載)
- **ユーザー名 (Windows)**: `onodera`
- **パスワード**: `Zoom5145`

## 接続手順 (SSH)

Antigravityのターミナルやローカルマシンから以下のコマンドで接続します。

```bash
ssh onodera@100.107.246.40
```

パスワードを聞かれたら `Zoom5145` を入力してください。

## WSL (Ubuntu) へのアクセス方法

SSH接続後はWindowsのPowerShell環境に入ります。そこからWSLのUbuntu環境に入るには以下のコマンドを実行します。

```powershell
wsl
```

または、最初からWSLでコマンドを実行したい場合は：

```bash
ssh onodera@100.107.246.40 "wsl <linux-command>"
```

## 接続構成の全体像

接続は2段階になっています：

```
Mac/ターミナル
  └─ ssh onodera@100.107.246.40  → Windows PowerShell
                                      └─ wsl              → Ubuntu (WSL2)
```

## トラブルシューティング

もし `ubuntu@100.107.246.40` で接続しようとしてパスワードが通らない場合は、Windowsユーザー (`onodera`) で接続してからWSLに入ってください。WSL側のSSHサーバーが別途設定されていない限り、Windows経由でのアクセスが基本となります。

### SSH接続が繰り返し失敗する場合の確認手順

**ステップ1: まずローカルから接続テスト**
```bash
ssh -o ConnectTimeout=10 onodera@100.107.246.40 "echo connected"
```

**ステップ2: 原因の切り分け**

| 症状 | 原因候補 | 対処 |
|------|----------|------|
| タイムアウト（応答なし） | Tailscaleが切れている / Windows自体がスリープ | 物理的に画面を確認してスリープ解除 |
| `Connection refused` | Windows側のSSHサービスが停止 | Windowsを再起動 |
| `Permission denied` | Fail2banにブロックされた（パスワード失敗が続いた） | しばらく待つか物理アクセスでFail2banリセット |
| SSHは入れるがWSLが応答しない | WSL2が停止している | `wsl --shutdown` → `wsl` で再起動 |

**ステップ3: WSL動作確認**
```bash
# SSHでWindows経由でWSLに1コマンド実行
ssh onodera@100.107.246.40 "wsl -- uname -a"
```
→ Linuxカーネル情報が返ってくれば正常。

**ステップ4: Fail2banがブロックしている場合（物理アクセス時）**
```powershell
# Windows PowerShell から
wsl -- sudo fail2ban-client status sshd
wsl -- sudo fail2ban-client set sshd unbanip <自分のIP>
```
