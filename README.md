# Multi Hotdeal Notifier

여러 핫딜 사이트를 주기적으로 확인하여  
새 게시글이 등록되면 Discord로 알림을 보내는 Python 기반 자동화 프로젝트입니다.

이 프로젝트는 단순 크롤러가 아니라,  
여러 사이트를 독립적으로 감시하고 게시글 이력을 저장하여  
중복 없이 새 글만 감지하는 **멀티 사이트 핫딜 알림 시스템**으로 설계되었습니다.

---

# Features

- 여러 핫딜 사이트 게시글 수집
- 사이트별 최신 게시글 자동 추출
- SQLite 기반 게시글 이력 저장
- 이전 게시글과 비교하여 새 글 감지
- Discord Webhook 알림 전송
- APScheduler 기반 주기 실행
- `.env` 기반 환경변수 설정
- 멀티 사이트 확장 가능한 크롤러 구조

---

# Supported Sites

- FM코리아 핫딜
- 루리웹 핫딜
- 어미새 인기정보

---

# Tech Stack

## Backend

- Python

## Libraries

- requests  
- BeautifulSoup4  
- APScheduler  
- python-dotenv  

## Storage

- SQLite

---

# Project Structure

```
multi-hotdeal-notifier/
├── app.py
├── config.py
├── db.py
├── notifier.py
├── scheduler.py
├── run.py
├── requirements.txt
├── sites.json
├── .env.example
├── .gitignore
├── README.md
└── crawlers/
    ├── __init__.py
    ├── fmkorea.py
    ├── ruliweb.py
    └── eomisae.py
```

---

# Setup

## 1. Create virtual environment

```
python -m venv .venv
```

## 2. Activate virtual environment

### Windows

```
.venv\Scripts\activate
```

### Mac / Linux

```
source .venv/bin/activate
```

## 3. Install dependencies

```
pip install -r requirements.txt
```

---

# Environment Variables

프로젝트 루트에 `.env` 파일을 생성합니다.

Example:

```
DISCORD_WEBHOOK_URL=your_discord_webhook_url
CHECK_INTERVAL_MINUTES=10
```

| Variable | Description |
|--------|--------|
| DISCORD_WEBHOOK_URL | Discord webhook URL for notifications |
| CHECK_INTERVAL_MINUTES | 게시글 확인 주기 (분) |

---

# Run

## One-time check

```
python app.py
```

## Run scheduler

```
python run.py
```

정상 실행 시 예시:

```
스케줄러 시작: 10분마다 점검
[CHECK] 사이트 점검 시작
```

---

# How it works

동작 흐름:

1. `sites.json`에서 감시할 사이트 목록 로드  
2. 사이트별 크롤러 실행  
3. 최신 게시글 목록 수집  
4. SQLite DB에 저장된 기존 게시글과 비교  
5. 새 글만 Discord Webhook으로 전송  
6. 새 게시글 이력을 DB에 저장  

---

# System Flow

```
sites.json
     │
     ▼
Crawler (per site)
     │
     ▼
Collect latest posts
     │
     ▼
Compare with SQLite DB
     │
 ┌───┴──────────────┐
 │                  │
No new post     New post detected
 │                  │
 ▼                  ▼
Ignore          Send Discord Webhook
                     │
                     ▼
               Save to SQLite
```

---

# Design Notes

이 프로젝트는 상품 단위 중복 제거보다  
**사이트별 게시글 신규 감지**를 우선하도록 설계했습니다.

핫딜 게시판은 같은 상품이라도 사이트마다 제목, 할인 조건, 설명 방식, 강조 포인트가 다르기 때문에  
동일 상품 여부보다 **각 사이트의 새 게시글 자체를 독립적인 정보**로 판단했습니다.

---

# Current Limitations

일부 사이트는 요청 빈도나 접근 방식에 따라 차단 응답이 발생할 수 있습니다.

특히 **FM코리아**는 상황에 따라 접근이 불안정할 수 있어  
추가적인 안정화가 필요합니다.

---

# Future Improvements

- 추가 핫딜 사이트 확장
- 키워드 기반 맞춤 알림
- 제외 키워드 기능
- Discord 임베드 메시지
- Docker 배포
- Oracle Cloud / systemd 운영 자동화

---

# Author

GitHub  
https://github.com/cbssmh
