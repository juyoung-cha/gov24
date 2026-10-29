import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import logging
from blogger_poster import BloggerPoster

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_posts_diet(keep_count=15):
    bp = BloggerPoster()
    logger.info("모든 LIVE 포스트를 조회합니다...")
    
    posts = []
    page_token = None
    while True:
        try:
            res = bp.service.posts().list(blogId=bp.blog_id, maxResults=500, pageToken=page_token, status=['LIVE']).execute()
            items = res.get('items', [])
            posts.extend(items)
            page_token = res.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            logger.warning(f"목록 조회 중 일시 오류 ({e}), 3초 후 재시도...")
            time.sleep(3)
            bp = BloggerPoster()
            
    total = len(posts)
    logger.info(f"현재 총 {total}개의 LIVE 포스트가 확인되었습니다.")
    
    if total <= keep_count:
        logger.info(f"이미 LIVE 포스트가 {total}개로 {keep_count}개 이하입니다. 작업이 완료되었습니다.")
        return
        
    keep_posts = posts[:keep_count]
    revert_posts = posts[keep_count:]
    
    logger.info(f"== [유지할 최신 정예 포스트 {len(keep_posts)}개] ==")
    for i, p in enumerate(keep_posts, 1):
        logger.info(f"  {i}. [{p.get('published')[:10]}] {p.get('title')[:40]}...")
        
    logger.info(f"\n총 {len(revert_posts)}개의 과거 포스트를 '초안(Draft/비공개)'으로 전환합니다.")
    
    reverted_count = 0
    for i, p in enumerate(revert_posts, 1):
        post_id = p.get('id')
        title = p.get('title', '무제')[:30]
        
        success = False
        for attempt in range(4):
            try:
                bp.service.posts().revert(blogId=bp.blog_id, postId=post_id).execute()
                reverted_count += 1
                success = True
                break
            except Exception as e:
                logger.warning(f"[{post_id}] 전환 시도 {attempt+1} 실패 ({e}), 재연결 후 재시도...")
                time.sleep(2 * (attempt + 1))
                try:
                    bp = BloggerPoster()
                except:
                    pass
        if not success:
            logger.error(f"[{post_id}] 최종 전환 실패 건너뜀.")
            
        if i % 10 == 0 or i == len(revert_posts):
            logger.info(f"진행 중... ({i}/{len(revert_posts)}) 완료 (누적 성공: {reverted_count})")
        time.sleep(0.4)
            
    logger.info(f"🎉 성공적으로 {reverted_count}개의 포스트를 초안(Draft)으로 보관 완료했습니다!")
    logger.info(f"남은 공개(LIVE) 글: {total - reverted_count}개")

if __name__ == "__main__":
    run_posts_diet(keep_count=15)
