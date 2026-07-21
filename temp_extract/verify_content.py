from blogger_poster import BloggerPoster
import json

def check_content():
    poster = BloggerPoster()
    posts = poster.list_posts(max_results=3)
    for i, post in enumerate(posts):
        print(f"--- Post {i+1} Content Snippet ---")
        print(f"Title: {post['title']}")
        print(post['content'][:200]) # 처음 200자만 출력
        print("-" * 30)

if __name__ == "__main__":
    check_content()
