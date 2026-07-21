"""auto_blog.log 분석 스크립트"""
import re

# 로그 파일 읽기
with open('auto_blog.log', 'r', encoding='utf-8', errors='ignore') as f:
    log_content = f.read()

# 마지막 실행 로그만 추출 (가장 최근 "정부 정책 자동 블로그 포스팅 시작" 이후)
sections = log_content.split('정부 정책 자동 블로그 포스팅 시작')
if len(sections) > 1:
    last_run = sections[-1]
else:
    last_run = log_content

# 통계 추출
posted_success = len(re.findall(r'✅ 포스팅 성공:', last_run))
posted_fail = len(re.findall(r'포스팅 실패', last_run))
crawl_fail = len(re.findall(r'원문 크롤링 실패', last_run))
gemini_fail = len(re.findall(r'블로그 글 작성 실패', last_run))

# 최종 결과 찾기
final_result = re.search(r'작업 완료: 성공 (\d+)개, 실패 (\d+)개', last_run)

print('='*70)
print('포스팅 로그 분석 결과')
print('='*70)
print(f'✅ 포스팅 성공: {posted_success}개')
print(f'❌ 포스팅 실패: {posted_fail}개')
print(f'❌ 크롤링 실패: {crawl_fail}개')
print(f'❌ Gemini 실패: {gemini_fail}개')

if final_result:
    print(f'\n최종 결과: 성공 {final_result.group(1)}개, 실패 {final_result.group(2)}개')

# 실패 사유 찾기
print('\n' + '='*70)
print('실패 원인 상세:')
print('='*70)

# 에러 메시지 추출
errors = re.findall(r'\[ERROR\].*', last_run)
warnings = re.findall(r'\[WARNING\].*', last_run)

if errors:
    print(f'\n에러 메시지 ({len(errors)}개):')
    for i, err in enumerate(errors[:10], 1):  # 처음 10개만
        print(f'{i}. {err[:150]}')

if warnings:
    print(f'\n경고 메시지 ({len(warnings)}개):')
    for i, warn in enumerate(warnings[:10], 1):
        print(f'{i}. {warn[:150]}')
