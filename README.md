# 🏛️ 대한민국 정책 매거진 24 (gov24) 자동화 시스템

대한민국 국가 부처 및 서울특별시의 공식 보도자료를 수집하여, 20년 경력의 베테랑 칼럼니스트 시각으로 분석한 고품질 생활 밀착형 꿀팁 콘텐츠를 구글 블로거(Blogger)에 **100% 완전 무료(Zero Cost)**로 자동 발행하는 시스템입니다.

---

## 🌟 주요 특징

- **100% 무료 무중단 자동화 (Zero Cost)**:
  - **GitHub Actions**: 매일 오전 7시(KST) 자동 크론 실행 (스케줄러 무료)
  - **Google Gemini API**: Free Tier 활용 (AI 생성 무료)
  - **Google Blogger API**: 무제한 무료 호스팅
- **고클릭률(High CTR) 실생활 혜택 주제 엄선**:
  - 단순 인사/행정공고/사업장 안전 수칙 100% 컷오프
  - 정부 지원금·환급금, 교통비 절약(K-패스, 기후동행카드), 청년/중장년 주거·일자리 혜택 선별
- **반응형(PC/모바일/태블릿) 무결점 렌더링**:
  - 모바일 표(Table) 가로 스크롤 래퍼 자동 감싸기
  - 카드형 Q&A 박스, 하이라이트 배너, 공식 출처 안내 박스 등 상용화 수준 인라인 UI
- **구글 애드센스 E-E-A-T 검수 완벽 충족**:
  - 3,000자 이상의 심층 스토리텔링 및 공감 1인칭 가이드

---

## 📁 프로젝트 핵심 파일 구조

```
d:\AI\gov24\
├── main.py                     # 메인 자동화 파이프라인 진입점
├── blog_writer.py              # Gemini AI 고품격 작성 및 정밀 파서 엔진
├── blogger_poster.py           # Google Blogger API OAuth v3 연동 모듈
├── rss_collector.py            # 정부 부처/지자체 공식 RSS 및 정책뉴스 수집기
├── content_scraper.py          # 공식 보도자료 본문 및 이미지 크롤러
├── storage_manager.py          # 발행 이력(seen.json) 및 스토리지 관리자
├── check_token_health.py       # OAuth 토큰 사전 검증 및 자동 갱신 헬퍼
├── clean_existing_posts.py     # 기존 포스트 본문 메타 잔여물 및 라벨 일괄 정제
├── clean_duplicate_pages.py    # 필수 3대 페이지(소개, 약관, 문의) 유지 및 중복 정리
├── config.json                 # RSS 피드, 점수 기준, 블로그 ID 등 메인 설정
├── credentials.json            # Google OAuth 2.0 클라이언트 비밀키
├── token.pickle                # Google Blogger API 인증 토큰
├── seen.json                   # 중복 포스팅 방지 링크 히스토리
├── requirements.txt            # 파이썬 의존 패키지 목록
├── Run_Daily_HQ.bat            # 윈도우 원클릭 수동 실행 배치 파일
│
├── .github/workflows/
│   └── auto_posting.yml        # GitHub Actions 매일 오전 7시 자동 실행 크론
│
└── archive_backup_20260903/   # 과거 테스트/임시/레거시 파일 안전 보관함
    ├── docs_guides/            # 과거 가이드 및 히스토리 마크다운 문서
    ├── test_scripts/           # 과거 테스트 및 1회성 스크립트
    ├── temp_files/             # 과거 임시 HTML 및 텍스트 파일
    └── legacy_folders/         # 과거 레거시 폴더 (scratch, backup 등)
```

---

## 🚀 실행 및 운영 방법

### 1. 로컬 수동 실행
```bash
# 가상환경 활성화 후
python main.py
# 또는
Run_Daily_HQ.bat 더블 클릭
```

### 2. 토큰 상태 확인
```bash
python check_token_health.py
```

### 3. GitHub Actions 자동 실행
- 매일 한국 시간 **오전 7시 (UTC 22:00)**에 `.github/workflows/auto_posting.yml`이 자동으로 실행되어 포스팅을 진행합니다.
