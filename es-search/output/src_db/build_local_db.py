"""
ES → 로컬 SQLite 저장 스크립트
patents.db: patents + patents_embodiment + patents_parsed
"""
import sqlite3, json, urllib.request, base64, re, csv, os, time
from datetime import datetime

DB_PATH = 'output/patents_local.db'
CSV_PATH = 'output/disclaimer_anchor_dimensions.csv'
BATCH    = 100
FIELDS   = [
    'ApplicationNumber','Title','ApplicantName','AgentNames',
    'MainCPC','SubCPC','ApplicationDate',
    'OpenNumber','OpenDate','RegisterNumber','RegisterDate',
    'TechnicalField','Background','Problem','SolutionProblem',
    'Effects','BriefDescriptionOfDrawings','Claims','Summary',
    'Embodiment',
]

def es_post(path, body, timeout=20):
    url = 'http://192.168.0.163:9204' + path
    req = urllib.request.Request(url, json.dumps(body).encode(), method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Basic ' + base64.b64encode(b'elastic:Rx6U8blh53KmWzs1Brnj').decode())
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def parse_segments(emb, bg, prob, claims_raw):
    """사전 파싱 세그먼트 추출"""
    # ─ Embodiment ─
    emb_paras = [p.strip() for p in (emb or '').split('\n\n') if p.strip() and len(p.strip()) > 20]
    if not emb_paras:
        emb_paras = [p.strip() for p in (emb or '').split('\n') if p.strip() and len(p.strip()) > 50]
    emb_intro     = emb_paras[0][:800] if emb_paras else ''
    emb_tail      = emb_paras[-1][:800] if emb_paras else ''
    emb_para_count = len(emb_paras)

    # ─ Background ─
    bg_paras = [p.strip() for p in (bg or '').split('\n\n') if p.strip() and len(p.strip()) > 20]
    bg_intro = bg_paras[0][:500] if bg_paras else ''
    bg_has_patent_cite = 1 if re.search(
        r'특허문헌|선행기술문헌|공개특허|등록특허|특개|일본 특허|미국 특허', bg or '') else 0

    # ─ Problem ─
    prob_sents = re.split(r'(?<=다)\.\s+', (prob or '').strip())
    prob_first_sent = prob_sents[0][:300] if prob_sents else ''

    # ─ Claims ─
    claim_blocks = [b.strip() for b in (claims_raw or '').split('¶')
                    if b.strip() and b.strip() != '삭제']
    claims_count = len(claim_blocks)
    # 첫 번째 독립항 (종속항 패턴 없는 것)
    claims_first = ''
    for blk in claim_blocks:
        if not re.search(r'(제\s*\d+\s*항|청구항\s*제?\s*\d+\s*항?)\s*(에\s*있어서|의\s|에\s*따른)', blk):
            claims_first = blk[:600]
            break

    return dict(
        emb_intro=emb_intro, emb_tail=emb_tail, emb_para_count=emb_para_count,
        bg_intro=bg_intro, bg_has_patent_cite=bg_has_patent_cite,
        prob_first_sent=prob_first_sent,
        claims_count=claims_count, claims_first=claims_first,
    )

def create_db(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS patents (
        application_number  TEXT PRIMARY KEY,
        index_name          TEXT,
        title               TEXT,
        applicant_name      TEXT,
        agent_names         TEXT,
        main_cpc            TEXT,
        sub_cpc             TEXT,
        application_date    TEXT,
        open_number         TEXT,
        open_date           TEXT,
        register_number     TEXT,
        register_date       TEXT,
        technical_field     TEXT,
        background          TEXT,
        problem             TEXT,
        solution_problem    TEXT,
        effects             TEXT,
        brief_description   TEXT,
        claims              TEXT,
        summary             TEXT,
        created_at          TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS patents_embodiment (
        application_number  TEXT PRIMARY KEY,
        embodiment          TEXT,
        embodiment_len      INTEGER,
        FOREIGN KEY (application_number) REFERENCES patents(application_number)
    );
    CREATE TABLE IF NOT EXISTS patents_parsed (
        application_number  TEXT PRIMARY KEY,
        emb_intro           TEXT,
        emb_tail            TEXT,
        emb_para_count      INTEGER,
        bg_intro            TEXT,
        bg_has_patent_cite  INTEGER,
        prob_first_sent     TEXT,
        claims_count        INTEGER,
        claims_first        TEXT,
        parsed_at           TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_number) REFERENCES patents(application_number)
    );
    CREATE INDEX IF NOT EXISTS idx_main_cpc       ON patents(main_cpc);
    CREATE INDEX IF NOT EXISTS idx_agent_names    ON patents(agent_names);
    CREATE INDEX IF NOT EXISTS idx_application_date ON patents(application_date);
    """)
    con.commit()

def upsert(con, src, idx_name):
    s = src
    a = s.get('ApplicationNumber','')
    if not a: return False
    emb = s.get('Embodiment','') or ''

    # patents
    con.execute("""
        INSERT OR REPLACE INTO patents
        (application_number,index_name,title,applicant_name,agent_names,
         main_cpc,sub_cpc,application_date,open_number,open_date,
         register_number,register_date,technical_field,background,problem,
         solution_problem,effects,brief_description,claims,summary)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (a, idx_name,
          s.get('Title',''), s.get('ApplicantName',''), s.get('AgentNames',''),
          s.get('MainCPC',''), s.get('SubCPC',''),
          str(s.get('ApplicationDate','')), s.get('OpenNumber',''), str(s.get('OpenDate','')),
          s.get('RegisterNumber',''), str(s.get('RegisterDate','')),
          s.get('TechnicalField',''), s.get('Background',''), s.get('Problem',''),
          s.get('SolutionProblem',''), s.get('Effects',''),
          s.get('BriefDescriptionOfDrawings',''), s.get('Claims',''), s.get('Summary','')))

    # patents_embodiment
    con.execute("""
        INSERT OR REPLACE INTO patents_embodiment (application_number, embodiment, embodiment_len)
        VALUES (?,?,?)
    """, (a, emb, len(emb)))

    # patents_parsed
    seg = parse_segments(
        emb, s.get('Background',''), s.get('Problem',''), s.get('Claims',''))
    con.execute("""
        INSERT OR REPLACE INTO patents_parsed
        (application_number,emb_intro,emb_tail,emb_para_count,
         bg_intro,bg_has_patent_cite,prob_first_sent,claims_count,claims_first)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (a, seg['emb_intro'], seg['emb_tail'], seg['emb_para_count'],
          seg['bg_intro'], seg['bg_has_patent_cite'], seg['prob_first_sent'],
          seg['claims_count'], seg['claims_first']))
    return True

def main():
    start = time.time()
    # 출원번호 목록
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        appnos = [r['출원번호'] for r in csv.DictReader(f)]
    total = len(appnos)
    print(f"[{datetime.now():%H:%M:%S}] 대상: {total}건")

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    create_db(con)

    # 이미 저장된 건 스킵
    existing = set(r[0] for r in con.execute("SELECT application_number FROM patents"))
    todo = [a for a in appnos if a not in existing]
    print(f"[{datetime.now():%H:%M:%S}] 기저장: {len(existing)}건 / 신규처리: {len(todo)}건")

    saved = 0; errors = 0
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        for attempt in range(3):
            try:
                res = es_post('/kr_pub_patents,kr_opn_patents/_search', {
                    'query': {'terms': {'ApplicationNumber': batch}},
                    '_source': FIELDS, 'size': BATCH * 2
                })
                # pub 우선
                seen = {}
                for h in res['hits']['hits']:
                    a = h['_source'].get('ApplicationNumber','')
                    idx = h['_index']
                    if a not in seen or 'pub' in idx:
                        seen[a] = (h['_source'], idx)
                for a, (src, idx) in seen.items():
                    if upsert(con, src, idx):
                        saved += 1
                con.commit()
                break
            except Exception as e:
                if attempt == 2:
                    errors += len(batch)
                    print(f"  BATCH ERR [{i}]: {e}")
                else:
                    time.sleep(5)

        done = i + len(batch)
        pct  = done / len(todo) * 100
        ela  = time.time() - start
        eta  = ela / done * (len(todo) - done) if done else 0
        print(f"  [{datetime.now():%H:%M:%S}] {done}/{len(todo)} ({pct:.0f}%) | "
              f"저장{saved} 에러{errors} | ETA {eta/60:.1f}분")

    # 최종 통계
    cnt = con.execute("SELECT COUNT(*) FROM patents").fetchone()[0]
    emb_cnt = con.execute("SELECT COUNT(*) FROM patents_embodiment WHERE embodiment_len>0").fetchone()[0]
    print(f"\n[완료] 총 {cnt}건 | Embodiment있음 {emb_cnt}건 | 소요 {(time.time()-start)/60:.1f}분")
    con.close()

if __name__ == '__main__':
    main()
