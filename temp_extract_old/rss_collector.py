"""
RSS 피드 수집 및 파싱 모듈
정부 부처 RSS 피드에서 새로운 보도자료/정책 정보를 수집합니다.
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Set

logger = logging.getLogger(__name__)


class RSSCollector:
    """RSS 피드 수집기"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
    
    def fetch_rss(self, name: str, url: str) -> List[Dict]:
        """
        RSS 피드 가져오기 (서울시 정책뉴스는 HTML 크롤링으로 처리)
        
        Args:
            name: 부처명
            url: RSS 피드 URL
            
        Returns:
            수집된 항목 리스트 [{"dept": str, "title": str, "link": str, "date": str}]
        """
        if name == "서울시 정책뉴스" or "seoul.go.kr" in url:
            return self._fetch_seoul_news(url)
            
        try:
            logger.info(f"[{name}] RSS 수집 시작: {url}")
            res = requests.get(url, timeout=self.timeout)
            res.raise_for_status()
            res.encoding = "utf-8"

            soup = BeautifulSoup(res.content, "xml")
            items = []
            
            for entry in soup.find_all("item"):
                title = entry.find("title").get_text(strip=True) if entry.find("title") else "제목 없음"
                link = entry.find("link").get_text(strip=True) if entry.find("link") else ""
                description = entry.find("description").get_text(strip=True) if entry.find("description") else ""
                pub_date = entry.find("pubDate").get_text(strip=True) if entry.find("pubDate") else ""
                
                # pubDate 형식이 다를 수 있으므로 유연하게 처리
                date = ""
                if entry.pubDate:
                    date = entry.pubDate.text.strip()
                elif entry.find("dc:date"):
                    date = entry.find("dc:date").text.strip()
                elif pub_date: # Fallback to pub_date extracted above
                    date = pub_date

                items.append({
                    "dept": name,
                    "title": title,
                    "link": link,
                    "description": description,
                    "date": date
                })

            logger.info(f"[{name}] {len(items)}개 항목 수집 완료")
            return items
        
        except requests.Timeout:
            logger.error(f"[{name}] 타임아웃 오류 (제한시간: {self.timeout}초)")
            return []
        except requests.HTTPError as e:
            logger.error(f"[{name}] HTTP 오류: {e.response.status_code} - {url}")
            return []
        except Exception as e:
            logger.error(f"[{name}] RSS 수집 오류: {str(e)}")
            return []

    def _fetch_seoul_news(self, url: str) -> List[Dict]:
        """
        공식 서울시 정책뉴스 페이지(HTML)에서 뉴스 목록 추출 (여러 페이지 수집)
        """
        try:
            items = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # 1페이지부터 5페이지까지 수집 (2026년 기사 전량 확보 목적)
            for page in range(1, 6):
                logger.info(f"서울시 정책뉴스(HTML) 수집 중... (페이지: {page})")
                
                try:
                    if page == 1:
                        res = requests.get(url, headers=headers, timeout=self.timeout)
                    else:
                        # 2페이지 이후는 POST 요청 (fetchStart 파라미터 사용)
                        data = {"fetchStart": str(page)}
                        res = requests.post(url, headers=headers, data=data, timeout=self.timeout)
                    
                    res.raise_for_status()
                    res.encoding = 'utf-8'
                    
                    soup = BeautifulSoup(res.text, "html.parser")
                    
                    # 리스트 컨테이너를 먼저 찾아 그 안의 item만 수집
                    container = soup.select_one(".news-lst-policy") or soup.select_one("#content") or soup.select_one(".sp_list-wrap") or soup
                    news_list = container.select(".item") or container.select("div.item") or container.select("ul.news-list-item li")
                    
                    if not news_list:
                        logger.warning(f"{page}페이지에 뉴스 항목이 없습니다.")
                        break # 더 이상 페이지가 없으면 종료
                        
                    page_item_count = 0
                    for li in news_list:
                        # [제목]
                        title_tag = li.select_one(".subject") or li.select_one(".title") or li.select_one("dt a") or li.select_one("strong") or li.select_one("a")
                        # [링크]
                        link_tag = li.select_one(".content_more_span_link a") or li.select_one("a.links") or li.select_one("a")
                        # [날짜]
                        date_tag = li.select_one(".info span") or li.select_one(".date") or li.select_one("span.date") or li.select_one(".day")
                        
                        if title_tag and link_tag:
                            title = title_tag.get_text(strip=True)
                            link = link_tag.get("href")
                            
                            if not link or "javascript" in link:
                                for a in li.select("a"):
                                    href = a.get("href")
                                    if href and ("http" in href or "/archives/" in href):
                                        link = href
                                        break
                            
                            if not link: continue
                            
                            if link.startswith("/"):
                                link = ("https://mediahub.seoul.go.kr" if "mediahub" in link else "https://www.seoul.go.kr") + link
                            
                            date_str = date_tag.get_text(strip=True).replace("발행일", "").strip() if date_tag else ""
                            
                            # 날짜 필터링 (2025-06-01 이후 기사만 수집)
                            if date_str:
                                try:
                                    clean_date = date_str.replace(".", "-")
                                    if len(clean_date) >= 10:
                                        if clean_date[:10] < "2025-06-01":
                                            continue
                                except: pass

                            items.append({
                                "dept": "서울시 정책뉴스",
                                "title": title,
                                "link": link,
                                "date": date_str
                            })
                            page_item_count += 1
                    
                    logger.info(f"{page}페이지 수집 완료: {page_item_count}개 항목")
                    
                except Exception as e:
                    logger.error(f"{page}페이지 수집 중 오류: {e}")
                    continue

            # 중복 제거 (여러 페이지 긁을 때 중복 발생 가능성 대비)
            unique_items = []
            seen_links = set()
            for item in items:
                if item["link"] not in seen_links:
                    unique_items.append(item)
                    seen_links.add(item["link"])
            
            logger.info(f"서울시 정책뉴스 총 {len(unique_items)}개 항목 수집 완료 (중복 제외)")
            return unique_items
            
        except Exception as e:
            logger.error(f"서울시 정책뉴스 수집 오류: {str(e)}")
            return []
    
    def fetch_all(self, rss_feeds: Dict[str, str]) -> List[Dict]:
        """
        모든 RSS 피드 수집
        
        Args:
            rss_feeds: {부처명: RSS_URL} 딕셔너리
            
        Returns:
            전체 수집 항목 리스트
        """
        all_items = []
        success_count = 0
        fail_count = 0
        
        for dept, url in rss_feeds.items():
            items = self.fetch_rss(dept, url)
            if items:
                all_items.extend(items)
                success_count += 1
            else:
                fail_count += 1
        
        logger.info(f"RSS 수집 완료: 성공 {success_count}개, 실패 {fail_count}개")
        return all_items
    
    def filter_new_items(self, items: List[Dict], seen: Set[str]) -> List[Dict]:
        """
        새로운 항목만 필터링 (seen에 추가하지 않음)
        
        seen 추가는 포스팅 성공 시 main.py에서 처리
        
        Args:
            items: 전체 항목 리스트
            seen: 이미 확인한 링크 셋
            
        Returns:
            새로운 항목 리스트
        """
        new_items = []
        for item in items:
            link = item["link"]
            if link and link not in seen:
                new_items.append(item)
                # seen.add(link) 제거 - 성공 시에만 추가하도록 변경
        
        logger.info(f"새 글 발견: {len(new_items)}개")
        return new_items
