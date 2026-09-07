"""
중복 정적 페이지 정리 및 최신화 스크립트
'블로그 소개', '개인정보처리방침', '문의하기' 3종 페이지만 1세트 유지하고 중복 페이지를 삭제/정리합니다.
"""
import time
import logging
from blogger_poster import BloggerPoster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

PAGES_CONTENT = {
    "블로그 소개": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; font-size: 16px; line-height: 1.8; color: #2d3748; padding: 20px 0;">
    <h2 style="color: #1e293b; border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px;">대한민국 정책 매거진 24 소개</h2>
    <p>대한민국의 모든 정책 정보와 지자체의 혜택을 가장 빠르고 정확하게 전달하는 <strong>'대한민국 정책 매거진 24'</strong>입니다.</p>
    <p>저희 블로그는 기획재정부, 보건복지부, 국토교통부, 고용노동부 등 국가 주요 부처와 서울특별시를 비롯한 지자체의 공신력 있는 공식 보도자료를 기반으로 합니다. 복잡하고 어려운 행정 용어를 알기 쉽게 풀이하고, 시민들에게 실질적으로 도움이 되는 지원금, 복지 서비스, 제도 변화 소식을 매일 업데이트하고 있습니다.</p>
    <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 18px 24px; margin: 25px 0; border-radius: 6px;">
        <h3 style="margin-top: 0; color: #1e40af;">📌 블로그 운영 가치 및 원칙</h3>
        <ul style="margin-bottom: 0; padding-left: 20px;">
            <li><strong>신속·정확성:</strong> 정부 및 공공기관의 공식 발표 자료만을 철저히 검증하여 전달합니다.</li>
            <li><strong>생활 밀착형 정보:</strong> 시민들이 실제로 체감할 수 있는 지원금, 환급금, 주거/복지 혜택을 중점적으로 분석합니다.</li>
            <li><strong>쉬운 해설:</strong> 어려운 정책 가이드라인을 누구나 쉽게 이해하고 바로 신청할 수 있도록 1인칭 가이드와 Q&A로 정리합니다.</li>
        </ul>
    </div>
    <p>누구도 정책 혜택에서 소외되지 않는 세상을 위해, 신뢰할 수 있는 정보를 제공하는 든든한 길잡이가 되겠습니다.</p>
</div>
""",
    "개인정보처리방침": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; font-size: 16px; line-height: 1.8; color: #2d3748; padding: 20px 0;">
    <h2 style="color: #1e293b; border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px;">개인정보처리방침 (Privacy Policy)</h2>
    <p>대한민국 정책 매거진 24(이하 '블로그')는 이용자의 개인정보를 소중하게 생각하며, 개인정보보호법 및 관련 법령을 준수합니다. 본 방침은 구글 애드센스 등 광고 서비스 제공 및 블로그 이용과 관련하여 시행됩니다.</p>
    
    <h3 style="color: #1e293b; margin-top: 25px;">1. 수집하는 개인정보 항목</h3>
    <p>블로그는 회원가입 절차 없이 자유롭게 열람할 수 있으며, 직접적인 개인 식별 정보(성명, 주민등록번호, 전화번호 등)를 수집하거나 저장하지 않습니다.</p>

    <h3 style="color: #1e293b; margin-top: 25px;">2. 쿠키(Cookie) 및 광고 게재 정책</h3>
    <p>블로그는 방문자의 웹사이트 이용 환경 개선 및 맞춤형 광고 게재를 위해 쿠키(Cookie) 정보를 사용할 수 있습니다.</p>
    <ul>
        <li>구글을 포함한 제3자 제공업체는 쿠키를 사용하여 사용자의 이전 웹사이트 방문 기록을 바탕으로 광고를 게재합니다.</li>
        <li>사용자는 웹 브라우저 설정을 통해 쿠키 저장을 거부하거나 삭제할 수 있습니다.</li>
        <li>맞춤형 광고 설정을 원치 않으실 경우, <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer" style="color: #2563eb;">Google 광고 설정</a>에서 맞춤 광고를 해제하실 수 있습니다.</li>
    </ul>

    <h3 style="color: #1e293b; margin-top: 25px;">3. 개인정보 관련 문의</h3>
    <p>개인정보 처리 및 블로그 정책에 관한 문의 사항은 언제든지 '문의하기' 페이지 또는 공식 이메일(friends1928374651@gmail.com)을 통해 문의해 주시기 바랍니다.</p>
    <p style="color: #64748b; font-size: 14px; margin-top: 30px;">시행일자: 2026년 3월 1일 (최종 개정: 2026년 9월 3일)</p>
</div>
""",
    "문의하기": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; font-size: 16px; line-height: 1.8; color: #2d3748; padding: 20px 0;">
    <h2 style="color: #1e293b; border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px;">문의하기 (Contact Us)</h2>
    <p>대한민국 정책 매거진 24에 방문해 주셔서 진심으로 감사드립니다.</p>
    <p>블로그의 정책 콘텐츠 내용에 대한 의견, 제휴 제안, 수정 요청 또는 기타 궁금하신 점이 있으시면 아래 공식 채널을 통해 언제든지 편하게 문의해 주시기 바랍니다.</p>
    
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin: 30px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="margin-top: 0; color: #1e293b; font-size: 18px;">📬 공식 소통 창구</h3>
        <ul style="list-style: none; padding-left: 0; margin-bottom: 0; line-height: 2;">
            <li>✉️ <strong>공식 이메일:</strong> <a href="mailto:friends1928374651@gmail.com" style="color: #2563eb; font-weight: bold;">friends1928374651@gmail.com</a></li>
            <li>⏰ <strong>운영 시간:</strong> 월요일 ~ 금요일 (09:00 ~ 18:00 KST)</li>
            <li>💬 <strong>응답 안내:</strong> 보내주신 소중한 의견은 확인 후 24~48시간 이내에 정성껏 답변드리겠습니다.</li>
        </ul>
    </div>
    <p>독자 여러분의 따뜻한 관심과 소중한 제안은 더 유익하고 공신력 있는 매거진을 만드는 데 큰 힘이 됩니다. 감사합니다.</p>
</div>
"""
}

def clean_pages():
    logger.info("=" * 60)
    logger.info("Blogger 중복 정적 페이지 정리 및 최신화 시작")
    logger.info("=" * 60)
    
    poster = BloggerPoster()
    pages = poster.list_pages()
    logger.info(f"현재 등록된 페이지 수: {len(pages)}개")
    
    # 제목별로 그룹화
    grouped = {}
    for p in pages:
        title = p.get("title", "").strip()
        grouped.setdefault(title, []).append(p)
        
    for title, target_content in PAGES_CONTENT.items():
        matched = grouped.get(title, [])
        logger.info(f"\n[{title}] 페이지 처리 (발견된 수: {len(matched)}개)")
        
        if not matched:
            # 아예 없으면 신규 생성
            url = poster.create_page(title=title, content=target_content, is_draft=False)
            logger.info(f"  ✨ 신규 생성 완료: {url}")
            time.sleep(2)
        else:
            # 가장 첫 번째(또는 최신) 페이지만 유지하고 본문 업데이트, 나머지는 삭제
            keep_page = matched[0]
            page_id = keep_page.get("id")
            poster.update_page(page_id=page_id, title=title, content=target_content)
            logger.info(f"  ✅ 대표 페이지 유지 및 내용 최신화 (ID: {page_id}, URL: {keep_page.get('url')})")
            time.sleep(1.5)
            
            # 나머지 중복 페이지 삭제
            for dup_page in matched[1:]:
                dup_id = dup_page.get("id")
                poster.delete_page(dup_id)
                logger.info(f"  🗑️ 중복 페이지 삭제 완료 (ID: {dup_id})")
                time.sleep(1.5)
                
    # PAGES_CONTENT에 없는 기타 불필요한 테스트 페이지가 있다면 확인
    for title, plist in grouped.items():
        if title not in PAGES_CONTENT:
            logger.info(f"\n기타 페이지 발견: '{title}' ({len(plist)}개)")
            
    logger.info("=" * 60)
    logger.info("정적 페이지 정리 완료!")
    logger.info("=" * 60)

if __name__ == "__main__":
    clean_pages()
