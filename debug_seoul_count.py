import json
from rss_collector import RSSCollector
from datetime import datetime

collector = RSSCollector()
url = "https://www.seoul.go.kr/seoul/mediahub.do?schAgeVals=&schTargetVals=&schBunyaVals=&schType=TAG&schValue="
items = collector.fetch_rss("서울시 정책뉴스", url)

print(f"Total Seoul items fetched: {len(items)}")

target_date_filter = datetime(2026, 1, 1)
filtered_count = 0
for item in items:
    date_str = item.get("date")
    if date_str:
        try:
            dt = None
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except: pass
            
            if not dt:
                try:
                    dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                except: pass
            
            if not dt:
                try:
                    clean_date_str = date_str.rstrip(".")
                    dt = datetime.strptime(clean_date_str, "%Y.%m.%d")
                except: pass
            
            if dt and dt >= target_date_filter:
                filtered_count += 1
        except:
            pass

print(f"Items after date filter (>= 2026-01-01): {filtered_count}")
