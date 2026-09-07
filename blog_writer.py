import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
import json
import logging
import google.generativeai as genai
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BlogWriter:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        api_key = self.config.get("gemini", {}).get("api_key") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # fallback to alternative keys if available
            api_key = self.config.get("api_keys", {}).get("gemini_api_key")
        genai.configure(api_key=api_key)
        model_name = self.config.get("gemini", {}).get("model", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name)
        
    def _create_prompt(self, title: str, content: str, dept: str, images: list = None, recent_posts: list = None) -> str:
        """Gemini에게 전달할 고클릭률 및 고품격 공감 스토리텔링 프롬프트"""
        
        max_content_length = 6500
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        image_prompt = "원문에 이미지가 없으므로, 텍스트와 시각적 표(table), 인용 박스만으로 정보를 완벽하게 구조화하세요."
        if images:
            image_prompt = "\n**이미지 활용 지침:**\n"
            for i, img_url in enumerate(images[:3], 1):
                image_prompt += f"- 이미지{i} URL: {img_url}\n"
            image_prompt += "위 이미지들을 본문의 흐름에 맞춰 <img src='이미지URL' style='max-width:100%; height:auto; margin:25px 0; border-radius:12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); display:block;'> 태그로 삽입하세요.\n"

        internal_link_prompt = ""
        if recent_posts:
            internal_link_prompt = "\n**내부 추천 글 링크 지침:**\n아래 최근 글 중 이번 주제와 연관된 글이 있다면, 본문 중반에 자연스럽게 추천 링크를 1~2개 삽입하세요.\n"
            for rp in recent_posts[:5]:
                internal_link_prompt += f"- [{rp['title']}]({rp['url']})\n"
            internal_link_prompt += "형식: <p style='background:#f1f5f9; padding:16px 20px; border-left:5px solid #2563eb; border-radius:6px; margin:25px 0;'><a href='URL' style='text-decoration:none; color:#1e293b; font-weight:700; font-size:15px;'>📌 함께 읽으면 도움되는 정책: {rp['title']} 바로가기 →</a></p>\n"

        prompt = f"""
당신은 대한민국 최고의 정책 저널리스트이자 20년 경력의 베테랑 칼럼니스트입니다.
포털 검색자(직장인, 주부, 청년, 시니어 등)가 제목을 보자마자 클릭하고 끝까지 읽게 만드는 '최고급 생활 밀착형 꿀팁 분석글'을 작성하세요.

[핵심 목표: 고클릭률 & 구글 애드센스 E-E-A-T 완벽 통과]
1. 제목 원칙 (극도로 중요):
   - 딱딱한 행정 보도자료 제목, 단순 공고형 제목, 훈계조는 절대 금지!
   - 사람들의 호기심과 실질적 혜택을 자극하는 질문형/숫자형/공감형 헤드라인을 만드세요.
   - 예시 스타일: 
     * '월 최대 50만원 지원? 놓치면 나만 손해 보는 2026 OO 지원금 완벽 정리!'
     * '전세금 걱정 끝! 서울시 OO 아파트 20년 내 집처럼 사는 신청 비법 대공개'
     * '교통비 절반으로 줄이는 숨겨진 꿀팁! OO카드 200% 활용 가이드'

2. 페르소나 및 문체:
   - 20년 경력의 따뜻하고 통찰력 있는 시니어 칼럼니스트 (친절하고 신뢰감 넘치는 '~입니다', '~하시죠?' 체).
   - 독자의 현실적인 고민(물가, 주거비, 육아, 자녀 교육, 재취업, 노후, 세금)을 짚어주며 깊은 공감 형성.

3. 필수 본문 구조 (3,000자 이상의 깊이 있는 고품질 장문):
   ① [따뜻한 인사 및 일상 공감 서두]: 최근 독자들의 현실 고민 공감 + 이번 정책이 주는 핵심 혜택 3줄 요약
   ② [실생활 Q&A 꿀팁 3문 3답]: 독자가 가장 궁금해할 핵심 질문 3개를 <h3> 및 <blockquote> 박스로 명쾌하게 해설
   ③ [한눈에 보는 자격 요건 & 지원 혜택 표]: <div style="overflow-x:auto; width:100%; margin:25px 0;"> 안에 세련된 <table>로 일목요연 정리
   ④ [담당자도 안 알려주는 신청 성공률 200% 높이는 실전 팁]: 필수 서류, 타이밍, 놓치기 쉬운 주의사항
   ⑤ [따뜻한 응원과 마무리 메시지]: 삶을 격려하는 칼럼니스트의 진정성 있는 맺음말

4. HTML 스타일링 가이드:
   - 순수 HTML 시맨틱 태그(article, section, h2, h3, p, blockquote, table, div 등)를 사용하세요.
   - 절대 ```html 같은 마크다운 코드블록 백틱으로 감싸지 마세요.
   - 표(table)는 테두리, 헤더 배경(#f8fafc), 패딩이 깔끔한 모던 스타일을 적용하세요.

{image_prompt}
{internal_link_prompt}

원문 정보:
- 제공 기관: {dept}
- 원문 제목: {title}
- 세부 내용: {content}

[반드시 준수할 출력 형식]:
메타설명: [검색 결과 스니펫에 노출될 140자 이내의 매력적인 요약문]

제목: [클릭을 부르는 매력적이고 세련된 헤드라인]

본문:
<article style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; font-size: 16px; line-height: 1.8; color: #2d3748; word-break: keep-all;">
... (3,000자 이상의 풍부한 본문 내용) ...
</article>

태그: #핵심태그1 #핵심태그2 #핵심태그3 #핵심태그4 #핵심태그5
"""
        return prompt

    def evaluate_item_relevance(self, title: str, content: str) -> dict:
        """수집된 기사가 일반 독자에게 흥미롭고 실생활에 직접 밀착된 혜택/소식인지 평가"""
        logger.info(f"아이템 대중 흥미도 및 유용성 평가 시작: {title[:40]}...")
        
        short_content = content[:1500] if len(content) > 1500 else content
        
        prompt = f"""
당신은 대중이 정말로 읽고 싶어 하는 흥미로운 이슈와 생활 혜택을 선별하는 베테랑 뉴스 에디터입니다.
다음 소식이 일반 시민(직장인, 청년, 주부, 소상공인 등)이 직접 혜택을 받거나 클릭하고 싶어 하는 흥미로운 생활 밀착형 정보인지 1~10점으로 평가해 주세요.

[❌ 절대 탈락 및 감점 대상 (1~6점 수준)]
- 선거 현수막 작업 안전, 건설 현장 안전 수칙, 특정 산업 안전 지침 등 일반 시민과 무관한 작업장 안전 공고
- 부처/지자체의 단순 해명자료, 설명자료, 내부 동정 (인사, 훈장 수여, 위원회 개최, 업무협약식 체결 등)
- 일반 시민이 이용할 수 없는 전문 기업/학술 고시, 행정 편의적 지침, 통계 조사 방식 변경 등
- 클릭하고 싶은 생각이 전혀 들지 않는 관료적이고 재미없는 행정 공고

[✅ 적극 선택 및 가점 대상 (8~10점 수준)]
- 지원금, 환급금, 보조금, 교통비 절약(K-패스, 기후동행카드 등) 직접적인 돈이 되는 혜택
- 가성비 주말 나들이, 무료 전시/축제, 휴가철 피서지, 맛집/문화 소식
- 청년/신혼부부 전세/임차보증금 지원, 주택/부동산 실생활 꿀팁, 노후 자산 관리, 세금 절세
- 일상생활에서 바로 활용할 수 있는 건강, 육아, 자녀 교육, 재취업, 복지 서비스

[출력 형식]
점수: [1에서 10 사이의 정수]
이유: [평가 이유 1문장]

제목: {title}
본문: {short_content}
"""
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            score = 1
            reason = "평가 파싱 실패"
            
            for line in response_text.split("\n"):
                line = line.strip()
                if line.startswith("점수:"):
                    score_match = re.search(r'\d+', line)
                    if score_match:
                        score = int(score_match.group())
                elif line.startswith("이유:"):
                    reason = line.replace("이유:", "").strip()
            
            score = max(1, min(10, score))
            logger.info(f"📊 대중 흥미도 평가 - 점수: {score}점, 이유: {reason}")
            return {"score": score, "reason": reason}
            
        except Exception as e:
            logger.error(f"⚠️ 아이템 평가 중 에러 발생: {e}")
            return {"score": 8, "reason": f"평가 오류 기본값 ({str(e)})"}

    def _clean_content_headers(self, content: str) -> str:
        """본문 상단에 유입된 메타설명, 제목, 코드블록 등 잔여 헤더 완벽 제거"""
        if not content:
            return ""
            
        cleaned = content.strip()
        
        # 1. 마크다운 코드 블록 제거
        cleaned = re.sub(r"^```html\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        
        # 2. 본문 상단에 남아있는 '메타설명: ...', '제목: ...', '본문:' 패턴 완벽 제거
        patterns = [
            r"^\s*<div[^>]*class=['\"]meta-description['\"][^>]*>.*?</div>\s*",
            r"^\s*메타설명\s*:\s*[^\n]+\n*",
            r"^\s*메타\s*설명\s*:\s*[^\n]+\n*",
            r"^\s*제목\s*:\s*[^\n]+\n*",
            r"^\s*본문\s*:\s*\n*",
            r"^\s*태그\s*:\s*[^\n]+\n*"
        ]
        
        changed = True
        while changed:
            changed = False
            for pat in patterns:
                new_cleaned = re.sub(pat, "", cleaned, count=1, flags=re.IGNORECASE | re.DOTALL)
                if new_cleaned != cleaned:
                    cleaned = new_cleaned.strip()
                    changed = True
                    
        # 3. 만약 본문 중에 <article> 태그가 존재한다면 <article> 앞쪽 잔여물 과감히 절단
        article_pos = cleaned.find("<article")
        if article_pos > 0 and article_pos < 600:
            cleaned = cleaned[article_pos:]
            
        return cleaned.strip()

    def _post_process_html(self, content: str) -> str:
        """HTML 후처리: 반응형 표(Table) 가로 스크롤 래퍼 및 모바일 가독성 최적화"""
        if not content:
            return ""
            
        try:
            soup = BeautifulSoup(content, "html.parser")
            
            # 모든 <table> 태그를 반응형 가로 스크롤 컨테이너로 감싸기
            for table in soup.find_all("table"):
                parent = table.parent
                if parent and "overflow-x" in str(parent.get("style", "")):
                    continue
                    
                wrapper = soup.new_tag("div", style="overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; margin: 25px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);")
                table.wrap(wrapper)
                
                # 테이블 기본 모던 스타일 보강
                table_style = table.get("style", "")
                if "border-collapse" not in table_style:
                    table["style"] = f"width: 100%; border-collapse: collapse; min-width: 500px; font-size: 15px; {table_style}"
                    
            return str(soup)
        except Exception as e:
            logger.warning(f"HTML 후처리 파싱 경고 (원문 유지): {e}")
            return content

    def write_post(self, title: str, content: str, dept: str, url: str = None, images: list = None, recent_posts: list = None) -> dict:
        """Gemini API를 사용하여 고품질 포스팅 생성 및 원문 출처 링크 박스 부착"""
        logger.info(f"Gemini API 작성 시작: {title[:30]}...")
        prompt = self._create_prompt(title, content, dept, images, recent_posts)
        
        try:
            response = self.model.generate_content(prompt)
            post_data = self._parse_response(response.text)
            
            # 유저 요구사항: 본문 하단 원문 출처 링크 안내 박스 부착
            if post_data and post_data.get("content"):
                post_data["content"] = self._clean_content_headers(post_data["content"])
                post_data["content"] = self._post_process_html(post_data["content"])
                
                source_url = url or "https://www.korea.kr"
                dept_name = dept or "정부 보도자료"
                
                source_box = f"""
<div style="margin-top: 50px; padding: 24px; background-color: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <div style="display: flex; align-items: center; margin-bottom: 16px;">
    <span style="font-size: 24px; margin-right: 12px;">📢</span>
    <h4 style="margin: 0; font-size: 18px; color: #1e293b; font-weight: 700; word-break: keep-all;">공식 보도자료 및 상세 정보 안내</h4>
  </div>
  <p style="font-size: 15px; color: #475569; line-height: 1.6; margin: 0 0 20px 0; word-break: keep-all;">
    이 정보와 관련된 공식 원문 보도자료나 더 상세한 세부 지침이 필요하신 분들은 아래 공식 원문 링크를 통해 바로 확인하실 수 있습니다.
  </p>
  <div style="margin-bottom: 24px;">
    <a href="{source_url}" target="_blank" rel="noopener noreferrer" style="display: inline-block; padding: 12px 24px; background-color: #2563eb; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(37,99,235,0.2); transition: all 0.2s ease-in-out; text-align: center;">
      📄 공식 사이트 원문 보러가기 →
    </a>
  </div>
  <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 0 0 16px 0;"/>
  <div style="font-size: 13px; color: #64748b; line-height: 1.5;">
    <p style="margin: 0 0 6px 0;"><strong>제공 부처/기관:</strong> {dept_name}</p>
    <p style="margin: 0 0 6px 0;">※ 본 콘텐츠는 정부/지자체 공개 자료를 바탕으로 가공 및 분석하여 작성된 유용한 정책 정보입니다.</p>
    <p style="margin: 0;">※ 정보의 유효성은 발행일 기준이며 최신 변경 사항은 공식 출처를 참고해 주시기 바랍니다.</p>
  </div>
</div>
"""
                post_data["content"] += "\n" + source_box
                
            return post_data
        except Exception as e:
            logger.error(f"Gemini API 글 작성 중 오류 발생: {e}")
            if "quota" in str(e).lower() or "429" in str(e):
                return "QUOTA_EXHAUSTED"
            return None

    def _parse_response(self, text: str) -> dict:
        """Gemini 응답 파싱 (마크다운 볼드, 헤더 기호 완벽 대응 및 무결점 정제)"""
        meta_desc = ""
        title = ""
        content = ""
        tags = []

        if not text:
            return {
                "meta_description": "",
                "title": "2026년 정부·서울시 주요 생활 정책 안내",
                "content": "",
                "tags": ["정부지원금", "서울시복지", "생활꿀팁", "정책정보"]
            }

        # 0. 마크다운 볼드 및 기호 정리용 텍스트 준비
        # 1. 메타설명 추출 (**메타설명:**, [메타설명], 메타설명: 등 지원)
        meta_match = re.search(r"[\*#\[\s]*메타\s*설명[\*#\]\s*:\s*(.*?)(?=\n[\*#\[\s]*제목|\n[\*#\[\s]*본문|\n<article|\n#|$)", text, re.DOTALL | re.IGNORECASE)
        if meta_match:
            meta_desc = meta_match.group(1).strip()
            # 메타설명이 여러 줄로 넘어가지 않도록 첫 줄 취득 및 마크다운 기호 제거
            meta_desc = meta_desc.split("\n")[0].strip().strip('*#`"\'')

        # 2. 제목 추출 (**제목:**, [제목], 제목: 등 지원)
        title_match = re.search(r"[\*#\[\s]*제목[\*#\]\s*:\s*(.*?)(?=\n[\*#\[\s]*본문|\n<article|\n\n<|\n[\*#\[\s]*태그:|$)", text, re.DOTALL | re.IGNORECASE)
        if title_match:
            raw_title = title_match.group(1).strip()
            title = raw_title.split("\n")[0].strip()
        else:
            # '제목:' 헤더가 없는 경우 <article> 이전의 텍스트 줄 중 탐색
            article_pos = text.find("<article")
            header_text = text[:article_pos] if article_pos != -1 else text
            for line in header_text.split("\n"):
                line_str = line.strip().strip('*#`"\'')
                if line_str and not line_str.startswith("메타") and not line_str.startswith("태그") and not line_str.startswith("<") and not line_str.startswith("```"):
                    title = line_str
                    break

        # 제목 정제: HTML 태그, 마크다운 기호, 불필요한 접두어('태그:', '제목:' 등) 제거
        title = re.sub(r'^[\*#\[\s]*제목[\*#\]\s*:\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^[\*#\[\s]*태그[\*#\]\s*:\s*.*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'<[^>]+>', '', title).strip().strip('\'"#*`')
        title = re.sub(r'[\r\n\t]+', ' ', title).strip()

        # 3. 본문 추출 (<article> 태그 우선 감지)
        article_match = re.search(r"(<article.*?</article>)", text, re.DOTALL | re.IGNORECASE)
        if article_match:
            content = article_match.group(1).strip()
        else:
            content_match = re.search(r"[\*#\[\s]*본문[\*#\]\s*:\s*(.*?)(?=\n[\*#\[\s]*태그:|\n#|$)", text, re.DOTALL | re.IGNORECASE)
            if content_match:
                content = content_match.group(1).strip()
            elif "본문:" in text:
                parts = text.split("본문:", 1)
                content = parts[1].strip()
                if "\n태그:" in content:
                    content = content.split("\n태그:")[0].strip()

        # 4. 태그 추출 (**태그:**, [태그], 태그: 등 지원)
        tags_match = re.search(r"[\*#\[\s]*태그[\*#\]\s*:\s*(.*)", text, re.IGNORECASE)
        if tags_match:
            raw_tags = tags_match.group(1).strip()
            # 쉼표나 공백으로 분리
            raw_tags = raw_tags.replace(',', ' ')
            extracted_tags = [t.strip().lstrip('#*') for t in raw_tags.split() if t.strip()]
            filtered_tags = []
            for t in extracted_tags:
                t_clean = re.sub(r'<[^>]+>', '', t).strip()
                t_clean = re.sub(r'[^\w가-힣]', '', t_clean)
                if not re.match(r'^\d+년|\d+월|\d+일|^[A-Z]\d+$', t_clean):
                    if 2 <= len(t_clean) <= 15:
                        filtered_tags.append(t_clean)
            tags = filtered_tags[:5]

        # 5. 본문 정리
        if content:
            content = self._clean_content_headers(content)

        # 6. 스마트 Fallback (본문이 비었거나 극도로 짧을 때)
        if not content or len(content) < 500:
            logger.warning("파싱 실패 또는 본문 길이 부족, 스마트 폴백 가동")
            content = self._clean_content_headers(text)

        # 최종 기본값
        if not title:
            title = "2026년 정부·서울시 주요 생활 정책 안내"
        if not tags:
            tags = ["정부지원금", "서울시복지", "생활꿀팁", "정책정보"]

        return {
            "meta_description": meta_desc,
            "title": title,
            "content": content,
            "tags": tags
        }

