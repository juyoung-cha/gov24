import json
import os
import logging
from blogger_poster import BloggerPoster

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def create_mandatory_pages():
    try:
        if not os.path.exists("config.json"):
            logger.error("config.json 파일이 없습니다.")
            return

        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        blog_id = config.get("blogger", {}).get("blog_id")
        poster = BloggerPoster(blog_id=blog_id)

        pages_to_create = [
            {
                "title": "블로그 소개",
                "content": """
                <p>대한민국의 모든 정책 정보와 지자체의 혜택을 가장 빠르고 정확하게 전달하는 '대한민국 정책 매거진 24'입니다.</p>
                <p>저희 블로그는 기획재정부, 보건복지부, 국토교통부, 고용노동부 등 국가 주요 부처와 서울특별시를 비롯한 지자체의 공신력 있는 공식 보도자료를 기반으로 합니다. 복잡한 정책 용어를 쉽게 풀이하고, 시민들에게 실질적으로 도움이 되는 지원금, 복지 서비스, 제도 변화 소식을 매일 업데이트하고 있습니다.</p>
                <p>누구도 정책 혜택에서 소외되지 않는 세상을 위해, 신뢰할 수 있는 정보를 제공하는 든든한 가이드가 되겠습니다.</p>
                """
            },
            {
                "title": "개인정보처리방침",
                "content": """
                <p>대한민국 정책 매거진 24(이하 '블로그')는 사용자의 개인정보를 소중히 여기며, 구글 애드센스 등 광고 서비스 제공을 위해 다음과 같은 정책을 시행합니다.</p>
                <ol>
                    <li><strong>데이터 수집</strong>: 블로그는 직접적인 개인정보(이름, 이메일 등)를 수집하지 않습니다. 다만, 방문자의 편의와 광고 제공을 위해 쿠키(Cookie)를 사용할 수 있습니다.</li>
                    <li><strong>쿠키 사용</strong>: 구글 등 제3자 제공업체는 쿠키를 사용하여 사용자의 이전 방문 기록을 바탕으로 광고를 게재합니다.</li>
                    <li><strong>거부 방법</strong>: 사용자는 브라우저 설정에서 쿠키 사용을 허용하거나 거부할 수 있습니다. 또한, 구글 광고 설정(<a href="https://adssettings.google.com">https://adssettings.google.com</a>)에서 맞춤형 광고를 해제할 수 있습니다.</li>
                    <li><strong>문의</strong>: 개인정보 관련 문의는 블로그의 '문의하기' 페이지를 이용해 주시기 바랍니다.</li>
                </ol>
                """
            },
            {
                "title": "문의하기",
                "content": """
                <p>블로그의 콘텐츠나 제안, 기타 문의 사항이 있으시면 아래 채널을 통해 연락 주시기 바랍니다.</p>
                <ul>
                    <li><strong>이메일</strong>: friends1928374651@gmail.com</li>
                    <li><strong>소통 시간</strong>: 월~금 (09:00 ~ 18:00)</li>
                </ul>
                <p>보내주신 의견은 확인 후 신속하게 답변드리도록 하겠습니다. 대한민국 정책 매거진 24를 이용해 주셔서 감사합니다.</p>
                """
            }
        ]

        logger.info("필수 고정 페이지 생성을 시작합니다...")
        for page in pages_to_create:
            url = poster.create_page(title=page["title"], content=page["content"])
            if url:
                print(f"✅ 생성 완료: {page['title']} -> {url}")
            else:
                print(f"❌ 생성 실패: {page['title']}")

    except Exception as e:
        logger.error(f"페이지 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    create_mandatory_pages()
