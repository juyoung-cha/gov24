"""
원문 콘텐츠 크롤링 모듈
RSS 피드의 링크에서 실제 보도자료 본문을 추출합니다.
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ContentScraper:
    """원문 콘텐츠 스크래퍼"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
    
    def scrape(self, url: str) -> Optional[Dict]:
        """
        URL에서 본문 내용 추출
        
        Args:
            url: 원문 URL
            
        Returns:
            {"content": str, "images": List[str]} 또는 None
        """
        try:
            logger.info(f"원문 크롤링 시작: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            res = requests.get(url, headers=headers, timeout=self.timeout)
            res.raise_for_status()
            res.encoding = "utf-8"
            
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 본문 추출 (사이트별로 다를 수 있음)
            content = self._extract_content(soup, url)
            images = self._extract_images(soup, url)
            publish_date = self._extract_publish_date(soup, url)
            
            if not content:
                logger.warning(f"본문 내용을 찾을 수 없습니다: {url}")
                return None
            
            logger.info(f"크롤링 완료 (본문: {len(content)}자, 이미지: {len(images)}개, 발행일: {publish_date})")
            
            return {
                "content": content,
                "images": images,
                "publish_date": publish_date
            }
        
        except Exception as e:
            logger.error(f"크롤링 오류: {url} - {str(e)}")
            return None

    def _extract_publish_date(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """
        상세 페이지에서 정확한 발행일 추출
        """
        if "seoul.go.kr" in url or "mediahub.seoul.go.kr" in url:
            # "발행일" 텍스트를 포함한 p.date 태그 찾기
            date_ps = soup.select(".news_detail_top .info_view p.date")
            for p in date_ps:
                if "발행일" in p.get_text():
                    num_span = p.select_one("span.num")
                    if num_span:
                        return num_span.get_text(strip=True)
            
            # 다른 패턴 시도
            date_elem = soup.select_one(".date_area") or soup.select_one(".post-date")
            if date_elem:
                return date_elem.get_text(strip=True)
                
        return None
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        본문 텍스트 추출 (사이트별 선택자 처리)
        """
        # korea.kr 사이트
        if "korea.kr" in url:
            content_div = soup.find("div", class_="view_cont")
            if content_div:
                # [FIX] HTML 구조 보존 및 이미지 경로 보완
                import re
                content_html = content_div.decode_contents().strip()
                content_html = re.sub(r"<!--.*?-->", "", content_html, flags=re.DOTALL)
                
                # 이미지 경로가 상대 경로인 경우 절대 경로로 변환
                if 'src="/' in content_html:
                    content_html = content_html.replace('src="/', 'src="https://www.korea.kr/')
                
                return content_html
        
        # mohw.go.kr 사이트 (보건복지부)
        if "mohw.go.kr" in url:
            content_div = (
                soup.select_one(".view_cont") or 
                soup.select_one(".vc_detail") or 
                soup.select_one("#contents") or
                soup.select_one(".article-body")
            )
            if content_div:
                import re
                content_html = content_div.decode_contents().strip()
                content_html = re.sub(r"<!--.*?-->", "", content_html, flags=re.DOTALL)
                
                # 이미지 경로가 상대 경로인 경우 절대 경로로 변환
                if 'src="/' in content_html:
                    content_html = content_html.replace('src="/', 'src="https://www.mohw.go.kr/')
                
                return content_html

        # seoul.go.kr 또는 mediahub.seoul.go.kr 사이트
        if "seoul.go.kr" in url or "mediahub.seoul.go.kr" in url:
            # 본문 영역 (itemprop="articleBody" 우선, 그 다음 #view_ct, 그 다음 #post_content)
            content_div = (
                soup.select_one("[itemprop='articleBody']") or
                soup.select_one("#view_ct") or
                soup.select_one("#post_content") or 
                soup.select_one(".post-content") or 
                soup.select_one(".view_cont") or 
                soup.select_one(".news-view-content") or 
                soup.select_one("#content")
            )
            if content_div:
                # 불필요한 영역 제거 (SNS, 버튼, 광고, 만족도 조사 등)
                for s in content_div.select(".btn_area, .view_info, .sns_area, .sns_elem, #sns_elem, .comment_eungdapso, .top-row, .sib-viw-board-rating, .mail_box, .view_comment, .related_posts"):
                    s.decompose()
                
                # [FIX] HTML 주석 제거 및 이미지 경로 보완
                import re
                content_html = content_div.decode_contents().strip()
                content_html = re.sub(r"<!--.*?-->", "", content_html, flags=re.DOTALL)
                
                # 이미지 경로가 상대 경로인 경우 절대 경로로 변환
                if 'src="/' in content_html:
                    if "mediahub.seoul.go.kr" in url:
                        content_html = content_html.replace('src="/', 'src="https://mediahub.seoul.go.kr/')
                    else:
                        content_html = content_html.replace('src="/', 'src="https://www.seoul.go.kr/')
                
                return content_html

        # 마지막 수단: body 전체에서 추출
        body = soup.find("body")
        if body:
            # 스크립트, 스타일 제거
            for script in body(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            return body.get_text(strip=True, separator="\n")
        
        return ""
    
    def _extract_images(self, soup: BeautifulSoup, url: str) -> list:
        """이미지 URL 추출 (상대 경로 대응)"""
        images = []
        base_url = "https://www.korea.kr" if "korea.kr" in url else \
                   "https://mediahub.seoul.go.kr" if "mediahub" in url else \
                   "https://www.seoul.go.kr" if "seoul.go.kr" in url else ""
        
        # 본문 영역 내부의 이미지만 추출 시도
        content_area = (
            soup.find("div", class_="view_cont") or 
            soup.select_one("[itemprop='articleBody']") or
            soup.select_one("#view_ct") or
            soup.select_one("#post_content") or
            soup
        )

        for img in content_area.find_all("img"):
            src = img.get("src")
            if not src: continue
            
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/") and base_url:
                src = base_url + src
            elif not src.startswith("http") and base_url:
                src = base_url + "/" + src
            
            if src.startswith("http") and src not in images:
                # 불필요한 아이콘 이미지 등 제외 필터링
                ignore_keywords = [
                    "icon", "btn", "spacer", "sns", "satisfaction", 
                    "facebook", "twitter", "kakao", "naver", "blog",
                    "taegeukgi", "logo", "emblem", "common"
                ]
                if any(x in src.lower() for x in ignore_keywords):
                    continue
                images.append(src)
        
        return images[:3]  # 최대 3개만
