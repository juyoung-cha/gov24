import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime
from typing import List, Dict, Set

# =========================
# 로깅 설정
# =========================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('rss_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =========================
# 설정 파일 로드
# =========================

CONFIG_FILE = "config.json"

def load_config():
    """설정 파일 로드"""
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"설정 파일 '{CONFIG_FILE}'이 없습니다. config.json을 생성해주세요.")
        raise FileNotFoundError(f"{CONFIG_FILE} 파일이 필요합니다.")
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

try:
    config = load_config()
    RSS_LIST = config["rss_feeds"]
    DATA_FILE = config["settings"]["data_file"]
    REQUEST_TIMEOUT = config["settings"].get("request_timeout", 10)
    ENABLE_TELEGRAM = config["settings"].get("enable_telegram", False)
    ENABLE_EMAIL = config["settings"].get("enable_email", False)
except Exception as e:
    logger.error(f"설정 파일 로드 실패: {e}")
    raise

# =========================
# RSS 수집
# =========================

def fetch_rss(name: str, url: str) -> List[Dict]:
    """RSS 피드 가져오기"""
    try:
        logger.info(f"[{name}] RSS 수집 시작: {url}")
        res = requests.get(url, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        res.encoding = "utf-8"

        soup = BeautifulSoup(res.text, "xml")
        items = soup.find_all("item")

        results = []
        for it in items:
            title = it.title.text.strip() if it.title else "제목 없음"
            link = it.link.text.strip() if it.link else ""
            
            # pubDate 형식이 다를 수 있으므로 유연하게 처리
            date = ""
            if it.pubDate:
                date = it.pubDate.text.strip()
            elif it.find("dc:date"):
                date = it.find("dc:date").text.strip()

            results.append({
                "dept": name,
                "title": title,
                "link": link,
                "date": date
            })

        logger.info(f"[{name}] {len(results)}개 항목 수집 완료")
        return results
    
    except requests.Timeout:
        logger.error(f"[{name}] 타임아웃 오류 (제한시간: {REQUEST_TIMEOUT}초)")
        return []
    except requests.HTTPError as e:
        logger.error(f"[{name}] HTTP 오류: {e.response.status_code} - {url}")
        return []
    except Exception as e:
        logger.error(f"[{name}] RSS 수집 오류: {str(e)}")
        return []


# =========================
# seen.json 처리
# =========================

def load_seen() -> Set[str]:
    """이미 확인한 링크 목록 로드"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"seen.json 로드 실패: {e}. 새로 시작합니다.")
            return set()
    return set()


def save_seen(seen: Set[str]):
    """확인한 링크 목록 저장"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen), f, ensure_ascii=False, indent=2)
        logger.info(f"seen.json 저장 완료 (총 {len(seen)}개 항목)")
    except Exception as e:
        logger.error(f"seen.json 저장 실패: {e}")


def filter_new(items: List[Dict], seen: Set[str]) -> List[Dict]:
    """새로운 항목만 필터링"""
    new_items = []
    for it in items:
        key = it["link"]
        if key and key not in seen:
            new_items.append(it)
            seen.add(key)
    return new_items


# =========================
# 텔레그램 알림
# =========================

def send_telegram(items: List[Dict]):
    """텔레그램으로 알림 전송"""
    if not items or not ENABLE_TELEGRAM:
        return

    try:
        bot_token = config["telegram"]["bot_token"]
        chat_id = config["telegram"]["chat_id"]
        
        if bot_token == "여기에_봇토큰" or chat_id == "여기에_채팅ID":
            logger.warning("텔레그램 설정이 필요합니다. config.json을 확인하세요.")
            return

        msg = "\n\n".join(
            f"📢 [{i['dept']}]\n{i['title']}\n{i['link']}\n{i['date']}"
            for i in items
        )

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(
            url, 
            data={"chat_id": chat_id, "text": msg},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"텔레그램 알림 전송 완료 ({len(items)}개 항목)")
    
    except Exception as e:
        logger.error(f"텔레그램 전송 실패: {e}")


# =========================
# 이메일 알림
# =========================

def send_email(items: List[Dict]):
    """이메일로 알림 전송"""
    if not items or not ENABLE_EMAIL:
        return

    try:
        smtp_config = config["email"]
        
        if smtp_config["smtp_user"] == "본인이메일@gmail.com":
            logger.warning("이메일 설정이 필요합니다. config.json을 확인하세요.")
            return

        body = "\n\n".join(
            f"[{i['dept']}]\n{i['title']}\n{i['link']}\n{i['date']}"
            for i in items
        )

        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = f"새 정부부처 보도자료 {len(items)}건"
        msg["From"] = smtp_config["smtp_user"]
        msg["To"] = smtp_config["to_email"]

        with smtplib.SMTP_SSL(smtp_config["smtp_host"], smtp_config["smtp_port"]) as s:
            s.login(smtp_config["smtp_user"], smtp_config["smtp_password"])
            s.send_message(msg)
        
        logger.info(f"이메일 알림 전송 완료 ({len(items)}개 항목)")
    
    except Exception as e:
        logger.error(f"이메일 전송 실패: {e}")


# =========================
# 메인
# =========================

def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("정부 RSS 모니터링 시작")
    logger.info("=" * 50)

    seen = load_seen()
    all_items = []
    success_count = 0
    fail_count = 0

    for dept, url in RSS_LIST.items():
        items = fetch_rss(dept, url)
        if items:
            all_items.extend(items)
            success_count += 1
        else:
            fail_count += 1

    logger.info(f"RSS 수집 완료: 성공 {success_count}개, 실패 {fail_count}개")

    new_items = filter_new(all_items, seen)

    if new_items:
        logger.info(f"🆕 새 글 발견: {len(new_items)}개")
        logger.info("-" * 50)

        for d in new_items:
            logger.info(f"[{d['dept']}] {d['title']}")
            logger.info(f"링크: {d['link']}")
            logger.info(f"날짜: {d['date']}")
            logger.info("-" * 50)

        # 알림 전송
        send_telegram(new_items)
        send_email(new_items)
        
        # seen.json 저장
        save_seen(seen)
    else:
        logger.info("새 글 없음")

    logger.info("정부 RSS 모니터링 종료")
    logger.info("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 오류: {e}", exc_info=True)
