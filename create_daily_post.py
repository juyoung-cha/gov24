import json
import logging
import os
from dotenv import load_dotenv
from content_scraper import ContentScraper
from blog_writer import BlogWriter
from blogger_poster import BloggerPoster

logging.basicConfig(level=logging.INFO)

def main():
    # .env 파일에서 환경변수 로드
    load_dotenv()
    
    # 1. 설정 로드
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    gemini_api_key = os.getenv("GEMINI_API_KEY") or config["gemini"].get("api_key")
    if not gemini_api_key:
        print("GEMINI_API_KEY가 설정되지 않았습니다.")
        return
        
    url = "https://mediahub.seoul.go.kr/archives/2017859"
    dept = "서울시 정책뉴스"
    
    # 2. 크롤링
    scraper = ContentScraper()
    scraped_data = scraper.scrape(url)
    
    if not scraped_data:
        print("크롤링 실패")
        return

    # 3. 블로그 글 작성 (AI)
    writer = BlogWriter(api_key=gemini_api_key, model=config["gemini"]["model"])
    
    # 최근 포스트 로드 (내부 링크용)
    poster = BloggerPoster()
    recent_posts = poster.list_posts(max_results=5)
    
    print("\n[단계 1] AI 블로그 글 생성 중...")
    result = writer.write_post(
        title="직장 내 고민, 퇴근길 지하철역 '찾아가는 노동상담'에서 털어놨더니…",
        content=scraped_data["content"],
        dept=dept,
        url=url,
        images=scraped_data["images"],
        recent_posts=recent_posts
    )

    if not result or result == 'QUOTA_EXHAUSTED':
        print("AI 글 작성 실패")
        return

    print("\n" + "="*80)
    print("AI 생성 블로그 글 초안 (검수용)")
    print("="*80)
    print(f"제목: {result['blog_title']}")
    print(f"메타설명: {result['meta_description']}")
    print(f"태그: {', '.join(result['tags'])}")
    print("-" * 40)
    # 본문 앞부분만 출력
    print(result['blog_content'][:500] + "...")
    print("="*80 + "\n")

    # 4. 포스팅 (Blogger)
    print("[단계 2] Blogger 포스팅 진행...")
    post_url = poster.post(
        title=result["blog_title"],
        content=result["blog_content"],
        labels=result["tags"] + ["1. 서울시 정책 뉴스"],
        meta_description=result["meta_description"],
        dept=dept
    )

    if post_url:
        print(f"✅ 포스팅 성공: {post_url}")
        
        # seen.json에 추가
        try:
            with open("seen.json", "r", encoding="utf-8") as f:
                seen = json.load(f)
            if url not in seen:
                seen.append(url)
                with open("seen.json", "w", encoding="utf-8") as f:
                    json.dump(seen, f, indent=2)
        except:
            pass
    else:
        print("❌ 포스팅 실패")

if __name__ == "__main__":
    main()
