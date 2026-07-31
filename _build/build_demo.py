# -*- coding: utf-8 -*-
# 맛보기(무료 데모) 빌더: 전체 앱에서 제1과목 개념 + 샘플 문항만 남기고 잠금/구매안내 추가.
# 모든 치환은 실패 시 즉시 AssertionError로 중단되며, 마지막에 산출물을 재파싱해
# 유료 콘텐츠(전체 문제은행·2/3과목 개념)가 새지 않았는지 검증한다.
# 샘플은 과목·유형별 풀의 앞쪽(기본 개념형)과 뒤쪽(신규 실전형)을 반반으로 뽑아
# 난이도 스펙트럼을 보여준다.
import re, json, sys, os

app = sys.argv[1] if len(sys.argv) > 1 else "_source/app.html"
qbank = sys.argv[2] if len(sys.argv) > 2 else "_source/qbank.json"
out = sys.argv[3] if len(sys.argv) > 3 else "demo/index.html"
EMAIL = "yuwolxx@gmail.com"
TOTAL = "659문항"

h = open(app, encoding="utf-8").read()
d = json.load(open(qbank, encoding="utf-8"))["questions"]


def sub1(pattern, repl, s, flags=0):
    """정확히 1회 치환. 무매치(앱 구조 변경 등)면 조용히 넘어가지 않고 즉시 실패한다."""
    new, n = re.subn(pattern, repl, s, count=1, flags=flags)
    assert n == 1, f"치환 실패(패턴 무매치): {pattern[:70]}"
    return new


def rep1(old, new, s):
    """문자열 리터럴 치환. 대상 문구가 앱에서 바뀌었으면 즉시 실패한다."""
    assert old in s, f"치환 실패(문구 없음): {old[:70]}"
    return s.replace(old, new, 1)


# --- 샘플 12문항 (1과목 4 / 2과목 3+표1 / 3과목 3+표1) ---
def pick(subj, n, kind):
    pool = []
    for q in d:
        if q["subject"] != subj: continue
        has = ("grid" in q) or ("table" in q)
        if kind == "text" and has: continue
        if kind == "grid" and "grid" not in q: continue
        if kind == "table" and "table" not in q: continue
        pool.append(q)
    assert len(pool) >= n, f"풀 부족: s{subj}/{kind} {len(pool)} < {n}"
    front = pool[:n // 2]
    back = pool[len(pool) - (n - len(front)):]
    return front + back

sample = pick(1, 4, "text") + pick(2, 3, "text") + pick(2, 1, "grid") + pick(3, 3, "text") + pick(3, 1, "table")
assert len(sample) == 12, f"샘플 추출 실패: {len(sample)}문항 (풀 부족)"
sample_json = json.dumps({"questions": sample}, ensure_ascii=False).replace("</", "<\\/")
h = sub1(r'var RAW = \{.*?\};(\s*\n\s*var QBANK)',
         lambda m: 'var RAW = ' + sample_json + ';' + m.group(1), h, flags=re.DOTALL)

# --- 데모/전체판 localStorage 분리 (같은 origin 공유로 인한 크래시·오염 방지) ---
h = rep1("var HKEY='cbt_history_v1', PKEY='cbt_progress_v1', SKEY='cbt_seen_v1', WKEY='cbt_wrong_v1';",
         "var HKEY='cbt_history_demo', PKEY='cbt_progress_demo', SKEY='cbt_seen_demo', WKEY='cbt_wrong_demo';", h)

# --- 제2·3과목 + 부록 섹션 제거, 잠금 CTA로 대체 ---
LOCK = ('<section class="subject" id="lock">'
        '<div class="subject-h ap">\U0001F512 제2·3과목 + 전체 문제은행은 구매 후 이용</div>'
        '<div class="topic"><div class="body">'
        '<p>이 <b>맛보기</b>에는 <b>제1과목 개념</b>과 <b>샘플 12문항</b>(엑셀·DB 표 문제 포함)만 담겨 있어요.</p>'
        '<p><b>전체판 구성</b> — 3개 과목 개념집 + <b>' + TOTAL + ' 모의고사</b>(자동 채점·합격 판정·오답노트·해설·응시 이력).</p>'
        '<p>구매·문의: <b>' + EMAIL + '</b></p>'
        '</div></div></section>')
h = sub1(r'<section class="subject s2" id="s2">.*?</section>', lambda m: LOCK, h, flags=re.DOTALL)
h = sub1(r'<section class="subject s3" id="s3">.*?</section>', lambda m: '', h, flags=re.DOTALL)
h = sub1(r'<section class="subject" id="ap">.*?</section>', lambda m: '', h, flags=re.DOTALL)

# --- 좌측 목차: 2·3과목·부록 그룹 제거 ---
h = sub1(r'<h4>제2과목.*?(?=</nav>)',
         lambda m: '<h4>전체판</h4>\n  <a href="#lock">\U0001F512 2·3과목 · 전체 문제</a>\n  ', h, flags=re.DOTALL)

# --- 상단 맛보기 리본 + CSS ---
ribbon_css = ('<style>#demoRibbon{background:linear-gradient(90deg,#5645d4,#7b3ff2);color:#fff;'
              'text-align:center;font-size:13.5px;padding:10px 16px;line-height:1.5}'
              '#demoRibbon a{color:#fff;font-weight:700;text-decoration:underline}</style>')
h = rep1('</head>', ribbon_css + '</head>', h)
ribbon = ('<div id="demoRibbon">\U0001F381 맛보기 버전 — 제1과목 개념 + 샘플 문항만 열려 있어요 · '
          '전체(3과목 + ' + TOTAL + ')는 구매 시 제공 · 문의 <a href="mailto:' + EMAIL + '">' + EMAIL + '</a></div>')
h = rep1('<header class="top">', ribbon + '<header class="top">', h)

# --- 모의고사 안내문을 맛보기용으로 ---
h = rep1('개념집 내용을 바탕으로 한 4지선다 문제를 실전처럼 풀고 채점받으세요. 틀린 문항은 자동으로 <b>오답노트</b>에 모이고, 맞힐 때까지 다시 풀 수 있습니다. 응시 이력은 이 브라우저(localStorage)에만 저장되며 외부로 전송되지 않습니다. 시험 도중 새로고침하거나 창을 닫아도 이어서 풀 수 있습니다.',
         '맛보기 샘플 12문항으로 채점·해설·오답노트를 체험해 보세요. 전체판은 ' + TOTAL + '으로 실전(과목당 20문항)까지 지원합니다. 응시 이력은 이 브라우저에만 저장됩니다.', h)

# --- 산출물 검증: 유료 콘텐츠 유출·치환 누락 최종 확인 ---
m = re.search(r'var RAW = (\{.*?\});\s*\n\s*var QBANK', h, flags=re.DOTALL)
assert m, "산출물에서 RAW 블록을 찾지 못함"
out_q = json.loads(m.group(1).replace("<\\/", "</"))["questions"]
assert len(out_q) == 12, f"산출물 문항 수 이상: {len(out_q)}"
assert 'id="s2"' not in h and 'id="s3"' not in h and '<section class="subject" id="ap"' not in h, "2·3과목/부록 섹션 잔존"
assert ("cbt_seen_v1" not in h and "cbt_history_v1" not in h and "cbt_progress_v1" not in h
        and "cbt_wrong_v1" not in h), "전체판 localStorage 키 잔존"
sample_texts = {q["q"] for q in sample}
leaked = [q["q"][:30] for q in d if q["q"] not in sample_texts and q["q"] in h]
assert not leaked, f"비샘플 문항 유출 {len(leaked)}건: {leaked[:3]}"

os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(h)
from collections import Counter
print("demo written:", out, "|", round(os.path.getsize(out)/1024, 1), "KB")
print("sample questions:", len(sample), "| per-subject", dict(sorted(Counter(q['subject'] for q in sample).items())))
print("has grid:", any('grid' in q for q in sample), "| has table:", any('table' in q for q in sample))
print("verify: 문항 12/12, 2·3과목 섹션 제거, localStorage 분리(오답노트 포함), 유출 0건 — OK")
