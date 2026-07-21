import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
import re

html = open('downloaded_fixed_post.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

post_body = soup.find('div', class_=re.compile(r'post-body'))
if post_body:
    print("=" * 60)
    print("Fixed Post Body Inner HTML (Length:", len(post_body.get_text()), "chars)")
    print("=" * 60)
    print(post_body.prettify()[:3000])
else:
    print("post-body div not found!")
