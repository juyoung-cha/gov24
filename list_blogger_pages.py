from blogger_poster import BloggerPoster
import json

def list_pages():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    poster = BloggerPoster(blog_id=config['blogger']['blog_id'])
    
    # Blogger API v3 pages().list() 호출
    result = poster.service.pages().list(blogId=poster.blog_id).execute()
    pages = result.get('items', [])
    
    print(f"총 {len(pages)}개의 페이지를 발견했습니다:")
    for i, page in enumerate(pages):
        print(f"[{i+1}] 제목: {page['title']}")
        print(f"    URL: {page['url']}")
        print(f"    ID: {page['id']}")
        print("-" * 20)

if __name__ == "__main__":
    list_pages()
