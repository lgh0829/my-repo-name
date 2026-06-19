"""
신규 ES (patent_kr_st96, 192.168.0.7:9207) → 로컬 SQLite 저장 스크립트 (v2)
기존 DB 스키마를 그대로 사용하고, 신규 ES 중첩 구조에서 필드를 매핑한다.

신규 ES 구조:
  metadata.application_number  (keyword)
  documents.PUBLICATION.*      (중첩)
    inventiontitle             (단일 텍스트)
    parties.applicants[].name  (keyword)
    parties.agents[].name      (text)
    classifications.cpc.sub_group (keyword / 배열 가능)
    abstract.text / technical_field.text / ... → [{p_number, text}, ...]
    claims[] → [{claim_number, text}, ...]
  documents.GRANT.grant_id / grant_date
"""
import sqlite3, json, urllib.request, base64, re, csv, time, os
from datetime import datetime

DB_PATH  = 'data/local/patents_local_v2.db'
CSV_PATH = 'output/disclaimer_anchor_dimensions.csv'
ES_URL   = 'http://192.168.0.7:9207'
ES_CREDS = base64.b64encode(b'elastic:88888888').decode()
ES_INDEX = 'patent_*'
BATCH    = 100

# ── ES 요청 ────────────────────────────────────────────────────────────────

def es_post(path, body, timeout=30):
    url = ES_URL + path
    req = urllib.request.Request(url, json.dumps(body).encode(), method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Basic ' + ES_CREDS)
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

# ── 신규 ES 구조 → 구 스키마 매핑 헬퍼 ────────────────────────────────────

def _first(val):
    """스칼라 또는 리스트 → 첫 번째 값(문자열)"""
    if isinstance(val, list):
        return str(val[0]) if val else ''
    return str(val) if val is not None else ''

def _join_text_paras(sections, sep='\n\n'):
    """{p_number, text}[] → 연결 문자열. 비어 있으면 ''."""
    if not sections:
        return ''
    if isinstance(sections, list):
        return sep.join(
            s.get('text', '') for s in sections
            if isinstance(s, dict) and s.get('text')
        )
    return str(sections)

def _join_claims(claims):
    """{claim_number, text}[] → ¶ 구분 문자열"""
    if not claims:
        return ''
    return '¶'.join(
        c.get('text', '') for c in claims
        if isinstance(c, dict) and c.get('text')
    )

def _cpc_code(entry):
    """CPC 항목 dict → 'H01L21/67132' 형식 풀 코드"""
    if not isinstance(entry, dict):
        return ''
    cls = entry.get('class', '')
    mg  = entry.get('main_group', '')
    sg  = entry.get('sub_group', '')
    if cls and mg and sg:
        return f"{cls}{mg}/{sg}"
    return ''

def _cpc_values(pub):
    """classifications.cpc (list<dict>) → (main_cpc, sub_cpc 공백구분)"""
    cls = (pub.get('classifications') or {})
    cpc = cls.get('cpc') or []
    if isinstance(cpc, dict):
        cpc = [cpc]
    codes = [_cpc_code(e) for e in cpc if _cpc_code(e)]
    if not codes:
        return '', ''
    return codes[0], ' '.join(codes[1:])

def map_source(src):
    """ES 신규 문서 _source → 기존 스키마 딕셔너리 (대문자 키)"""
    meta  = src.get('metadata')  or {}
    docs  = src.get('documents') or {}
    pub   = docs.get('PUBLICATION') or {}
    grant = docs.get('GRANT')       or {}

    # parties는 list: [{applicants:[...], agents:[...], date:...}, ...]
    parties_list = pub.get('parties') or []
    parties      = parties_list[0] if isinstance(parties_list, list) and parties_list else (
                   parties_list if isinstance(parties_list, dict) else {})

    # 대리인: parties.agents[].name → ¶ 구분
    agents      = parties.get('agents') or []
    agent_names = '¶'.join(
        a.get('name', '') for a in agents
        if isinstance(a, dict) and a.get('name')
    )

    # 출원인: parties.applicants[].name → 첫 번째 (name 또는 name_raw 폴백)
    applicants     = parties.get('applicants') or []
    if applicants:
        ap0 = applicants[0]
        applicant_name = str(ap0.get('name') or ap0.get('name_raw') or '')
    else:
        applicant_name = ''

    # CPC
    main_cpc, sub_cpc = _cpc_values(pub)

    # 텍스트 섹션: pub.get(field) 자체가 [{p_number, text}] 리스트
    def _s(field):
        return _join_text_paras(pub.get(field))

    return {
        'ApplicationNumber'         : str(meta.get('application_number', '')),
        'Title'                     : str(pub.get('inventiontitle', '') or ''),
        'ApplicantName'             : applicant_name,
        'AgentNames'                : agent_names,
        'MainCPC'                   : main_cpc,
        'SubCPC'                    : sub_cpc,
        'ApplicationDate'           : str(meta.get('application_date', '') or ''),
        'OpenNumber'                : str(pub.get('publication_id', '') or ''),
        'OpenDate'                  : str(pub.get('open_date', '') or ''),
        'RegisterNumber'            : str(grant.get('grant_id', '') or ''),
        'RegisterDate'              : str(grant.get('grant_date', '') or ''),
        'TechnicalField'            : _s('technical_field'),
        'Background'                : _s('background_art'),
        'Problem'                   : _s('technicalproblem'),
        'SolutionProblem'           : _s('technicalsolution'),
        'Effects'                   : _s('advantageouseffects'),
        'BriefDescriptionOfDrawings': _s('drawingdescription'),
        'Claims'                    : _join_claims(pub.get('claims') or []),
        'Summary'                   : _s('abstract'),
        'Embodiment'                : _s('embodimentdescription'),
    }

# ── SQLite 스키마 / upsert (기존과 동일) ───────────────────────────────────

def parse_segments(emb, bg, prob, claims_raw):
    emb_paras = [p.strip() for p in (emb or '').split('\n\n') if p.strip() and len(p.strip()) > 20]
    if not emb_paras:
        emb_paras = [p.strip() for p in (emb or '').split('\n') if p.strip() and len(p.strip()) > 50]
    emb_intro      = emb_paras[0][:800] if emb_paras else ''
    emb_tail       = emb_paras[-1][:800] if emb_paras else ''
    emb_para_count = len(emb_paras)

    bg_paras = [p.strip() for p in (bg or '').split('\n\n') if p.strip() and len(p.strip()) > 20]
    bg_intro = bg_paras[0][:500] if bg_paras else ''
    bg_has_patent_cite = 1 if re.search(
        r'특허문헌|선행기술문헌|공개특허|등록특허|특개|일본 특허|미국 특허', bg or '') else 0

    prob_sents   = re.split(r'(?<=다)\.\s+', (prob or '').strip())
    prob_first_sent = prob_sents[0][:300] if prob_sents else ''

    claim_blocks = [b.strip() for b in (claims_raw or '').split('¶')
                    if b.strip() and b.strip() != '삭제']
    claims_count = len(claim_blocks)
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
    CREATE INDEX IF NOT EXISTS idx_main_cpc         ON patents(main_cpc);
    CREATE INDEX IF NOT EXISTS idx_agent_names      ON patents(agent_names);
    CREATE INDEX IF NOT EXISTS idx_application_date ON patents(application_date);
    """)
    con.commit()

def upsert(con, mapped, idx_name):
    """mapped: map_source() 반환 딕셔너리"""
    s = mapped
    a = s.get('ApplicationNumber', '')
    if not a:
        return False
    emb = s.get('Embodiment', '') or ''

    con.execute("""
        INSERT OR REPLACE INTO patents
        (application_number,index_name,title,applicant_name,agent_names,
         main_cpc,sub_cpc,application_date,open_number,open_date,
         register_number,register_date,technical_field,background,problem,
         solution_problem,effects,brief_description,claims,summary)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (a, idx_name,
          s['Title'], s['ApplicantName'], s['AgentNames'],
          s['MainCPC'], s['SubCPC'],
          s['ApplicationDate'], s['OpenNumber'], s['OpenDate'],
          s['RegisterNumber'], s['RegisterDate'],
          s['TechnicalField'], s['Background'], s['Problem'],
          s['SolutionProblem'], s['Effects'],
          s['BriefDescriptionOfDrawings'], s['Claims'], s['Summary']))

    con.execute("""
        INSERT OR REPLACE INTO patents_embodiment (application_number, embodiment, embodiment_len)
        VALUES (?,?,?)
    """, (a, emb, len(emb)))

    seg = parse_segments(emb, s['Background'], s['Problem'], s['Claims'])
    con.execute("""
        INSERT OR REPLACE INTO patents_parsed
        (application_number,emb_intro,emb_tail,emb_para_count,
         bg_intro,bg_has_patent_cite,prob_first_sent,claims_count,claims_first)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (a, seg['emb_intro'], seg['emb_tail'], seg['emb_para_count'],
          seg['bg_intro'], seg['bg_has_patent_cite'], seg['prob_first_sent'],
          seg['claims_count'], seg['claims_first']))
    return True

# ── main ──────────────────────────────────────────────────────────────────

def main():
    start = time.time()

    with open(CSV_PATH, encoding='utf-8-sig') as f:
        appnos = [r['출원번호'] for r in csv.DictReader(f)]
    total = len(appnos)
    print(f"[{datetime.now():%H:%M:%S}] 대상: {total}건")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    create_db(con)

    existing = set(r[0] for r in con.execute("SELECT application_number FROM patents"))
    todo = [a for a in appnos if a not in existing]
    print(f"[{datetime.now():%H:%M:%S}] 기저장: {len(existing)}건 / 신규처리: {len(todo)}건")

    saved = 0; errors = 0
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        for attempt in range(3):
            try:
                res = es_post(f'/{ES_INDEX}/_search', {
                    'query': {'terms': {'metadata.application_number': batch}},
                    'size': BATCH * 2,
                })
                seen = {}
                for h in res['hits']['hits']:
                    src = h['_source']
                    meta = src.get('metadata') or {}
                    a = str(meta.get('application_number', ''))
                    idx = h['_index']
                    # PUBLICATION 있는 문서를 우선 보존
                    if a not in seen:
                        seen[a] = (src, idx)
                    else:
                        pub = (src.get('documents') or {}).get('PUBLICATION')
                        if pub:
                            seen[a] = (src, idx)

                for a, (src, idx) in seen.items():
                    try:
                        mapped = map_source(src)
                        if upsert(con, mapped, idx):
                            saved += 1
                    except Exception as e:
                        errors += 1
                        print(f"  DOC ERR [{a}]: {e}")
                con.commit()
                break
            except Exception as e:
                if attempt == 2:
                    errors += len(batch)
                    print(f"  BATCH ERR [{i}]: {e}")
                else:
                    time.sleep(5)

        done = i + len(batch)
        ela  = time.time() - start
        eta  = ela / done * (len(todo) - done) if done else 0
        print(f"  [{datetime.now():%H:%M:%S}] {done}/{len(todo)} ({done/len(todo)*100:.0f}%) | "
              f"저장{saved} 에러{errors} | ETA {eta/60:.1f}분")

    cnt     = con.execute("SELECT COUNT(*) FROM patents").fetchone()[0]
    emb_cnt = con.execute("SELECT COUNT(*) FROM patents_embodiment WHERE embodiment_len>0").fetchone()[0]
    print(f"\n[완료] 총 {cnt}건 | Embodiment있음 {emb_cnt}건 | 소요 {(time.time()-start)/60:.1f}분")
    con.close()

if __name__ == '__main__':
    main()
