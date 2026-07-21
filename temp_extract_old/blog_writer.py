"""
Gemini API를 사용한 블로그 글 작성 모듈
원문을 블로그 포스트 형식으로 자동 변환합니다.
"""
import google.generativeai as genai
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BlogWriter:
    """Gemini API 기반 블로그 글 작성기"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        """
        Args:
            api_key: Gemini API 키
            model: 사용할 모델 (기본: gemini-pro)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        logger.info(f"BlogWriter 초기화 완료 (모델: {model})")
    
    def write_post(self, title: str, content: str, dept: str, url: str, images: list = None) -> Optional[Dict]:
        """
        블로그 글 작성 (재시도 로직 포함)
        """
        import time
        max_retries = 3
        retry_delay = 10 # 기본 대기 시간 (초)
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Gemini API 재시도 {attempt}/{max_retries-1}... ({retry_delay}초 대기)")
                    time.sleep(retry_delay)
                    retry_delay *= 2 # 지수 백오프
                
                logger.info(f"블로그 글 작성 시작: {title[:50]}...")
                
                # [FIX] 원본 HTML에서 모든 img 태그 제거 (AI의 오인 방지)
                import re
                clean_content = re.sub(r'<img[^>]*>', '', content, flags=re.IGNORECASE)
                
                prompt = self._create_prompt(title, clean_content, dept, images)
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    logger.error("Gemini API 응답이 비어있습니다")
                    return None
                
                # 응답 파싱
                result = self._parse_response(response.text, title, images)
                
                # [ADD] "자세한 내용은 여기를 눌러 원문을 볼수 있습니다" 문구와 저작권 추가
                copyright_footer = self._add_copyright(dept, url)
                result['blog_content'] += copyright_footer
                
                logger.info(f"블로그 글 작성 완료: {result['blog_title'][:30]}...")
                return result
            
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Resource exhausted" in error_msg:
                    logger.warning(f"⚠️ Gemini API 할당량 초과 (429): {error_msg}")
                    if attempt < max_retries - 1:
                        continue
                
                logger.error(f"블로그 글 작성 최종 오류: {error_msg}")
                return None
        return None
    
    def _create_prompt(self, title: str, content: str, dept: str, images: list = None) -> str:
        """Gemini에게 전달할 프롬프트 생성"""
        
        # 내용이 너무 길면 요약 (Gemini 토큰 제한 고려)
        max_content_length = 3500 # 좀 더 자세한 내용을 위해 늘림
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        # 이미지 정보 추가
        image_prompt = ""
        no_image_warning = "제공된 이미지 URL이 없으므로 본문에 <img> 태그를 절대로 포함하지 마세요."
        if images:
            image_prompt = "\n**이미지 활용 지침:**\n"
            for i, img_url in enumerate(images[:3], 1):
                image_prompt += f"- 이미지{i} URL: {img_url}\n"
            image_prompt += "위 이미지들을 본문의 적절한 위치에 <img src='이미지URL' style='max-width:100%; height:auto; margin-bottom:20px;'> 태그를 사용하여 삽입하세요.\n"
            no_image_warning = "위의 제공된 이미지 URL들만 사용하여 본문의 적절한 위치에 삽입하세요. 제공되지 않은 가상의 이미지 URL은 절대 사용하지 마세요."

        prompt = f"""
당신은 대한민국 정부 정책 및 지자체 소식을 전문으로 전달하는 에디터입니다. 
당신의 목표는 아래 제공된 보도자료를 바탕으로 **구글 검색 결과 상단에 노출될 수 있는(SEO 최적화)** 고품질 블로그 포스트를 작성하는 것입니다.

**SEO 및 본문 작성 가이드**
- **검색 최적화 제목**: 제목에 핵심 키워드(예: '~신청방법', '~대상', '2026년', '지원금' 등)를 포함하여 클릭을 유도하고 검색에 잘 걸리도록 작성하세요.
- **핵심 정보 중심**: 사용자가 궁금해하는 '누가(대상)', '언제(일정)', '어떻게(방법)'를 가장 명확하고 상세하게 서술하세요. (내용 생략 금지)
- **리치 콘텐츠 활용**: 제공된 원문의 **표(table)와 이미지(img)**를 최대한 활용하세요.{image_prompt}
- **가독성 최우선**: 소제목(h3)과 불렛 포인트를 사용하여 정보의 구조를 명확히 하세요.

**원문 정보**
- 부처/기관: {dept}
- 원문 제목: {title}
- 내용:
{content}

**작성 요구사항**
1. 블로그 제목 (SEO 최적화)
   - 원문 제목의 핵심을 유지하되, 사람들이 많이 검색할 법한 키워드를 추가하여 매력적으로 구성 (예: [원문제목] - 신청방법, 지원대상, 혜택 총정리)

2. 블로그 본문 (HTML 형식, 모바일 최적화)
   - 전체를 <div style="font-size: 19px; line-height: 1.9; word-break: keep-all;">로 감싸기
   - **서론**: 정책이 나온 배경과 독자에게 주는 실제 혜택 강조 (2-3문단)
   - **본론**: 
     - 상세 지원 내용, 대상, 신청 방법 등을 섹션별로 구분 (h3 사용)
     - 원문의 표와 이미지를 적재적소에 배치 (제공된 이미지 URL 활용)
     - {no_image_warning}
     - 표 스타일 추천: <table border="1" style="width:100%; border-collapse:collapse; margin-bottom:22px;">
   - **결론**: 향후 일정이나 기대 효과, 독자를 향한 응원 메시지 (1-2문단)

3. 해시태그: 검색량이 높은 관련 키워드 5개 (#키워드 형식)

**주의사항: 출력 시 ```html 또는 '''html 같은 마크다운 코드 블록 태그를 절대로 사용하지 마세요. 오직 순수 텍스트와 HTML 본문만 출력하세요.**

**출력 형식 (반드시 엄수)**
제목: [생성된 SEO 최적화 제목]

본문:
[HTML 형식 블로그 본문]

태그: #태그1 #태그2 #태그3 #태그4 #태그5
"""
        return prompt
    
    def _parse_response(self, response_text: str, original_title: str, images: list = None) -> Dict:
        """Gemini 응답 파싱"""
        
        lines = response_text.strip().split("\n")
        
        blog_title = original_title  # 기본값
        blog_content = ""
        tags = []
        
        current_section = None
        content_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("제목:"):
                blog_title = line.replace("제목:", "").strip()
                current_section = None
            elif line.startswith("본문:"):
                current_section = "content"
            elif line.startswith("태그:"):
                tags_text = line.replace("태그:", "").strip()
                tags = [tag.strip() for tag in tags_text.split("#") if tag.strip()]
                current_section = None
            elif current_section == "content":
                content_lines.append(line)
        
        blog_content = "\n".join(content_lines).strip()
        
        # [FIX] 마크다운 코드 블록 제거 (더욱 견고한 로직)
        import re
        # 1. ```html 또는 '''html 등 시작/끝 태그 제거
        blog_content = re.sub(r"^(?:```|''')(?:html|HTML)?\s*", "", blog_content, flags=re.MULTILINE)
        blog_content = re.sub(r"\s*(?:```|''')$", "", blog_content, flags=re.MULTILINE)
        
        # 2. 본문 중간이나 줄 처음에 남은 잔재들 제거
        blog_content = re.sub(r"```(?:html|HTML)?", "", blog_content, flags=re.IGNORECASE)
        blog_content = re.sub(r"'''(?:html|HTML)?", "", blog_content, flags=re.IGNORECASE)
        
        blog_content = blog_content.strip()
        
        # HTML 태그가 없으면 기본 포맷팅 적용
        if "<" not in blog_content:
            blog_content = f"<p>{blog_content.replace(chr(10), '</p><p>')}</p>"
        
        # [FIX] 이미지가 없을 경우 생성된 본문에서 img 태그 강제 제거 (환각 방지)
        if not images and "<img" in blog_content:
            import re
            blog_content = re.sub(r'<img[^>]*>', '', blog_content, flags=re.IGNORECASE)

        return {
            "blog_title": blog_title,
            "blog_content": blog_content,
            "tags": tags[:5]  # 최대 5개
        }
    
    def _add_copyright(self, dept: str, url: str) -> str:
        """
        저작권 및 원문 링크 HTML 생성
        """
        copyright_html = f"""
<div style="margin-top: 40px; padding: 20px; background-color: #f1f8ff; border-radius: 10px; border: 1px solid #c8e1ff;">
    <p style="font-size: 18px; margin-bottom: 15px; font-weight: bold;">
        💡 좀 더 자세한 내용은 <a href="{url}" target="_blank" style="color: #0366d6; text-decoration: underline;">"여기"</a>를 눌러 원문을 볼 수 있습니다.
    </p>
    <hr style="border: 0; border-top: 1px solid #c8e1ff; margin-bottom: 15px;">
    <div style="font-size: 14px; color: #586069;">
        <p style="margin-bottom: 5px;"><strong>출처 정보:</strong> {dept} 보도자료</p>
        <p style="margin-bottom: 5px;">본 글은 정부 공개 자료를 기반으로 AI가 재구성한 콘텐츠입니다.</p>
        <p style="margin-bottom: 0;">저작권은 원 저작권자에게 있으며, 상업적 이용 시 출처를 명시해주세요.</p>
    </div>
</div>
"""
        return copyright_html
