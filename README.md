# education

산업안전보건기준 조항을 현장에 빠르게 적용하기 위한 MVP 프로젝트입니다.

## 프로젝트 개요
- 법조항(산업안전보건기준에 관한 규칙) 검색 및 열람
- 조항별 삽화(만화본) 확인
- 근로감독관 현장 사진 업로드/조회
- 사진 및 범죄인지 예시에 대한 좋아요/싫어요 집단평가
- 단어 호버 시 뜻/대표 이미지 보조 조회
- QR 코드 클릭 시 화면 내부 팝업으로 관련 웹페이지 열람

## 주요 파일
- `scripts/index_articles.py`: 조항 인덱싱 스크립트
- `scripts/build_article_viewer.py`: 단일 HTML 뷰어 생성 스크립트
- `output/article_viewer.html`: 생성된 실행 화면

## 실행 방법
1. 인덱스 생성
   ```bash
   python3 scripts/index_articles.py
   ```
2. 뷰어 생성
   ```bash
   python3 scripts/build_article_viewer.py \
     --index-json output/index/article_index_master.json \
     --out-html output/article_viewer.html
   ```
3. 화면 열기
   - `output/article_viewer.html` 파일을 브라우저에서 열어 사용

## 비고
- 현재 버전은 빠른 검증을 위한 MVP이며, 향후 DB/API 연동 및 권한/이력 관리 기능 확장을 전제로 합니다.
