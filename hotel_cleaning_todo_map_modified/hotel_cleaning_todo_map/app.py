from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
import urllib.request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# 監査アプリ(受信側)のエンドポイント: 環境変数で指定
# 例: AUDITOR_ENDPOINT=http://127.0.0.1:5001/api/receive_report
AUDITOR_ENDPOINT = os.environ.get("AUDITOR_ENDPOINT", "").strip()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/report")
def api_report():
    data = request.get_json(silent=True) or {}
    report_id = uuid.uuid4().hex[:12]
    filename = f"cleaning_report_{report_id}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    # ===== テキスト化（監査側で読み込みやすい形式）=====
    lines = []
    lines.append("CLEANING_REPORT_V1")
    lines.append(f"report_id: {report_id}")
    lines.append(f"roomId: {data.get('roomId','')}")
    lines.append(f"cleanerId: {data.get('cleanerId','')}")
    lines.append(f"startedAt: {data.get('startedAt','')}")
    lines.append(f"finishedAt: {data.get('finishedAt','')}")
    lines.append(f"durationSeconds: {data.get('durationSeconds','')}")
    lines.append(f"totalScore: {data.get('totalScore','')}")
    lines.append("")
    lines.append("tasks:")
    tasks = data.get("tasks") or {}
    for tid, tinfo in tasks.items():
        status = (tinfo or {}).get("status","")
        score = (tinfo or {}).get("score","")
        checkedAt = (tinfo or {}).get("checkedAt","")
        notes = (tinfo or {}).get("notes","")
        lines.append(f"- id: {tid}")
        lines.append(f"  status: {status}")
        lines.append(f"  score: {score}")
        lines.append(f"  checkedAt: {checkedAt}")
        lines.append(f"  notes: {notes}")
    text = "\n".join(lines) + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    # ===== 送信（任意）=====
    sent = False
    send_error = ""
    if AUDITOR_ENDPOINT:
        try:
            payload = json_bytes({"filename": filename, "content": text})
            req = urllib.request.Request(
                AUDITOR_ENDPOINT,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                _ = resp.read()
            sent = True
        except Exception as e:
            send_error = str(e)

    return jsonify({
        "ok": True,
        "report_id": report_id,
        "filename": filename,
        "download_url": f"/reports/{filename}",
        "sent_to_auditor": sent,
        "send_error": send_error,
    })

@app.get("/reports/<path:filename>")
def download_report(filename):
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)

def json_bytes(obj):
    import json
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")
