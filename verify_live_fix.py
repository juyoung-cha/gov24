from content_scraper import ContentScraper
from blog_writer import BlogWriter
import json

def test_live():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    api_key = config['gemini']['api_key']
    model_name = config['gemini']['model']
    scraper = ContentScraper()
    writer = BlogWriter(api_key=api_key, model=model_name)
    
    # 서울시 정책 뉴스 (사용자가 언급한 다른 소스)
    url = "https://mediahub.seoul.go.kr/news/newsView.do?articleId=2010834"
    
    print(f"Testing URL: {url}")
    scraped = scraper.scrape(url)
    
    if scraped:
        print(f"\n[Scraped Data]")
        # scrape()는 content와 images만 반환하므로 title은 테스트용으로 지정
        sample_title = "우리 지역 수소도시, 어떻게 만들어갈까? (테스트)"
        print(f"Title: {sample_title}")
        print(f"Images found: {scraped['images']}")
        
        # 블로그 글 생성
        blog_post = writer.write_post(
            title=sample_title,
            content=scraped['content'],
            dept="대한민국 정책브리핑",
            url=url,
            images=scraped['images']
        )
        
        if blog_post:
            print("\n[Generated Blog Post - Title]")
            print(blog_post['blog_title'])
            
            print("\n[Generated Blog Post - Content Snippet (Check for HTML tags/imgs)]")
            content = blog_post['blog_content']
            print(content[:500])
            
            # 검증
            if "```html" in content or "'''html" in content:
                print("\n❌ FAIL: Raw HTML tags still present!")
            else:
                print("\n✅ SUCCESS: No raw HTML tags found.")
                
            if not scraped['images'] and "<img" in content:
                print("❌ FAIL: Image tag found when no images were provided!")
            elif scraped['images'] and "<img" in content:
                print("✅ SUCCESS: Images correctly included.")
            elif not scraped['images'] and "<img" not in content:
                print("✅ SUCCESS: No image tags present (as expected).")
        else:
            print("Blog generation failed.")
    else:
        print("Scraping failed.")

if __name__ == "__main__":
    test_live()
