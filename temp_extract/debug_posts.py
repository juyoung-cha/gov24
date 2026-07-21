from blogger_poster import BloggerPoster
import json

def check_posts():
    poster = BloggerPoster()
    posts = poster.list_posts(max_results=10)
    for i, post in enumerate(posts):
        print(f"--- Post {i+1} ---")
        print(f"Title: {post['title']}")
        print(f"Labels: {post.get('labels', [])}")
        print(f"URL: {post['url']}")
        print("-" * 20)

if __name__ == "__main__":
    check_posts()
