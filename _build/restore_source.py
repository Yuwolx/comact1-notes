# -*- coding: utf-8 -*-
# 원본 복원기: 암호화된 게이트(index.html)에서 평문 앱을 복호화하여 _source/를 재구성한다.
# _source/app.html 과, 앱에 내장된 RAW 문제은행에서 _source/qbank.json 을 추출한다.
#
# 사용: CBT_PW="입장암호" python _build/restore_source.py [게이트HTML] [출력디렉터리]
import os, sys, re, json, base64, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

gate = sys.argv[1] if len(sys.argv) > 1 else "index.html"
outdir = sys.argv[2] if len(sys.argv) > 2 else "_source"
pw = os.environ.get("CBT_PW")
if not pw:
    print("ERROR: 환경변수 CBT_PW(입장 암호)가 필요합니다."); sys.exit(1)

html = open(gate, encoding="utf-8").read()
m = re.search(r'<script id="enc" type="application/json">(.*?)</script>', html, re.DOTALL)
if not m:
    print("ERROR: 게이트에서 암호화 페이로드를 찾지 못했습니다:", gate); sys.exit(1)
enc = json.loads(m.group(1))

d = lambda s: base64.b64decode(s)
key = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), d(enc["salt"]), enc["iters"], dklen=32)
try:
    plain = AESGCM(key).decrypt(d(enc["iv"]), d(enc["ct"]), None).decode("utf-8")
except Exception:
    print("ERROR: 복호화 실패 — 암호가 올바른지 확인하세요."); sys.exit(1)

os.makedirs(outdir, exist_ok=True)
app_path = os.path.join(outdir, "app.html")
open(app_path, "w", encoding="utf-8").write(plain)
print("wrote:", app_path, "|", round(os.path.getsize(app_path)/1024,1), "KB")

mq = re.search(r'var RAW = (\{.*?\});\s*\n\s*var QBANK', plain, re.DOTALL)
if mq:
    raw = json.loads(mq.group(1))
    q_path = os.path.join(outdir, "qbank.json")
    json.dump(raw, open(q_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote:", q_path, "| questions:", len(raw.get("questions", [])))
else:
    print("WARN: RAW 문제은행 패턴을 찾지 못해 qbank.json 은 만들지 못했습니다.")
