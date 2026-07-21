from content_scraper import ContentScraper
from blog_writer import BlogWriter
import json

# config에서 API 키 가져오기
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

scraper = ContentScraper()
writer = BlogWriter(config["gemini"]["api_key"], config["gemini"]["model"])

# korea.kr 샘플 URL (최근 글 중 하나)
test_url = "https://www.korea.kr/news/pressReleaseView.do?newsId=156703355&call_from=rsslink"

scraped = scraper.scrape(test_url)
if scraped:
    print(f"Scraped images: {scraped.get('images')}")
    print(f"Content length: {len(scraped['content'])}")
    
    blog_post = writer.write_post(
        title="[테스트] 수소도시 건설 지원",
        content=scraped["content"],
        dept="기획재정부",
        url=test_url,
        images=scraped.get("images")
    )
    
    if blog_post:
        print("\n--- Blog Title ---")
        print(blog_post["blog_title"])
        print("\n--- Blog Content Snippet ---")
        print(blog_post["blog_content"][:500])
        print("\n--- Tags ---")
        print(blog_post["tags"])
        
        # 'html' 태그가 본문에 남아있는지 체크
        if "'''html" in blog_post["blog_content"] or "```html" in blog_post["blog_content"]:
            print("\n❌ ISSUE: Raw HTML tags still present!")
        else:
            print("\n✅ SUCCESS: No raw HTML tags found.")
        
        # 이미지 태그가 포함되어 있는지 체크
        if "<img" in blog_post["blog_content"]:
            print("✅ SUCCESS: Content includes images.")
        else:
            print("❌ ISSUE: No images found in blog content.")
else:
    print("Failed to scrape.")
