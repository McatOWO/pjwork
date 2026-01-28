# 監査人向け 清掃記録ビューア

## 起動
```bash
python app.py
```

- 受信URL: `http://127.0.0.1:5001/api/receive_report`
- 一覧画面: `http://127.0.0.1:5001/`

## 清掃アプリ側の送信設定（例）
Windows PowerShell:
```powershell
$env:AUDITOR_ENDPOINT="http://127.0.0.1:5001/api/receive_report"
python app.py
```
(清掃アプリ側を起動するターミナルで設定してください)
