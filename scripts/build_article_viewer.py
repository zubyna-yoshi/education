#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--index-json', required=True)
    ap.add_argument('--out-html', required=True)
    args = ap.parse_args()

    index_path = Path(args.index_json).resolve()
    out_path = Path(args.out_html).resolve()

    data = json.loads(index_path.read_text(encoding='utf-8'))
    base_dir = out_path.parent

    # Convert absolute paths in index payload to relative paths from HTML location.
    for _, article in data.items():
        for _, doc in (article.get('documents') or {}).items():
            for key in ('first_text_file', 'first_image_file'):
                v = doc.get(key)
                if isinstance(v, str) and v.startswith('/'):
                    doc[key] = os.path.relpath(v, start=base_dir)

    payload = json.dumps(data, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>산업안전보건 조항 뷰어</title>
  <style>
    :root {{
      --bg: #f3f6fa;
      --card: #ffffff;
      --line: #dbe3ed;
      --text: #17212b;
      --muted: #5f6c7b;
      --accent: #0b57d0;
      --accent-soft: #e8f0ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: linear-gradient(180deg, #eef3fa 0%, #f7f9fc 100%); color: var(--text); font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif; }}
    .wrap {{ max-width: 1380px; margin: 0 auto; padding: 16px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; }}
    .desc {{ color: var(--muted); margin-bottom: 12px; font-size: 13px; }}
    .home {{
      background: radial-gradient(1200px 360px at 20% -10%, #dce9ff 0%, #f7f9fc 45%), #fff;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 12px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, .06);
    }}
    .home-grid {{ display: grid; grid-template-columns: 1fr; gap: 14px; align-items: center; }}
    .home-title {{ font-size: 28px; font-weight: 800; line-height: 1.2; margin-bottom: 8px; color: #17365c; }}
    .home-sub {{ font-size: 14px; color: #49617f; margin-bottom: 12px; }}
    .home-pill-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }}
    .home-pill {{ font-size: 12px; border: 1px solid #cdddf0; background: #f6faff; border-radius: 999px; padding: 4px 10px; color: #34567f; }}
    .home-img {{ width: 100%; border: 1px solid #d7e2f0; border-radius: 12px; overflow: hidden; min-height: 260px; max-height: 480px; background: #eef4fb; }}
    .home-img img {{ display: block; width: 100%; height: 100%; object-fit: cover; object-position: center 35%; filter: saturate(1.03) contrast(1.02); }}
    #startBtn {{ display: block; margin: 8px auto 0; padding: 14px 28px; font-size: 18px; font-weight: 800; border-radius: 12px; min-width: 220px; }}
    .workspace {{ display: none; }}

    .toolbar {{
      display: grid;
      grid-template-columns: 230px 1fr 140px;
      gap: 8px;
      margin-bottom: 12px;
    }}
    input, select, button {{
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
      font-size: 14px;
    }}
    button {{ background: var(--accent); color: #fff; border: 0; cursor: pointer; }}
    .summary {{ color: var(--muted); margin-bottom: 10px; font-size: 13px; min-height: 18px; }}

    .layout {{ display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 12px; }}
    .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; box-shadow: 0 6px 18px rgba(15, 23, 42, .05); }}
    .head {{ padding: 12px 14px; border-bottom: 1px solid var(--line); font-weight: 700; background: #fbfcfe; }}
    .body {{ padding: 12px; }}

    .pill-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }}
    .pill {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; font-size: 12px; color: var(--muted); background: #fff; }}

    .image-wrap {{ border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: #eef3f8; min-height: 220px; }}
    .image-wrap img {{ width: 100%; display: block; }}
    .image-hint {{ margin-top: 6px; font-size: 12px; color: var(--muted); }}

    .text-box {{ margin-top: 10px; border: 1px solid var(--line); border-radius: 10px; background: #fafcff; padding: 10px; white-space: pre-wrap; font-size: 13px; line-height: 1.5; max-height: 220px; overflow: auto; }}

    .split {{ display: grid; grid-template-columns: 1fr; gap: 10px; margin-top: 10px; }}
    .mini {{ border: 1px solid var(--line); border-radius: 10px; padding: 10px; background: #fff; }}
    .mini-title {{ font-weight: 700; font-size: 13px; margin-bottom: 6px; }}

    .upload-area {{ border: 1px dashed #9fb7dc; border-radius: 12px; padding: 12px; background: var(--accent-soft); }}
    .upload-top {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
    .upload-note {{ color: var(--muted); font-size: 12px; margin-top: 6px; }}

    .photos {{ margin-top: 12px; display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }}
    .photo-card {{ border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: #fff; }}
    .photo-card img {{ width: 100%; height: 130px; object-fit: cover; display: block; background: #e5e7eb; }}
    .photo-meta {{ padding: 8px; font-size: 12px; color: var(--muted); }}
    .photo-actions {{ display: flex; justify-content: space-between; gap: 6px; padding: 0 8px 8px; }}
    .photo-actions button {{ width: 100%; padding: 6px 8px; font-size: 12px; border-radius: 8px; }}
    .btn-sub {{ background: #eef3f9; color: #27405f; border: 1px solid #ccd9ea; }}
    .react-row {{ display: flex; gap: 6px; padding: 0 8px 8px; }}
    .react-btn {{ flex: 1; background: #fff; border: 1px solid #cfd9e8; color: #29466b; border-radius: 8px; padding: 6px 8px; font-size: 12px; }}
    .react-btn.active-like {{ background: #e9f7ef; border-color: #8fd0a9; color: #185b35; }}
    .react-btn.active-dislike {{ background: #fff0f0; border-color: #e3a1a1; color: #8f1f1f; }}
    .tag {{ display: inline-block; margin: 0 8px 8px; padding: 3px 8px; border-radius: 999px; border: 1px solid #d8e1ef; color: #5f6c7b; font-size: 11px; }}

    .empty {{ border: 1px dashed var(--line); border-radius: 10px; padding: 14px; color: var(--muted); font-size: 13px; background: #fff; }}
    .links {{ margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap; }}
    a {{ color: var(--accent); text-decoration: none; font-size: 13px; }}
    .crime-box {{ margin-top: 12px; border: 1px solid var(--line); border-radius: 12px; background: #fff; padding: 10px; }}
    .crime-title {{ font-weight: 700; font-size: 13px; margin-bottom: 8px; }}
    .crime-input {{ width: 100%; min-height: 86px; resize: vertical; border: 1px solid #ccd8e8; border-radius: 10px; padding: 10px; font-size: 13px; }}
    .crime-actions {{ display: flex; justify-content: flex-end; margin-top: 8px; }}
    .crime-list {{ margin-top: 10px; display: grid; gap: 8px; }}
    .crime-item {{ border: 1px solid #d9e3f0; border-radius: 10px; padding: 10px; background: #fbfdff; }}
    .crime-text {{ white-space: pre-wrap; font-size: 13px; line-height: 1.45; }}
    .crime-meta {{ margin-top: 6px; color: #6b7280; font-size: 12px; }}
    .term {{ text-decoration: underline dotted #7aa2d6; text-underline-offset: 2px; cursor: help; }}
    .term-tooltip {{
      position: fixed;
      z-index: 10001;
      display: none;
      width: 320px;
      padding: 8px 10px;
      border-radius: 8px;
      border: 1px solid #c8d8ec;
      background: #ffffff;
      box-shadow: 0 8px 24px rgba(15, 23, 42, .18);
      color: #1f2a37;
      font-size: 12px;
      line-height: 1.45;
      pointer-events: auto;
    }}
    .term-title {{ font-weight: 700; margin-bottom: 6px; color: #1a3555; }}
    .term-def {{ color: #30465f; margin-bottom: 8px; }}
    .modal {{ position: fixed; inset: 0; background: rgba(11, 18, 30, .68); display: none; align-items: center; justify-content: center; z-index: 9999; }}
    .modal.show {{ display: flex; }}
    .modal-content {{ max-width: min(94vw, 1200px); max-height: 90vh; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,.35); }}
    .modal-head {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 10px 12px; border-bottom: 1px solid #e1e7ef; font-size: 13px; color: #42556d; }}
    .modal-head button {{ background: #edf2f8; color: #223954; border: 1px solid #ccdae9; padding: 6px 10px; border-radius: 8px; font-size: 12px; }}
    .modal-body {{ background: #f1f5fa; }}
    .modal-body img {{ display: block; max-width: min(94vw, 1200px); max-height: calc(90vh - 52px); width: auto; height: auto; margin: 0 auto; }}
    .web-modal-body {{ background: #f7f9fc; width: min(94vw, 1200px); height: min(86vh, 860px); }}
    .web-modal-body iframe {{ width: 100%; height: 100%; border: 0; background: #fff; }}

    @media (max-width: 980px) {{
      .toolbar {{ grid-template-columns: 1fr; }}
      .layout {{ grid-template-columns: 1fr; }}
      .split {{ grid-template-columns: 1fr; }}
      .home-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div id=\"homeScreen\" class=\"home\">
      <div class=\"home-grid\">
        <div class=\"home-img\"><img id=\"homeHeroImg\" alt=\"집단지성 대표 이미지\" /></div>
        <div>
          <div class=\"home-title\">근로감독관 집단 지성 플랫폼</div>
          <div class=\"home-sub\">현장 사진, 조항 해석, 범죄인지 예시를 함께 쌓아 동일한 상황에서 더 빠르고 일관된 판단을 지원합니다.</div>
          <div class=\"home-pill-row\">
            <span class=\"home-pill\">조항별 사례 축적</span>
            <span class=\"home-pill\">좋아요/싫어요 기반 집단평가</span>
            <span class=\"home-pill\">현장 사진 중심 학습</span>
          </div>
          <button id=\"startBtn\" type=\"button\">두뇌 풀가동 시작</button>
        </div>
      </div>
    </div>

    <div id=\"workspace\" class=\"workspace\">
      <h1>산업안전보건기준 조항 적용 화면</h1>
      <div class=\"desc\">상단에서 조항을 찾고, 좌측에서 법조항/삽화를 확인한 뒤, 우측에 근로감독관 현장 사진을 업로드해 기록합니다.</div>

      <div class=\"toolbar\">
        <select id=\"articleSelect\"></select>
        <input id=\"search\" placeholder=\"숫자만 입력 가능 (예: 44) / 제44조 / 안전대\" />
        <button id=\"go\">검색</button>
      </div>

      <div id=\"summary\" class=\"summary\"></div>

      <div class=\"layout\">
      <section class=\"card\">
        <div class=\"head\">법조항 및 삽화</div>
        <div class=\"body\">
          <div id=\"leftMeta\" class=\"pill-row\"></div>

          <div class=\"image-wrap\" id=\"comicImageWrap\"></div>
          <div class=\"image-hint\">삽화 이미지 내 QR 코드를 클릭하면 현재 화면 내부 팝업으로 웹페이지를 엽니다.</div>

          <div class=\"split\">
            <div class=\"mini\">
              <div class=\"mini-title\">법제처 조항 본문</div>
              <div id=\"lawText\" class=\"text-box\"></div>
            </div>
          </div>
        </div>
      </section>

      <section class=\"card\">
        <div class=\"head\">근로감독관 현장 사진</div>
        <div class=\"body\">
          <div class=\"upload-area\">
            <div class=\"upload-top\">
              <input id=\"photoInput\" type=\"file\" accept=\"image/*\" multiple />
              <button id=\"clearPhotos\" type=\"button\" class=\"btn-sub\">전체 삭제</button>
            </div>
            <div id=\"uploadScope\" class=\"upload-note\"></div>
          </div>
          <div id=\"photoList\" class=\"photos\"></div>
          <div class=\"crime-box\">
            <div class=\"crime-title\">범죄인지 예시 (근로감독관 작성)</div>
            <textarea id=\"crimeInput\" class=\"crime-input\" placeholder=\"예: 안전대 미착용 상태를 인지하고도 작업을 계속 지시한 정황이 있어, 관련 진술/점검기록 확보 후 범죄인지 검토\"></textarea>
            <div class=\"crime-actions\">
              <button id=\"addCrime\" type=\"button\">예시 추가</button>
            </div>
            <div id=\"crimeList\" class=\"crime-list\"></div>
          </div>
        </div>
      </section>
      </div>
    </div>
  </div>
  <div id=\"imageModal\" class=\"modal\">
    <div class=\"modal-content\">
      <div class=\"modal-head\">
        <span id=\"imageModalTitle\">이미지 보기</span>
        <button id=\"imageModalClose\" type=\"button\">닫기</button>
      </div>
      <div class=\"modal-body\">
        <img id=\"imageModalImg\" alt=\"확대 이미지\" />
      </div>
    </div>
  </div>
  <div id=\"termTooltip\" class=\"term-tooltip\"></div>
  <div id=\"webModal\" class=\"modal\">
    <div class=\"modal-content\">
      <div class=\"modal-head\">
        <span id=\"webModalTitle\">웹 보기</span>
        <button id=\"webModalClose\" type=\"button\">닫기</button>
      </div>
      <div class=\"web-modal-body\">
        <iframe id=\"webModalFrame\" referrerpolicy=\"no-referrer\"></iframe>
      </div>
    </div>
  </div>

  <script>
    const DATA = {payload};
    const entries = Object.values(DATA).sort((a, b) => (a.article_no - b.article_no) || ((a.sub_no || 0) - (b.sub_no || 0)));

    const sel = document.getElementById('articleSelect');
    const search = document.getElementById('search');
    const go = document.getElementById('go');
    const summary = document.getElementById('summary');
    const homeScreen = document.getElementById('homeScreen');
    const workspace = document.getElementById('workspace');
    const startBtn = document.getElementById('startBtn');
    const homeHeroImg = document.getElementById('homeHeroImg');
    const CUSTOM_HOME_HERO = 'assets/main-photo.png';

    const leftMeta = document.getElementById('leftMeta');
    const comicImageWrap = document.getElementById('comicImageWrap');
    const lawText = document.getElementById('lawText');

    const photoInput = document.getElementById('photoInput');
    const clearPhotosBtn = document.getElementById('clearPhotos');
    const photoList = document.getElementById('photoList');
    const uploadScope = document.getElementById('uploadScope');
    const crimeInput = document.getElementById('crimeInput');
    const addCrimeBtn = document.getElementById('addCrime');
    const crimeList = document.getElementById('crimeList');
    const imageModal = document.getElementById('imageModal');
    const imageModalImg = document.getElementById('imageModalImg');
    const imageModalTitle = document.getElementById('imageModalTitle');
    const imageModalClose = document.getElementById('imageModalClose');
    const termTooltip = document.getElementById('termTooltip');
    const webModal = document.getElementById('webModal');
    const webModalFrame = document.getElementById('webModalFrame');
    const webModalTitle = document.getElementById('webModalTitle');
    const webModalClose = document.getElementById('webModalClose');

    const STORAGE_KEY = 'labor_inspector_uploaded_photos_v1';
    const CRIME_STORAGE_KEY = 'labor_inspector_crime_examples_v1';
    const MAX_PHOTOS = 6;
    const MAX_VISIBLE_PHOTOS = 6;
    let activeArticleKey = entries.length ? entries[0].article_key : '';
    let currentComicUrlFallback = '';
    let termHoverTimer = null;
    let termHoverWord = '';
    let lastGoogleFetchAt = 0;
    let googleBlockedUntil = 0;
    const TERM_DICT = {{
      '사업주': '근로자를 사용하는 자로서 산업안전보건법상 안전·보건조치 의무의 주체입니다.',
      '근로자': '임금을 목적으로 사업 또는 사업장에 근로를 제공하는 사람입니다.',
      '안전대': '추락 위험 작업 시 신체를 지지점에 연결해 추락을 방지하는 개인보호구입니다.',
      '추락': '높은 위치에서 아래로 떨어지는 재해 유형을 말합니다.',
      '작업발판': '근로자가 안전하게 작업하기 위해 설치한 발 디딤 구조물입니다.',
      '안전난간': '개구부·가장자리 등에서 추락을 막기 위한 난간형 방호설비입니다.',
      '추락방호망': '높은 곳에서 떨어지는 근로자나 물체를 받아 피해를 줄이는 방호망입니다.',
      '방호조치': '위험요인을 제거·통제하기 위한 기술적/관리적 조치입니다.',
      '점검': '작업 전·중 설비나 보호구의 이상 유무를 확인하는 행위입니다.',
      '시정지시': '위반 사항에 대해 개선을 명하는 감독상 조치입니다.'
    }};

    function safeEncode(path) {{
      return encodeURI(path || '');
    }}

    function openImageModal(src, title) {{
      imageModalImg.src = src || '';
      imageModalTitle.textContent = title || '이미지 보기';
      imageModal.classList.add('show');
    }}

    function closeImageModal() {{
      imageModal.classList.remove('show');
      imageModalImg.src = '';
    }}

    function openWebModal(url, title) {{
      webModalTitle.textContent = title || '웹 보기';
      webModalFrame.src = url || 'about:blank';
      webModal.classList.add('show');
    }}

    function closeWebModal() {{
      webModal.classList.remove('show');
      webModalFrame.src = 'about:blank';
    }}

    function extractFirstUrl(text) {{
      const m = (text || '').match(/https?:\\/\\/[^\\s)\\]]+/i);
      return m ? m[0] : '';
    }}

    function escapeHtml(s) {{
      return (s || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    function escapeRegExp(s) {{
      return s.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    }}

    function annotateTerms(text) {{
      const src = text || '';
      const re = /[가-힣A-Za-z0-9·_-]+/g;
      const out = [];
      let last = 0;
      let m;
      while ((m = re.exec(src)) !== null) {{
        const start = m.index;
        const word = m[0];
        out.push(escapeHtml(src.slice(last, start)));
        const esc = escapeHtml(word);
        out.push(`<span class=\"term\" data-term=\"${{esc}}\">${{esc}}</span>`);
        last = start + word.length;
      }}
      out.push(escapeHtml(src.slice(last)));
      return out.join('');
    }}

    function positionTooltip(ev) {{
      const x = Math.min(window.innerWidth - termTooltip.offsetWidth - 12, ev.clientX + 12);
      const y = Math.min(window.innerHeight - termTooltip.offsetHeight - 12, ev.clientY + 12);
      termTooltip.style.left = `${{Math.max(8, x)}}px`;
      termTooltip.style.top = `${{Math.max(8, y)}}px`;
    }}

    function renderTermTooltip(term, def, extraHtml) {{
      const safeTerm = escapeHtml(term || '');
      const safeDef = escapeHtml(def || '사전 정의가 아직 등록되지 않은 단어입니다.');
      termTooltip.innerHTML = `
        <div class=\"term-title\">${{safeTerm}}</div>
        <div class=\"term-def\">${{safeDef}}</div>
        ${{extraHtml || ''}}
      `;
    }}

    const termInfoCache = {{}};
    function normalizeKoreanTerm(term) {{
      let t = (term || '').trim();
      // 흔한 2글자 조사/어미
      const suffix2 = ['으로', '에서', '에게', '까지', '부터', '처럼', '마다', '밖에', '조차', '마저', '인데', '이다'];
      for (const s of suffix2) {{
        if (t.length > s.length + 1 && t.endsWith(s)) {{
          t = t.slice(0, -s.length);
          return t;
        }}
      }}
      // 흔한 1글자 조사
      const suffix1 = ['의', '은', '는', '이', '가', '을', '를', '에', '도', '만', '와', '과', '로'];
      for (const s of suffix1) {{
        if (t.length > 1 && t.endsWith(s)) {{
          t = t.slice(0, -s.length);
          return t;
        }}
      }}
      return t;
    }}

    function buildIndustrialQuery(term) {{
      const base = normalizeKoreanTerm(term) || term;
      const article = DATA[activeArticleKey] || {{}};
      const docVals = Object.values(article.documents || {{}});
      const titles = docVals.flatMap(d => d.titles || []).slice(0, 2).join(' ');
      const context = [base, '산업현장', '산업안전보건', titles, '뜻', '대표 이미지']
        .filter(Boolean)
        .join(' ');
      return {{
        base,
        query: context,
      }};
    }}

    async function fetchGoogleSummary(queryText) {{
      // Google 페이지는 브라우저 CORS 제한이 있어 텍스트 프록시를 이용해 요약 텍스트를 추출
      const now = Date.now();
      const info = {{
        extract: '',
        image: '',
        page: '',
        imagePage: '',
        rateLimited: false,
      }};
      if (now < googleBlockedUntil) {{
        info.rateLimited = true;
        return info;
      }}
      const minIntervalMs = 5000;
      const wait = Math.max(0, minIntervalMs - (now - lastGoogleFetchAt));
      if (wait > 0) {{
        await new Promise((r) => setTimeout(r, wait));
      }}
      lastGoogleFetchAt = Date.now();

      const q = encodeURIComponent(queryText);
      const proxy = `https://r.jina.ai/http://www.google.com/search?q=${{q}}`;
      info.page = `https://www.google.com/search?q=${{q}}`;
      info.imagePage = `https://www.google.com/search?tbm=isch&q=${{q}}`;
      try {{
        const res = await fetch(proxy);
        if (res.status === 429) {{
          googleBlockedUntil = Date.now() + 60 * 1000;
          info.rateLimited = true;
          return info;
        }}
        if (!res.ok) return info;
        const txt = await res.text();
        if ((txt || '').includes('429') && (txt || '').toLowerCase().includes('too many requests')) {{
          googleBlockedUntil = Date.now() + 60 * 1000;
          info.rateLimited = true;
          return info;
        }}
        const cleaned = (txt || '')
          .replace(/\\r/g, '')
          .split('\\n')
          .map(s => s.trim())
          .filter(Boolean)
          .filter(s => !s.startsWith('Title:') && !s.startsWith('URL Source:') && !s.startsWith('Markdown Content:'))
          .slice(0, 120)
          .join(' ');
        info.extract = cleaned.slice(0, 240);
        const img = (txt.match(/https?:\\/\\/[^\\s)]+\\.(?:jpg|jpeg|png|webp)/i) || [])[0] || '';
        info.image = img;
      }} catch (_) {{
        // fallback to links only
      }}
      return info;
    }}

    function cleanProxyText(raw) {{
      return (raw || '')
        .replace(/\\r/g, '')
        .split('\\n')
        .map(s => s.trim())
        .filter(Boolean)
        .filter(s => !s.startsWith('Title:') && !s.startsWith('URL Source:') && !s.startsWith('Markdown Content:'))
        .filter(s => !/^https?:\\/\\//i.test(s))
        .join(' ')
        .replace(/\\[[^\\]]+\\]\\((https?:\\/\\/[^)]+)\\)/g, ' ')
        .replace(/https?:\\/\\/[^\\s)\\]]+/g, ' ')
        .replace(/\\s+/g, ' ')
        .trim();
    }}

    function summarizeText(raw, maxLen = 240) {{
      const txt = cleanProxyText(raw);
      // 문장 단위로 잘라 링크/잡음을 최소화한 짧은 의미 설명 우선 표시
      const parts = txt.split(/(?<=[.!?。]|다\\.)\\s+/).map(s => s.trim()).filter(Boolean);
      const picked = parts.slice(0, 2).join(' ');
      return (picked || txt).slice(0, maxLen).trim();
    }}

    async function fetchNaverMeaning(term, queryText) {{
      const q = encodeURIComponent(queryText || term);
      const info = {{ extract: '', normalized: term }};
      try {{
        const searchProxy = `https://r.jina.ai/http://search.naver.com/search.naver?where=nexearch&query=${{q}}`;
        const res = await fetch(searchProxy);
        if (!res.ok) return info;
        const txt = await res.text();
        let extract = summarizeText(txt, 280);

        // 검색 결과 본문에서 첫 번째 참고 링크를 찾아 한 번 더 본문 추출 시도
        const links = (txt.match(/https?:\\/\\/[^\\s)\\]]+/g) || [])
          .filter(u => !u.includes('r.jina.ai'))
          .filter(u => !u.includes('search.naver.com'))
          .slice(0, 8);
        const ref = links.find(u =>
          u.includes('terms.naver.com') ||
          u.includes('namu.wiki') ||
          u.includes('ko.wikipedia.org') ||
          u.includes('encykorea.aks.ac.kr')
        ) || links[0];

        if (ref) {{
          try {{
            const refProxy = `https://r.jina.ai/http://${{ref.replace(/^https?:\\/\\//, '')}}`;
            const refRes = await fetch(refProxy);
            if (refRes.ok) {{
              const refTxt = await refRes.text();
              const refined = summarizeText(refTxt, 280);
              if (refined && refined.length > 30) extract = refined;
            }}
          }} catch (_) {{
            // keep original extract
          }}
        }}
        info.extract = (extract || '').replace(/\\s+/g, ' ').trim();
      }} catch (_) {{
        // ignore
      }}
      return info;
    }}

    async function fetchWikiFallback(term) {{
      const info = {{ extract: '', image: '', page: '' }};
      try {{
        const summaryUrl = `https://ko.wikipedia.org/api/rest_v1/page/summary/${{encodeURIComponent(term)}}`;
        const res = await fetch(summaryUrl, {{ headers: {{ 'accept': 'application/json' }} }});
        if (!res.ok) return info;
        const j = await res.json();
        info.extract = j.extract || '';
        info.image = (j.thumbnail && j.thumbnail.source) ? j.thumbnail.source : '';
        info.page = (j.content_urls && j.content_urls.desktop && j.content_urls.desktop.page) ? j.content_urls.desktop.page : '';
      }} catch (_) {{
        // ignore
      }}
      return info;
    }}

    async function fetchTermInfo(term) {{
      const industrial = buildIndustrialQuery(term);
      const cacheKey = `${{term}}|${{activeArticleKey}}`;
      if (termInfoCache[cacheKey]) return termInfoCache[cacheKey];
      const searchTerm = industrial.base;
      // 뜻은 네이버 우선(링크 추적 포함), 이미지는 구글 보강
      const nv = await fetchNaverMeaning(searchTerm, industrial.query);
      const wk = await fetchWikiFallback(searchTerm);
      const info = {{
        extract: nv.extract || wk.extract || '',
        image: wk.image || '',
        page: wk.page || '',
        imagePage: '',
        rateLimited: false,
      }};
      info.normalized = searchTerm;
      info.query = industrial.query;
      if (!info.image) {{
        const gg = await fetchGoogleSummary(industrial.query);
        info.rateLimited = !!gg.rateLimited;
        if (!info.image && gg.image) info.image = gg.image;
        if (!info.page && gg.page) info.page = gg.page;
        if (gg.imagePage) info.imagePage = gg.imagePage;
      }}
      termInfoCache[cacheKey] = info;
      return info;
    }}

    function showTermTooltip(target, ev) {{
      const term = target.getAttribute('data-term') || '';
      renderTermTooltip(
        term,
        TERM_DICT[term],
        '<div class=\"term-def\">2초 이상 올려두면 산업현장 맥락으로 뜻/대표 이미지를 이 창에서 불러옵니다.</div>'
      );
      termTooltip.style.display = 'block';
      positionTooltip(ev);
    }}

    function hideTermTooltip() {{
      termTooltip.style.display = 'none';
    }}

    function scheduleTermSearch(term, ev) {{
      if (!term) return;
      if (termHoverTimer) clearTimeout(termHoverTimer);
      termHoverWord = term;
      termHoverTimer = setTimeout(async () => {{
        if (termHoverWord !== term) return;
        renderTermTooltip(term, TERM_DICT[term], '<div class=\"term-def\">뜻/대표 이미지를 불러오는 중...</div>');
        positionTooltip(ev);
        const info = await fetchTermInfo(term);
        let extra = '';
        if (info.normalized && info.normalized !== term) {{
          extra += `<div class=\"term-def\" style=\"margin-top:8px;\">검색어 보정: <b>${{escapeHtml(term)}}</b> → <b>${{escapeHtml(info.normalized)}}</b></div>`;
        }}
        if (info.extract) {{
          extra += `<div class=\"term-def\" style=\"margin-top:8px;\">${{escapeHtml(info.extract.slice(0, 180))}}</div>`;
        }}
        if (info.image) {{
          const src = escapeHtml(info.image);
          extra += `<div style=\"margin-top:8px;\"><img src=\"${{src}}\" alt=\"${{escapeHtml(term)}}\" style=\"width:100%;max-height:140px;object-fit:cover;border:1px solid #d9e3f0;border-radius:6px;\"></div>`;
        }}
        if (!info.extract && !info.image) {{
          if (info.rateLimited) {{
            extra += '<div class=\"term-def\" style=\"margin-top:8px;\">외부 검색 요청이 잠시 제한(429)되어 로컬 정보만 표시 중입니다. 잠시 후 다시 시도해 주세요.</div>';
          }} else {{
            extra += '<div class=\"term-def\" style=\"margin-top:8px;\">뜻/대표 이미지를 찾지 못했습니다.</div>';
          }}
        }}
        renderTermTooltip(term, TERM_DICT[term], extra);
        positionTooltip(ev);
      }}, 2000);
    }}

    function cancelTermSearch() {{
      if (termHoverTimer) {{
        clearTimeout(termHoverTimer);
        termHoverTimer = null;
      }}
      termHoverWord = '';
    }}

    async function tryOpenQrPopupFromImage(imgEl, ev, fallbackUrl) {{
      const popup = (url) => openWebModal(url, 'QR 연결 페이지');
      try {{
        if ('BarcodeDetector' in window) {{
          const detector = new BarcodeDetector({{ formats: ['qr_code'] }});
          const natW = imgEl.naturalWidth || imgEl.width;
          const natH = imgEl.naturalHeight || imgEl.height;
          if (!natW || !natH) throw new Error('image-size');
          const rect = imgEl.getBoundingClientRect();
          const relX = Math.max(0, Math.min(1, (ev.clientX - rect.left) / Math.max(1, rect.width)));
          const relY = Math.max(0, Math.min(1, (ev.clientY - rect.top) / Math.max(1, rect.height)));

          const baseCanvas = document.createElement('canvas');
          baseCanvas.width = natW;
          baseCanvas.height = natH;
          const bctx = baseCanvas.getContext('2d');
          bctx.drawImage(imgEl, 0, 0, natW, natH);

          const regions = [];
          regions.push({{ x: 0, y: 0, w: natW, h: natH }});
          regions.push({{ x: 0, y: 0, w: Math.floor(natW * 0.55), h: Math.floor(natH * 0.55) }});
          regions.push({{ x: Math.floor(natW * 0.45), y: 0, w: Math.floor(natW * 0.55), h: Math.floor(natH * 0.55) }});
          regions.push({{ x: 0, y: Math.floor(natH * 0.45), w: Math.floor(natW * 0.55), h: Math.floor(natH * 0.55) }});
          regions.push({{ x: Math.floor(natW * 0.45), y: Math.floor(natH * 0.45), w: Math.floor(natW * 0.55), h: Math.floor(natH * 0.55) }});

          const cx = Math.floor(relX * natW);
          const cy = Math.floor(relY * natH);
          const sizes = [0.25, 0.38, 0.55];
          sizes.forEach((r) => {{
            const rw = Math.floor(natW * r);
            const rh = Math.floor(natH * r);
            regions.push({{
              x: Math.max(0, Math.min(natW - rw, cx - Math.floor(rw / 2))),
              y: Math.max(0, Math.min(natH - rh, cy - Math.floor(rh / 2))),
              w: rw,
              h: rh,
            }});
          }});

          const scales = [1, 1.5, 2];
          for (const reg of regions) {{
            for (const sc of scales) {{
              const c = document.createElement('canvas');
              c.width = Math.max(1, Math.floor(reg.w * sc));
              c.height = Math.max(1, Math.floor(reg.h * sc));
              const ctx = c.getContext('2d');
              ctx.imageSmoothingEnabled = true;
              ctx.imageSmoothingQuality = 'high';
              ctx.drawImage(baseCanvas, reg.x, reg.y, reg.w, reg.h, 0, 0, c.width, c.height);
              const found = await detector.detect(c);
              if (found && found.length) {{
                const raw = (found[0].rawValue || '').trim();
                if (raw) {{
                  const target = /^https?:\\/\\//i.test(raw) ? raw : `https://${{raw}}`;
                  popup(target);
                  return;
                }}
              }}
            }}
          }}
        }}
      }} catch (_) {{
        // ignore and fallback below
      }}
      if (fallbackUrl) {{
        popup(fallbackUrl);
        return;
      }}
      alert('QR 코드를 인식하지 못했습니다. 다른 위치를 클릭하거나 잠시 후 다시 시도해 주세요.');
    }}

    function pickDocs(docs) {{
      const keys = Object.keys(docs || {{}});
      const lawKey = keys.find(k => k.includes('법제처')) || keys[0] || null;
      const comicKey = keys.find(k => k.includes('만화')) || keys[1] || keys[0] || null;
      return {{ lawKey, comicKey }};
    }}

    function fillSelect(list) {{
      sel.innerHTML = '';
      for (const e of list) {{
        const opt = document.createElement('option');
        opt.value = e.article_key;
        opt.textContent = e.article_label;
        sel.appendChild(opt);
      }}
    }}

    function renderArticle(key) {{
      const e = DATA[key];
      if (!e) return;
      const docs = e.documents || {{}};
      const {{ lawKey, comicKey }} = pickDocs(docs);
      const lawDoc = lawKey ? docs[lawKey] : null;
      const comicDoc = comicKey ? docs[comicKey] : null;

      const allTitles = Object.values(docs).flatMap(d => d.titles || []);
      summary.textContent = `${{e.article_label}} | 제목: ${{allTitles.slice(0, 3).join(' / ')}}`;
      activeArticleKey = e.article_key;
      uploadScope.textContent = `현재 선택 조항(${{e.article_label}}) 기준으로 사진/범죄인지 예시가 저장됩니다. 사진 목록은 최대 6개까지만 화면에 표시됩니다.`;

      leftMeta.innerHTML = '';
      const p1 = document.createElement('span'); p1.className = 'pill'; p1.textContent = `조항: ${{e.article_label}}`;
      const p2 = document.createElement('span'); p2.className = 'pill'; p2.textContent = `법제처 페이지: ${{lawDoc?.first_page ?? '-'}}`;
      const p3 = document.createElement('span'); p3.className = 'pill'; p3.textContent = `만화 페이지: ${{comicDoc?.first_page ?? '-'}}`;
      leftMeta.appendChild(p1); leftMeta.appendChild(p2); leftMeta.appendChild(p3);

      comicImageWrap.innerHTML = '';
      if (comicDoc && comicDoc.first_image_file) {{
        const img = document.createElement('img');
        img.src = safeEncode(comicDoc.first_image_file);
        img.alt = e.article_label;
        img.loading = 'lazy';
        currentComicUrlFallback = extractFirstUrl(comicDoc.first_text_preview || '');
        img.style.cursor = 'zoom-in';
        img.title = 'QR 코드 영역을 클릭해 보세요';
        img.onclick = (ev) => tryOpenQrPopupFromImage(img, ev, currentComicUrlFallback);
        comicImageWrap.appendChild(img);
      }} else {{
        currentComicUrlFallback = '';
        comicImageWrap.textContent = '삽화 이미지가 없습니다.';
      }}

      const rawLawText = (lawDoc && lawDoc.first_text_preview) ? lawDoc.first_text_preview : '법제처 본문 미리보기가 없습니다.';
      lawText.innerHTML = annotateTerms(rawLawText);
      renderPhotos();
      renderCrimeExamples();
    }}

    function findCandidates(q) {{
      const qq = (q || '').trim();
      if (!qq) return entries;
      const n = qq.replace(/\s+/g, '');
      const num = n.match(/^제?(\d+)조(?:의(\d+))?$/);
      return entries.filter(e => {{
        const label = e.article_label.replace(/\s+/g, '');
        const titles = Object.values(e.documents || {{}}).flatMap(d => d.titles || []).join(' ').toLowerCase();
        if (num) {{
          const k = num[2] ? `${{parseInt(num[1], 10)}}-${{parseInt(num[2], 10)}}` : `${{parseInt(num[1], 10)}}`;
          return e.article_key === k;
        }}
        return label.includes(n) || e.article_key === n || titles.includes(qq.toLowerCase());
      }});
    }}

    function loadPhotos() {{
      try {{
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      }} catch (_) {{
        return [];
      }}
    }}

    function savePhotos(items) {{
      let arr = items.slice(0, MAX_PHOTOS);
      while (arr.length >= 0) {{
        try {{
          localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
          return true;
        }} catch (_) {{
          if (!arr.length) break;
          arr = arr.slice(0, arr.length - 1);
        }}
      }}
      return false;
    }}

    async function fileToCompressedDataUrl(file, maxW = 1400, quality = 0.72) {{
      const raw = await new Promise((resolve, reject) => {{
        const fr = new FileReader();
        fr.onload = () => resolve(fr.result);
        fr.onerror = reject;
        fr.readAsDataURL(file);
      }});

      const img = new Image();
      img.src = raw;
      await img.decode();

      const scale = Math.min(1, maxW / (img.naturalWidth || img.width || maxW));
      const w = Math.max(1, Math.round((img.naturalWidth || img.width) * scale));
      const h = Math.max(1, Math.round((img.naturalHeight || img.height) * scale));

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, w, h);
      return canvas.toDataURL('image/jpeg', quality);
    }}

    function loadCrimeExamples() {{
      try {{
        return JSON.parse(localStorage.getItem(CRIME_STORAGE_KEY) || '[]');
      }} catch (_) {{
        return [];
      }}
    }}

    function saveCrimeExamples(items) {{
      localStorage.setItem(CRIME_STORAGE_KEY, JSON.stringify(items));
    }}

    function applyReaction(item, target) {{
      const prev = item.reaction || '';
      item.likeCount = Number(item.likeCount || 0);
      item.dislikeCount = Number(item.dislikeCount || 0);

      if (target === 'like') {{
        if (prev === 'like') {{
          item.likeCount = Math.max(0, item.likeCount - 1);
          item.reaction = '';
        }} else if (prev === 'dislike') {{
          item.dislikeCount = Math.max(0, item.dislikeCount - 1);
          item.likeCount += 1;
          item.reaction = 'like';
        }} else {{
          item.likeCount += 1;
          item.reaction = 'like';
        }}
      }} else if (target === 'dislike') {{
        if (prev === 'dislike') {{
          item.dislikeCount = Math.max(0, item.dislikeCount - 1);
          item.reaction = '';
        }} else if (prev === 'like') {{
          item.likeCount = Math.max(0, item.likeCount - 1);
          item.dislikeCount += 1;
          item.reaction = 'dislike';
        }} else {{
          item.dislikeCount += 1;
          item.reaction = 'dislike';
        }}
      }}
    }}

    function renderPhotos() {{
      const items = loadPhotos().filter(x => (x.articleKey || '') === (activeArticleKey || ''));
      photoList.innerHTML = '';
      if (!items.length) {{
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = '현재 조항에 업로드된 사진이 없습니다.';
        photoList.appendChild(empty);
        return;
      }}

      const displayItems = items.slice(0, MAX_VISIBLE_PHOTOS);
      displayItems.forEach((item) => {{
        const card = document.createElement('div');
        card.className = 'photo-card';

        const img = document.createElement('img');
        img.src = item.dataUrl;
        img.alt = item.name || 'photo';
        img.style.cursor = 'zoom-in';
        img.title = '클릭하면 크게 보기';
        img.onclick = () => openImageModal(item.dataUrl, item.name || '현장 사진');

        const meta = document.createElement('div');
        meta.className = 'photo-meta';
        const date = new Date(item.createdAt || Date.now());
        meta.textContent = `${{item.name || 'image'}} | ${{date.toLocaleString()}}`;
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.textContent = item.articleLabel || '';

        const actions = document.createElement('div');
        actions.className = 'photo-actions';
        const openBtn = document.createElement('button');
        openBtn.className = 'btn-sub';
        openBtn.textContent = '원본 보기';
        openBtn.onclick = () => openImageModal(item.dataUrl, item.name || '현장 사진');

        const delBtn = document.createElement('button');
        delBtn.className = 'btn-sub';
        delBtn.textContent = '삭제';
        delBtn.onclick = () => {{
          const next = loadPhotos();
          const targetIdx = next.findIndex(p => p.id === item.id);
          if (targetIdx >= 0) next.splice(targetIdx, 1);
          savePhotos(next);
          renderPhotos();
        }};

        const react = document.createElement('div');
        react.className = 'react-row';
        const likeBtn = document.createElement('button');
        likeBtn.className = `react-btn ${{item.reaction === 'like' ? 'active-like' : ''}}`;
        likeBtn.textContent = `좋아요 ${{Number(item.likeCount || 0)}}`;
        likeBtn.onclick = () => {{
          const next = loadPhotos();
          const t = next.find(p => p.id === item.id);
          if (!t) return;
          applyReaction(t, 'like');
          savePhotos(next);
          renderPhotos();
        }};
        const dislikeBtn = document.createElement('button');
        dislikeBtn.className = `react-btn ${{item.reaction === 'dislike' ? 'active-dislike' : ''}}`;
        dislikeBtn.textContent = `싫어요 ${{Number(item.dislikeCount || 0)}}`;
        dislikeBtn.onclick = () => {{
          const next = loadPhotos();
          const t = next.find(p => p.id === item.id);
          if (!t) return;
          applyReaction(t, 'dislike');
          savePhotos(next);
          renderPhotos();
        }};
        react.appendChild(likeBtn);
        react.appendChild(dislikeBtn);

        actions.appendChild(openBtn);
        actions.appendChild(delBtn);

        card.appendChild(img);
        card.appendChild(meta);
        card.appendChild(tag);
        card.appendChild(react);
        card.appendChild(actions);
        photoList.appendChild(card);
      }});
      if (items.length > MAX_VISIBLE_PHOTOS) {{
        const more = document.createElement('div');
        more.className = 'empty';
        more.textContent = `사진은 최대 ${{MAX_VISIBLE_PHOTOS}}개까지 표시됩니다. (${{items.length - MAX_VISIBLE_PHOTOS}}개는 숨김)`;
        photoList.appendChild(more);
      }}
    }}

    function renderCrimeExamples() {{
      const items = loadCrimeExamples().filter(x => (x.articleKey || '') === (activeArticleKey || ''));
      crimeList.innerHTML = '';
      if (!items.length) {{
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = '현재 조항에 등록된 범죄인지 예시가 없습니다.';
        crimeList.appendChild(empty);
        return;
      }}

      items.forEach((item) => {{
        const row = document.createElement('div');
        row.className = 'crime-item';

        const text = document.createElement('div');
        text.className = 'crime-text';
        text.textContent = item.text || '';

        const meta = document.createElement('div');
        meta.className = 'crime-meta';
        meta.textContent = `${{item.articleLabel || ''}} | ${{new Date(item.createdAt || Date.now()).toLocaleString()}}`;

        const react = document.createElement('div');
        react.className = 'react-row';

        const likeBtn = document.createElement('button');
        likeBtn.className = `react-btn ${{item.reaction === 'like' ? 'active-like' : ''}}`;
        likeBtn.textContent = `좋아요 ${{Number(item.likeCount || 0)}}`;
        likeBtn.onclick = () => {{
          const all = loadCrimeExamples();
          const t = all.find(x => x.id === item.id);
          if (!t) return;
          applyReaction(t, 'like');
          saveCrimeExamples(all);
          renderCrimeExamples();
        }};

        const dislikeBtn = document.createElement('button');
        dislikeBtn.className = `react-btn ${{item.reaction === 'dislike' ? 'active-dislike' : ''}}`;
        dislikeBtn.textContent = `싫어요 ${{Number(item.dislikeCount || 0)}}`;
        dislikeBtn.onclick = () => {{
          const all = loadCrimeExamples();
          const t = all.find(x => x.id === item.id);
          if (!t) return;
          applyReaction(t, 'dislike');
          saveCrimeExamples(all);
          renderCrimeExamples();
        }};

        const delBtn = document.createElement('button');
        delBtn.className = 'react-btn';
        delBtn.textContent = '삭제';
        delBtn.onclick = () => {{
          const all = loadCrimeExamples().filter(x => x.id !== item.id);
          saveCrimeExamples(all);
          renderCrimeExamples();
        }};

        react.appendChild(likeBtn);
        react.appendChild(dislikeBtn);
        react.appendChild(delBtn);

        row.appendChild(text);
        row.appendChild(meta);
        row.appendChild(react);
        crimeList.appendChild(row);
      }});
    }}

    photoInput.addEventListener('change', async (ev) => {{
      const files = Array.from(ev.target.files || []);
      if (!files.length) return;

      const current = loadPhotos();
      for (const f of files) {{
        if (!f.type.startsWith('image/')) continue;
        const dataUrl = await fileToCompressedDataUrl(f);
        current.unshift({{
          id: `p_${{Date.now()}}_${{Math.random().toString(36).slice(2, 8)}}`,
          name: f.name,
          dataUrl,
          createdAt: new Date().toISOString(),
          articleKey: activeArticleKey,
          articleLabel: (DATA[activeArticleKey] || {{}}).article_label || '',
          reaction: '',
          likeCount: 0,
          dislikeCount: 0,
        }});
      }}
      const ok = savePhotos(current);
      if (!ok) alert('사진 저장 공간이 부족합니다. 기존 사진을 일부 삭제한 뒤 다시 시도해 주세요.');
      renderPhotos();
      photoInput.value = '';
    }});

    clearPhotosBtn.addEventListener('click', () => {{
      const left = loadPhotos().filter(x => (x.articleKey || '') !== (activeArticleKey || ''));
      savePhotos(left);
      renderPhotos();
    }});

    addCrimeBtn.addEventListener('click', () => {{
      const text = (crimeInput.value || '').trim();
      if (!text) return;
      const all = loadCrimeExamples();
      all.unshift({{
        id: `c_${{Date.now()}}_${{Math.random().toString(36).slice(2, 8)}}`,
        articleKey: activeArticleKey,
        articleLabel: (DATA[activeArticleKey] || {{}}).article_label || '',
        text,
        createdAt: new Date().toISOString(),
        reaction: '',
        likeCount: 0,
        dislikeCount: 0,
      }});
      saveCrimeExamples(all);
      crimeInput.value = '';
      renderCrimeExamples();
    }});

    lawText.addEventListener('mouseover', (ev) => {{
      const t = ev.target.closest('.term');
      if (!t) return;
      const term = t.getAttribute('data-term') || '';
      if (term && term !== termHoverWord) scheduleTermSearch(term, ev);
      showTermTooltip(t, ev);
    }});
    lawText.addEventListener('mousemove', (ev) => {{
      const t = ev.target.closest('.term');
      if (!t) return;
      positionTooltip(ev);
    }});
    lawText.addEventListener('mouseout', (ev) => {{
      if (!ev.target.closest('.term')) return;
      cancelTermSearch();
      hideTermTooltip();
    }});
    termTooltip.addEventListener('mouseleave', () => {{
      cancelTermSearch();
      hideTermTooltip();
    }});

    imageModalClose.addEventListener('click', closeImageModal);
    imageModal.addEventListener('click', (ev) => {{
      if (ev.target === imageModal) closeImageModal();
    }});
    webModalClose.addEventListener('click', closeWebModal);
    webModal.addEventListener('click', (ev) => {{
      if (ev.target === webModal) closeWebModal();
    }});
    window.addEventListener('keydown', (ev) => {{
      if (ev.key === 'Escape') {{
        closeImageModal();
        closeWebModal();
      }}
    }});

    function showWorkspace() {{
      homeScreen.style.display = 'none';
      workspace.style.display = 'block';
    }}

    function runSearch() {{
      showWorkspace();
      const q = (search.value || '').trim();
      let list = [];
      if (/^\\d+$/.test(q)) {{
        const key = String(parseInt(q, 10));
        list = entries.filter(e => e.article_key === key);
      }} else {{
        list = findCandidates(q);
      }}
      fillSelect(list.length ? list : entries);
      if (list.length) renderArticle(list[0].article_key);
      else summary.textContent = '검색 결과가 없습니다.';
    }}

    go.addEventListener('click', runSearch);
    search.addEventListener('keydown', (ev) => {{
      if (ev.key === 'Enter') {{
        ev.preventDefault();
        runSearch();
      }}
    }});

    sel.addEventListener('change', () => {{
      showWorkspace();
      renderArticle(sel.value);
    }});

    startBtn.addEventListener('click', () => {{
      showWorkspace();
      if (entries.length) renderArticle(entries[0].article_key);
    }});

    // home hero image: custom photo first, then comic illustration fallback
    try {{
      const first = entries[0];
      const docs = first ? Object.values(first.documents || {{}}) : [];
      const comic = docs.find(d => d.first_image_file && String(d.first_image_file).includes('만화')) || docs.find(d => d.first_image_file);
      const fallbackSrc = (comic && comic.first_image_file) ? safeEncode(comic.first_image_file) : '';
      homeHeroImg.onerror = () => {{
        if (fallbackSrc) homeHeroImg.src = fallbackSrc;
      }};
      homeHeroImg.src = safeEncode(CUSTOM_HOME_HERO);
    }} catch (_) {{}}

    fillSelect(entries);
    if (!entries.length) {{
      homeScreen.style.display = 'none';
      workspace.style.display = 'block';
      uploadScope.textContent = '조항 데이터가 없습니다.';
      renderPhotos();
      renderCrimeExamples();
    }}
  </script>
</body>
</html>
"""

    out_path.write_text(html, encoding='utf-8')
    print(out_path)


if __name__ == '__main__':
    main()
