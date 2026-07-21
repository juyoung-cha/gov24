import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
import re

html = open('downloaded_post.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

post_body = soup.find('div', class_=re.compile(r'post-body'))
if post_body:
    print("=" * 60)
    print("Post Body Inner HTML:")
    print("=" * 60)
    print(post_body.prettify()[:3000])
else:
    print("post-body div not found!")
