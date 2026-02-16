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

## トラブルシューティング

もし `ubuntu@100.107.246.40` で接続しようとしてパスワードが通らない場合は、Windowsユーザー (`onodera`) で接続してからWSLに入ってください。WSL側のSSHサーバーが別途設定されていない限り、Windows経由でのアクセスが基本となります。
