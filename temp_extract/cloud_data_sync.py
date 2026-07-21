import json
import os
import pickle
import logging
from google.cloud import storage

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def sync_to_cloud():
    # 1. 설정 로드
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    project_id = config["gcs"].get("project_id", "petmind-10422")
    bucket_name = config["gcs"].get("bucket_name")
    
    if not bucket_name:
        bucket_name = f"gov24-blog-data-{project_id}"
        logger.info(f"버킷 이름이 설정되지 않아 기본값으로 설정합니다: {bucket_name}")
        # config 업데이트 제안
        config["gcs"]["bucket_name"] = bucket_name
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.info("config.json의 bucket_name을 업데이트했습니다.")

    client = storage.Client(project=project_id)
    
    # 2. 버킷 존재 확인 및 생성
    try:
        bucket = client.get_bucket(bucket_name)
        logger.info(f"기존 버킷 확인: {bucket_name}")
    except Exception:
        logger.info(f"버킷이 없어 새로 생성합니다: {bucket_name}")
        bucket = client.create_bucket(bucket_name, location="asia-northeast3")
        logger.info(f"버킷 생성 완료: {bucket_name}")

    # 3. seen.json 업로드
    if os.path.exists("seen.json"):
        blob = bucket.blob("seen.json")
        blob.upload_from_filename("seen.json")
        logger.info("seen.json GCS 업로드 완료")
    
    # 4. token.pickle 업로드
    if os.path.exists("token.pickle"):
        blob = bucket.blob("token.pickle")
        blob.upload_from_filename("token.pickle")
        logger.info("token.pickle GCS 업로드 완료")
    
    logger.info("=" * 60)
    logger.info("클라우드 데이터 동기화 완료!")
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        sync_to_cloud()
    except Exception as e:
        logger.error(f"동기화 오류: {e}")
