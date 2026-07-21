import requests
from bs4 import BeautifulSoup

url = "https://www.mohw.go.kr/board.es?mid=a10501010000&bid=0003&list_no=1488794&act=view"
headers = {'User-Agent': 'Mozilla/5.0'}

res = requests.get(url, headers=headers)
res.encoding = 'euc-kr'
soup = BeautifulSoup(res.text, 'html.parser')

print("--- All Images on the page ---")
for img in soup.find_all('img'):
    src = img.get('src')
    print(f"Src: {src} | Alt: {img.get('alt')}")

print("\n--- Content Elements check ---")
content_selectors = [".view_cont", ".vc_detail", "#contents", ".article-body", ".board_view", ".view_article", ".post_content"]
for sel in content_selectors:
    elem = soup.select_one(sel)
    if elem:
        print(f"Selector '{sel}' exists.")
        # Is there any text that looks like it should have an image?
        # Sometimes images are in a separate div or in a table.
    else:
        # print(f"Selector '{sel}' does NOT exist.")
        pass
