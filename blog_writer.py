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
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def _create_prompt(self, title: str, content: str, dept: str, images: list = None, recent_posts: list = None) -> str:
        """Gemini에게 전달할 프롬프트 생성 (5월 인기 공감 스토리텔링 템플릿 강조)"""
        
        max_content_length = 6000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        image_prompt = "원문에 이미지가 없으므로, 텍스트와 표(table)만으로 정보를 완벽하게 시각화하세요."
        if images:
            image_prompt = "\n**이미지 활용 지침:**\n"
            for i, img_url in enumerate(images[:3], 1):
                image_prompt += f"- 이미지{i} URL: {img_url}\n"
            image_prompt += "위 이미지들을 본문의 흐름에 맞춰 <img src='이미지URL' style='max-width:100%; height:auto; margin:25px 0; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'> 태그로 삽입하세요.\n"

        internal_link_prompt = ""
        if recent_posts:
            internal_link_prompt = "\n**내부 링크 삽입 지침:**\n아래 최근 글 중 이번 주제와 연관된 글이 있다면, 본문 중간에 자연스럽게 삽입하세요.\n"
            for rp in recent_posts[:5]:
                internal_link_prompt += f"- [{rp['title']}]({rp['url']})\n"
            internal_link_prompt += "형식: <p style='background:#f9f9f9; padding:15px; border-left:5px solid #007bff;'><a href='URL' style='text-decoration:none; color:#333; font-weight:bold;'>📌 {rp['title']} 바로가기</a></p>\n"

        prompt = f"""
당신은 대한민국 최고의 정책 분석가이자, 20년 경력의 베테랑 IT/생활 칼럼니스트입니다.
독자의 마음을 읽고 깊은 공감과 실질적인 생활 혜택을 주는 독창적인 고품질 콘텐츠를 작성해야 합니다.

[페르소나 및 톤앤매너 - 5월 베스트 스타일]
- 페르소나: 50대 중반의 지혜롭고 친근한 20년 차 칼럼니스트. 독자를 아끼는 따뜻한 '~입니다' 체 사용.
- 공감 서두: 독자의 현실적인 일상 고민("요즘 물가 상승으로 장보기가 무섭죠?", "주말 나들이 장소 고민 많으셨죠?", "대중교통비/생활비 절약 비법이 궁금하신가요?")으로 매력적으로 시작하세요.
- 제목 지침 (중요): 훈계조(예: "아직도 빨리빨리 외치시나요?")나 딱딱한 행정 공고 제목은 절대 금지합니다. 독자가 보자마자 클릭하고 싶은 실용 혜택/생활 꿀팁 중심 질문형 제목으로 만드세요. (예: '모르면 나만 손해! ~ 혜택 총정리', '월 5만원 절약하는 숨은 비법 대공개')

[필수 구성 요소]
1. [따뜻한 인사 및 공감 서두]: 일상 에피소드와 팩트 위주의 3줄 요약.
2. [실생활 Q&A 꿀팁]: 독자가 가장 궁금해할 질문 3개 이상을 <h3> 및 <blockquote> 인사이트 태그를 활용해 전문적으로 풀어내기.
3. [자격 요건 및 혜택 표]: 표(table)를 활용해 한눈에 정리.
4. [놓치면 후회할 팁]: 담당자도 안 알려주는 신청 성공률 높이는 비법.
5. [마무리]: 독자들의 삶을 응원하는 따뜻한 메시지.

SEO 가이드:
- 분량: 반드시 3,000자 이상의 장문을 작성하세요. (정보의 깊이가 승인의 핵심입니다.)
- HTML 규칙: ```html 과 같은 코드 블록으로 본문을 감싸지 마세요. 순수 HTML 시맨틱 태그(article, section, blockquote, table)만 사용하세요.

{image_prompt}
{internal_link_prompt}

원문 정보:
- 출처: {dept}
- 원제: {title}
- 내용: {content}

출력 형식 (반드시 엄수):
메타설명: [150자 이내의 검색 유도 요약]

제목: [SEO 최적화된 매력적이고 공감 가는 제목]

본문:
[순수 HTML 형식 블로그 본문 (코드 블록 절대 사용 금지) - 3000자 이상 풍부한 분량, 이모지 활용, 구조화된 레이아웃]

태그: #태그1 #태그2 #태그3 #태그4 #태그5
"""
        return prompt

    def evaluate_item_relevance(self, title: str, content: str) -> dict:
        """수집된 기사가 일반 독자에게 흥미롭고 실생활에 직접 밀착된 혜택/소식인지 평가"""
        logger.info(f"아이템 대중 흥미도 및 유용성 평가 시작: {title[:40]}...")
        
        short_content = content[:1500] if len(content) > 1500 else content
        
        prompt = f"""
당신은 대중이 정말로 읽고 싶어 하는 흥미로운 이슈와 생활 혜택을 선별하는 베테랑 뉴스 에디터입니다.
다음 소식이 일반 시민(직장인, 청년, 주부, 소상공인 등)이 직접 혜택을 받거나 클릭하고 싶어 하는 흥미로운 생활 밀착형 정보인지 1~10점으로 평가해 주세요.

[❌ 절대 탈락 및 감점 대상 (1~4점 수준)]
- 선거 현수막 작업 안전, 건설 현장 안전 수칙, 특정 산업 안전 지침 등 일반 시민과 무관한 작업장 안전 공고
- 부처/지자체의 단순 해명자료, 설명자료, 내부 동정 (인사, 훈장 수여, 위원회 개최 등)
- 일반 시민이 이용할 수 없는 전문 기업/학술 고시, 행정 편의적 지침, 통계 조사 방식 변경 등
- 클릭하고 싶은 생각이 전혀 들지 않는 관료적이고 재미없는 행정 공고

[✅ 적극 선택 및 가점 대상 (8~10점 수준)]
- 지원금, 환급금, 보조금, 교통비 절약(K-패스, 기후동행카드 등) 직접적인 돈이 되는 혜택
- 가성비 주말 나들이, 무료 전시/축제, 휴가철 피서지, 맛집/문화 소식
- 청년 전세/임차보증금 지원, 주택/부동산 실생활 꿀팁, 노후 자산 관리
- 일상생활에서 바로 활용할 수 있는 건강, 생활 상식, 복지 서비스

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
            return {"score": 7, "reason": f"평가 오류 기본값 ({str(e)})"}

    def write_post(self, title: str, content: str, dept: str, url: str = None, images: list = None, recent_posts: list = None) -> dict:
        """Gemini API를 사용하여 고품질 포스팅 생성 및 원문 출처 링크 박스 부착"""
        logger.info(f"Gemini API 작성 시작: {title[:30]}...")
        prompt = self._create_prompt(title, content, dept, images, recent_posts)
        
        try:
            response = self.model.generate_content(prompt)
            post_data = self._parse_response(response.text)
            
            # 유저 요구사항: 본문 하단 원문 출처 링크 안내 박스 부착
            if post_data and post_data.get("content"):
                source_url = url or "https://www.korea.kr"
                dept_name = dept or "정부 보도자료"
                
                source_box = f"""
<div style="margin-top: 40px; padding: 20px; background-color: #f1f8ff; border-radius: 10px; border: 1px solid #c8e1ff;">
  <p style="font-size: 18px; margin-bottom: 15px; font-weight: bold;">
    💡 좀 더 자세한 내용은 <a href="{source_url}" style="color: #0366d6; text-decoration: underline;" target="_blank">"여기"</a>를 눌러 원문을 볼 수 있습니다.
  </p>
  <hr style="border: 0; border-top: 1px solid #c8e1ff; margin-bottom: 15px;"/>
  <div style="font-size: 14px; color: #586069;">
    <p style="margin-bottom: 5px;"><strong>출처 정보:</strong> {dept_name}</p>
    <p style="margin-bottom: 5px;">본 글은 정부 공개 자료를 바탕으로 재구성 및 분석한 글입니다.</p>
    <p style="margin-bottom: 0;">저작권은 원 저작권자에게 있으며, 상업적 이용 시 출처를 명시해주세요.</p>
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
        """Gemini 응답 파싱 (스마트 정규식 및 폴백 메커니즘 적용)"""
        meta_desc = ""
        title = ""
        content = ""
        tags = []

        meta_match = re.search(r"메타설명:\s*(.*?)(?=\n|제목:|$)", text, re.DOTALL)
        if meta_match:
            meta_desc = meta_match.group(1).strip()

        title_match = re.search(r"제목:\s*(.*?)(?=\n|본문:|$)", text, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()

        content_match = re.search(r"본문:\s*(.*?)(?=\n태그:|$)", text, re.DOTALL)
        if content_match:
            content = content_match.group(1).strip()
        else:
            if "본문:" in text:
                parts = text.split("본문:", 1)
                content = parts[1].strip()
                if "\n태그:" in content:
                    content = content.split("\n태그:")[0].strip()

        tags_match = re.search(r"태그:\s*(.*)", text)
        if tags_match:
            raw_tags = tags_match.group(1).strip()
            tags = [t.strip().lstrip('#') for t in raw_tags.split() if t.strip()]

        if content:
            content = re.sub(r"^```html\s*", "", content, flags=re.IGNORECASE)
            content = re.sub(r"^```\s*", "", content)
            content = re.sub(r"\s*```$", "", content)

        if not content or len(content) < 500:
            logger.warning("파싱 실패 또는 본문 길이 부족, 스마트 폴백 가동")
            content = text
            if meta_desc:
                content = f"<div class='meta-description' style='display:none;'>{meta_desc}</div>\n" + content

        return {
            "meta_description": meta_desc,
            "title": title or "정부/서울시 주요 정책 안내",
            "content": content,
            "tags": tags or ["정부정책", "서울시소식", "정책정보"]
        }
