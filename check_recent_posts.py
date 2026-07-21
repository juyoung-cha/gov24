#!/usr/bin/env python3
"""최근 포스팅 내역을 확인하는 스크립트"""

import re
from datetime import datetime

# 로그 파일 읽기
with open('auto_blog.log', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 최근 실행 (21:26~21:28) 로그만 필터링
recent_logs = [line for line in lines if '2026-02-04 21:2' in line]

print("=" * 70)
print("최근 실행 (21:26~21:28) 상세 분석")
print("=" * 70)

# 신규 항목 발견
new_items = [line for line in recent_logs if '신규 항목' in line or 'new_items' in line]
if new_items:
    print("\n📊 신규 항목 발견:")
    for line in new_items:
        print(f"  {line.strip()}")

# 처리 중인 항목들
processing = [line for line in recent_logs if '처리 중:' in line]
print(f"\n📝 처리 시도한 항목: {len(processing)}개")
for i, line in enumerate(processing, 1):
    match = re.search(r'처리 중: (.+)', line)
    if match:
        print(f"  {i}. {match.group(1).strip()}")

# 성공한 포스팅
success = [line for line in recent_logs if '포스팅 성공' in line]
print(f"\n✅ 포스팅 성공: {len(success)}개")
for line in success:
    match = re.search(r'포스팅 성공: (.+)', line)
    if match:
        print(f"  - {match.group(1).strip()}")

# 실패한 항목
errors = [line for line in recent_logs if 'ERROR' in line]
print(f"\n❌ 오류 발생: {len(errors)}개")
for line in errors:
    print(f"  {line.strip()}")

# 최종 결과
final_result = [line for line in recent_logs if '작업 완료' in line]
if final_result:
    print("\n" + "=" * 70)
    print("최종 결과:")
    print("=" * 70)
    for line in final_result:
        print(f"  {line.strip()}")

print("\n" + "=" * 70)
