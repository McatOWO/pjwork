from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import os
import re
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECEIVED_DIR = os.path.join(BASE_DIR, "received_reports")
os.makedirs(RECEIVED_DIR, exist_ok=True)

@app.get("/")
def index():
    reports = []
    for fn in sorted(os.listdir(RECEIVED_DIR), reverse=True):
        if not fn.endswith(".txt"):
            continue
        path = os.path.join(RECEIVED_DIR, fn)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            mtime = ""
        meta = parse_meta(path)
        reports.append({"filename": fn, "mtime": mtime, **meta})
    return render_template("index.html", reports=reports)

@app.post("/api/receive_report")
def receive_report():
    data = request.get_json(silent=True) or {}
    filename = (data.get("filename") or "").strip()
    content = data.get("content") or ""

    if not filename or not filename.endswith(".txt"):
        filename = f"cleaning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    # 安全なファイル名に整形
    filename = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)
    path = os.path.join(RECEIVED_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return jsonify({"ok": True, "saved_as": filename, "view_url": f"/reports/{filename}"})

@app.get("/reports/<path:filename>")
def view_report(filename):
    path = os.path.join(RECEIVED_DIR, filename)
    if not os.path.isfile(path):
        abort(404)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    meta = parse_meta(path)
    return render_template("report.html", filename=filename, text=text, meta=meta)

@app.get("/download/<path:filename>")
def download_report(filename):
    return send_from_directory(RECEIVED_DIR, filename, as_attachment=True)

def parse_meta(path):
    meta = {"roomId":"", "cleanerId":"", "totalScore":"", "finishedAt":""}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for _ in range(40):
                line = f.readline()
                if not line:
                    break
                line=line.strip()
                if line.startswith("roomId:"):
                    meta["roomId"]=line.split(":",1)[1].strip()
                elif line.startswith("cleanerId:"):
                    meta["cleanerId"]=line.split(":",1)[1].strip()
                elif line.startswith("totalScore:"):
                    meta["totalScore"]=line.split(":",1)[1].strip()
                elif line.startswith("finishedAt:"):
                    meta["finishedAt"]=line.split(":",1)[1].strip()
    except Exception:
        pass
    return meta

if __name__ == "__main__":
    # 受信ポート例: 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
