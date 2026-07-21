import json
from blogger_poster import BloggerPoster

def check_status():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    blogger_id = config['blogger']['blog_id']
    poster = BloggerPoster(blog_id=blogger_id)
    
    # max 500
    try:
        req = poster.service.posts().list(blogId=blogger_id, maxResults=500, status='LIVE')
        res = req.execute()
        live_posts = res.get('items', [])
        print(f"공개(LIVE) 상태 게시물 수: {len(live_posts)}개")
        for i, p in enumerate(live_posts[:10]):
            print(f" - [LIVE] {p.get('title')[:30]} ({p.get('published')[:10]})")
            
        req2 = poster.service.posts().list(blogId=blogger_id, maxResults=500, status='DRAFT')
        res2 = req2.execute()
        draft_posts = res2.get('items', [])
        print(f"\n비공개/임시저장(DRAFT) 상태 게시물 수: {len(draft_posts)}개")
        
    except Exception as e:
        print(f"에러: {e}")

if __name__ == '__main__':
    check_status()
