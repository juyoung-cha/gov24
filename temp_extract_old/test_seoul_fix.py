
import logging
from rss_collector import RSSCollector
from content_scraper import ContentScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_seoul_mediahub():
    collector = RSSCollector()
    scraper = ContentScraper()
    
    url = "https://www.seoul.go.kr/seoul/mediahub.do?schAgeVals=&schTargetVals=&schBunyaVals=&schType=TAG&schValue="
    
    logger.info("1. 리스트 수집 테스트...")
    items = collector._fetch_seoul_news(url)
    
    if not items:
        logger.error("기사를 하나도 수집하지 못했습니다.")
        return
        
    logger.info(f"수집된 기사 수: {len(items)}")
    
    # 첫 번째 기사로 본문 추출 테스트
    test_item = items[0]
    logger.info(f"2. 본문 추출 테스트 (URL: {test_item['link']}, 제목: {test_item['title']})")
    
    content = scraper.scrape(test_item['link'])
    
    if content:
        logger.info("본문 추출 성공!")
        logger.info(f"본문 길이: {len(content)}")
        if "<table" in content:
            logger.info("표(Table) 감지됨!")
        if "<img" in content:
            logger.info("이미지(Img) 감지됨!")
        
        # 샘플 출력 (앞부분 500자)
        print("\n--- SAMPLE CONTENT ---")
        print(str(content)[:500])
        print("----------------------\n")
    else:
        logger.error("본문 추출 실패")

if __name__ == "__main__":
    test_seoul_mediahub()
