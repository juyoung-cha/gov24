import urllib.request

url = "https://story0people.blogspot.com/2026/07/7-31.html"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    with open("downloaded_fixed_post.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Fixed HTML downloaded successfully. Size:", len(html))
except Exception as e:
    print("Error downloading:", e)
