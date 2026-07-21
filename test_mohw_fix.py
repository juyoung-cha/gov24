from content_scraper import ContentScraper
from blog_writer import BlogWriter
import json

# config에서 API 키 가져오기
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

scraper = ContentScraper()
writer = BlogWriter(config["gemini"]["api_key"], config["gemini"]["model"])

# 보건복지부 샘플 URL (사용자가 이미지가 안 보인다고 한 글)
test_url = "https://www.mohw.go.kr/board.es?mid=a10501010000&bid=0003&list_no=1488794&act=view"

scraped = scraper.scrape(test_url)
if scraped:
    print(f"Scraped images: {scraped.get('images')}")
    print(f"Content length: {len(scraped['content'])}")
    
    # 본문에 이미지가 있는지 확인
    if "<img" in scraped['content']:
        print("✅ SUCCESS: Content HTML includes images.")
    else:
        print("❌ ISSUE: Content HTML does not include images.")

    blog_post = writer.write_post(
        title="[테스트] 첨단재생의료실시기관 지정 현황",
        content=scraped["content"],
        dept="보건복지부",
        url=test_url,
        images=scraped.get("images")
    )
    
    if blog_post:
        print("\n--- Blog Content Snippet ---")
        print(blog_post["blog_content"][:500])
        
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
