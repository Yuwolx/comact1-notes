# -*- coding: utf-8 -*-
# 정적 사이트용 암호 게이트 빌더 (StatiCrypt 방식)
# 평문 앱 HTML을 AES-256-GCM으로 암호화하여, 암호 없이는 내용이 암호문으로만 보이는
# 잠금 페이지(index.html)를 생성한다. 복호화는 브라우저 WebCrypto로 수행.
#
# 사용: CBT_PW="암호" python _build/build_gate.py <평문HTML> <출력HTML>
import os, sys, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

ITER = 200000
src = sys.argv[1] if len(sys.argv) > 1 else "_source/app.html"
out = sys.argv[2] if len(sys.argv) > 2 else "index.html"
pw = os.environ.get("CBT_PW")
if not pw:
    print("ERROR: 환경변수 CBT_PW(암호)가 필요합니다."); sys.exit(1)

plain = open(src, encoding="utf-8").read().encode("utf-8")
salt = os.urandom(16)
iv = os.urandom(12)
key = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITER, dklen=32)
ct = AESGCM(key).encrypt(iv, plain, None)  # ciphertext || 16-byte tag
b64 = lambda b: base64.b64encode(b).decode()
payload = {"salt": b64(salt), "iv": b64(iv), "ct": b64(ct), "iters": ITER}

GATE = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>컴퓨터활용능력 1급 개념집 · 잠금</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,__FAV__">
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
 background:#0a1530;color:#fff;font-family:"Inter",system-ui,"Malgun Gothic","맑은 고딕",sans-serif}
.box{width:min(92vw,420px);background:#0f1a35;border:1px solid #1f3161;border-radius:16px;
 padding:34px 30px;text-align:center;box-shadow:rgba(0,0,0,.35) 0 24px 48px -8px}
.lock{font-size:34px;margin-bottom:8px}
h1{font-size:20px;margin:6px 0 4px;letter-spacing:-.5px}
p.sub{margin:0 0 22px;font-size:13px;color:#aab3cc;line-height:1.6}
input{width:100%;height:46px;padding:0 14px;border-radius:10px;border:1px solid #2b3f73;
 background:#0a1530;color:#fff;font-size:15px;outline:none}
input:focus{border-color:#5645d4}
button{width:100%;height:46px;margin-top:12px;border:none;border-radius:10px;background:#5645d4;
 color:#fff;font-size:15px;font-weight:600;cursor:pointer}
button:hover{background:#4534b3}
.err{color:#ff8a9c;font-size:13px;margin-top:12px;min-height:16px}
.hint{margin-top:18px;font-size:12px;color:#7a86a6}
</style></head>
<body>
<div class="box">
  <div class="lock">🔒</div>
  <h1>컴퓨터활용능력 1급 개념집</h1>
  <p class="sub">구매하신 분께 제공된 <b>입장 암호</b>를 입력하세요.</p>
  <form id="f" autocomplete="off">
    <input id="pw" type="password" placeholder="입장 암호" autofocus>
    <button type="submit" id="go">입장</button>
    <div class="err" id="err"></div>
  </form>
  <div class="hint">암호는 기기 종류와 무관하게 동일합니다.</div>
</div>
<script id="enc" type="application/json">__PAYLOAD__</script>
<script>
(function(){
  var enc=JSON.parse(document.getElementById('enc').textContent);
  var d=function(s){return Uint8Array.from(atob(s),function(c){return c.charCodeAt(0);});};
  async function unlock(pw){
    var km=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
    var key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:d(enc.salt),iterations:enc.iters,hash:'SHA-256'},km,{name:'AES-GCM',length:256},false,['decrypt']);
    var pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:d(enc.iv)},key,d(enc.ct));
    return new TextDecoder().decode(pt);
  }
  document.getElementById('f').addEventListener('submit',async function(e){
    e.preventDefault();
    var err=document.getElementById('err'),go=document.getElementById('go');
    err.textContent='';go.textContent='확인 중…';go.disabled=true;
    try{
      var html=await unlock(document.getElementById('pw').value);
      document.open();document.write(html);document.close();
    }catch(_){
      err.textContent='암호가 올바르지 않습니다.';go.textContent='입장';go.disabled=false;
      document.getElementById('pw').select();
    }
  });
})();
</script>
</body></html>"""

# 파비콘(SVG) 재사용
fav_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="7" fill="#0a1530"/>'
    '<rect x="7" y="7" width="8" height="8" rx="2" fill="#5645d4"/>'
    '<rect x="17" y="7" width="8" height="8" rx="2" fill="#ff64c8"/>'
    '<rect x="7" y="17" width="8" height="8" rx="2" fill="#2a9d99"/>'
    '<rect x="17" y="17" width="8" height="8" rx="2" fill="#f5d75e"/></svg>')
fav_b64 = base64.b64encode(fav_svg.encode()).decode()

html = (GATE.replace("__PAYLOAD__", json.dumps(payload))
            .replace("__FAV__", fav_b64))
open(out, "w", encoding="utf-8").write(html)
print("wrote gate:", out, "|", round(os.path.getsize(out)/1024,1), "KB")
print("payload ct bytes:", len(ct), "| iters:", ITER)
