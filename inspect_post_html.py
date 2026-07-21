import urllib.request
import re

url = "https://story0people.blogspot.com/2026/07/10-20.html"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    with open("downloaded_post.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML downloaded successfully. Size:", len(html))
except Exception as e:
    print("Error downloading:", e)
