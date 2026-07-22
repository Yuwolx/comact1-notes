# -*- coding: utf-8 -*-
# 맛보기(무료 데모) 빌더: 전체 앱에서 제1과목 개념 + 샘플 문항만 남기고 잠금/구매안내 추가.
import re, json, sys, os

app = sys.argv[1] if len(sys.argv) > 1 else "_source/app.html"
qbank = sys.argv[2] if len(sys.argv) > 2 else "_source/qbank.json"
out = sys.argv[3] if len(sys.argv) > 3 else "demo/index.html"
EMAIL = "yuwolxx@gmail.com"

h = open(app, encoding="utf-8").read()
d = json.load(open(qbank, encoding="utf-8"))["questions"]

# --- 샘플 12문항 (1과목4 / 2과목 3+표1 / 3과목 3+표1) ---
def pick(subj, n, kind):
    r = []
    for q in d:
        if q["subject"] != subj: continue
        has = ("grid" in q) or ("table" in q)
        if kind == "text" and has: continue
        if kind == "grid" and "grid" not in q: continue
        if kind == "table" and "table" not in q: continue
        r.append(q)
        if len(r) >= n: break
    return r
sample = pick(1,"4" and 4,"text") + pick(2,3,"text") + pick(2,1,"grid") + pick(3,3,"text") + pick(3,1,"table")
sample_json = json.dumps({"questions": sample}, ensure_ascii=False)
h = re.sub(r'var RAW = \{.*?\};(\s*\n\s*var QBANK)',
           lambda m: 'var RAW = ' + sample_json + ';' + m.group(1), h, count=1, flags=re.DOTALL)

# --- 제2·3과목 + 부록 섹션 제거, 잠금 CTA로 대체 ---
LOCK = ('<section class="subject" id="lock">'
        '<div class="subject-h ap">\U0001F512 제2·3과목 + 전체 문제은행은 구매 후 이용</div>'
        '<div class="topic"><div class="body">'
        '<p>이 <b>맛보기</b>에는 <b>제1과목 개념</b>과 <b>샘플 12문항</b>(엑셀·DB 표 문제 포함)만 담겨 있어요.</p>'
        '<p><b>전체판 구성</b> — 3개 과목 개념집 + <b>484문항 모의고사</b>(자동 채점·합격 판정·오답 해설·응시 이력).</p>'
        '<p>구매·문의: <b>' + EMAIL + '</b></p>'
        '</div></div></section>')
h = re.sub(r'<section class="subject s2" id="s2">.*?</section>', LOCK, h, count=1, flags=re.DOTALL)
h = re.sub(r'<section class="subject s3" id="s3">.*?</section>', '', h, count=1, flags=re.DOTALL)
h = re.sub(r'<section class="subject" id="ap">.*?</section>', '', h, count=1, flags=re.DOTALL)

# --- 좌측 목차: 2·3과목·부록 그룹 제거 ---
h = re.sub(r'<h4>제2과목.*?(?=</nav>)',
           '<h4>전체판</h4>\n  <a href="#lock">\U0001F512 2·3과목 · 전체 문제</a>\n  ', h, count=1, flags=re.DOTALL)

# --- 상단 맛보기 리본 + CSS ---
ribbon_css = ('<style>#demoRibbon{background:linear-gradient(90deg,#5645d4,#7b3ff2);color:#fff;'
              'text-align:center;font-size:13.5px;padding:10px 16px;line-height:1.5}'
              '#demoRibbon a{color:#fff;font-weight:700;text-decoration:underline}</style>')
h = h.replace('</head>', ribbon_css + '</head>', 1)
ribbon = ('<div id="demoRibbon">\U0001F381 맛보기 버전 — 제1과목 개념 + 샘플 문항만 열려 있어요 · '
          '전체(3과목 + 484문항)는 구매 시 제공 · 문의 <a href="mailto:' + EMAIL + '">' + EMAIL + '</a></div>')
h = h.replace('<header class="top">', ribbon + '<header class="top">', 1)

# --- 모의고사 안내문을 맛보기용으로 ---
h = h.replace('개념집 내용을 바탕으로 한 4지선다 문제를 실전처럼 풀고 채점받으세요. 틀린 문항은 자동으로 <b>오답노트</b>에 모이고, 맞힐 때까지 다시 풀 수 있습니다. 응시 이력은 이 브라우저(localStorage)에만 저장되며 외부로 전송되지 않습니다. 시험 도중 새로고침하거나 창을 닫아도 이어서 풀 수 있습니다.',
              '맛보기 샘플 12문항으로 채점·해설·오답노트를 체험해 보세요. 전체판은 484문항으로 실전(과목당 20문항)까지 지원합니다. 응시 이력은 이 브라우저에만 저장됩니다.')

os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(h)
from collections import Counter
print("demo written:", out, "|", round(os.path.getsize(out)/1024,1), "KB")
print("sample questions:", len(sample), "| per-subject", dict(sorted(Counter(q['subject'] for q in sample).items())))
print("has grid:", any('grid' in q for q in sample), "| has table:", any('table' in q for q in sample))
