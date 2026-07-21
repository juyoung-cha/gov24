import requests
from bs4 import BeautifulSoup

url = "https://www.mohw.go.kr/board.es?mid=a10501010000&bid=0003&list_no=1488794&act=view"
headers = {'User-Agent': 'Mozilla/5.0'}

res = requests.get(url, headers=headers)
res.encoding = 'euc-kr' # 보합시도
soup = BeautifulSoup(res.text, 'html.parser')

# 제목 확인
title = soup.find('title')
print(f"Title: {title.text if title else 'N/A'}")

# 본문일 것으로 예상되는 후보들 출력
selectors = [".view_cont", ".vc_detail", "#contents", ".article-body", ".board_view", ".view_article"]
for sel in selectors:
    elem = soup.select_one(sel)
    if elem:
        print(f"Found selector: {sel}")
        # 이미지 태그 찾기
        imgs = elem.find_all('img')
        print(f"  Images in {sel}: {len(imgs)}")
        for i, img in enumerate(imgs):
            print(f"    Img {i}: {img.get('src')}")
    else:
        # print(f"Not found: {sel}")
        pass

# 전체 이미지 확인 (페이지 내 모든 이미지)
all_imgs = soup.find_all('img')
print(f"Total images on page: {len(all_imgs)}")
