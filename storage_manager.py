"""
Google Cloud Storage 연동 모듈
seen.json 파일을 GCS에서 관리합니다.
"""
import json
import logging
import typing
from typing import Set

# Google Cloud Storage는 선택적으로 import (로컬 환경에서는 불필요)
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    storage = None

import pickle
import io
import os

logger = logging.getLogger(__name__)


class StorageManager:
    """GCS 스토리지 관리자"""
    
    def __init__(self, bucket_name: str, file_name: str = "seen.json"):
        """
        Args:
            bucket_name: GCS 버킷 이름
            file_name: 저장할 파일명 (기본: seen.json)
        """
        if not GCS_AVAILABLE:
            raise ImportError(
                "google-cloud-storage가 설치되지 않았습니다. "
                "로컬 실행 시 LocalStorageManager를 사용하세요."
            )
        
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"StorageManager 초기화 완료 (버킷: {bucket_name})")
    
    def load_seen(self) -> Set[str]:
        """
        GCS에서 seen.json 로드
        
        Returns:
            확인한 링크 셋
        """
        try:
            blob = self.bucket.blob(self.file_name)
            
            if not blob.exists():
                logger.info("seen.json 파일이 없습니다. 새로 시작합니다.")
                return set()
            
            data = blob.download_as_text()
            seen_list = json.loads(data)
            
            logger.info(f"seen.json 로드 완료 (총 {len(seen_list)}개 항목)")
            return set(seen_list)
        
        except Exception as e:
            logger.error(f"seen.json 로드 실패: {e}. 새로 시작합니다.")
            return set()
    
    def save_seen(self, seen: Set[str]):
        """
        seen.json을 GCS에 저장
        
        Args:
            seen: 확인한 링크 셋
        """
        try:
            blob = self.bucket.blob(self.file_name)
            
            data = json.dumps(list(seen), ensure_ascii=False, indent=2)
            blob.upload_from_string(data, content_type="application/json")
            
            logger.info(f"seen.json 저장 완료 (총 {len(seen)}개 항목)")
        
        except Exception as e:
            logger.error(f"seen.json 저장 실패: {e}")

    def load_token(self, token_file: str = "token.pickle") -> typing.Optional[bytes]:
        """GCS에서 token.pickle 로드"""
        try:
            blob = self.bucket.blob(token_file)
            if not blob.exists():
                return None
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"token.pickle 로드 실패: {e}")
            return None

    def save_token(self, creds_bytes: bytes, token_file: str = "token.pickle"):
        """GCS에 token.pickle 저장"""
        try:
            blob = self.bucket.blob(token_file)
            blob.upload_from_string(creds_bytes, content_type="application/octet-stream")
            logger.info("token.pickle GCS 저장 완료")
        except Exception as e:
            logger.error(f"token.pickle 저장 실패: {e}")


class LocalStorageManager:
    """로컬 파일 시스템 관리자 (테스트용)"""
    
    def __init__(self, file_path: str = "seen.json"):
        """
        Args:
            file_path: 로컬 파일 경로
        """
        self.file_path = file_path
        logger.info(f"LocalStorageManager 초기화 완료 (파일: {file_path})")
    
    def load_seen(self) -> Set[str]:
        """로컬 파일에서 seen.json 로드"""
        try:
            import os
            if not os.path.exists(self.file_path):
                logger.info("seen.json 파일이 없습니다. 새로 시작합니다.")
                return set()
            
            with open(self.file_path, "r", encoding="utf-8-sig") as f:
                seen_list = json.load(f)
            
            logger.info(f"seen.json 로드 완료 (총 {len(seen_list)}개 항목)")
            return set(seen_list)
        
        except Exception as e:
            logger.error(f"seen.json 로드 실패: {e}. 새로 시작합니다.")
            return set()
    
    def save_seen(self, seen: Set[str]):
        """로컬 파일에 seen.json 저장 (Atomic Write)"""
        try:
            import tempfile
            
            # 1. 임시 파일 생성
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(self.file_path), suffix=".tmp")
            try:
                # 2. 임시 파일에 데이터 쓰기
                with os.fdopen(fd, 'w', encoding="utf-8") as f:
                    json.dump(list(seen), f, ensure_ascii=False, indent=2)
                
                # 3. 기존 파일 교체 (Atomic)
                # Windows의 경우 Destination이 있으면 에러나므로 고전적 방법 사용
                if os.path.exists(self.file_path):
                    backup_path = self.file_path + ".bak"
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(self.file_path, backup_path)
                
                os.rename(temp_path, self.file_path)
                logger.info(f"seen.json 저장 완료 (총 {len(seen)}개 항목)")
                
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
                
        except Exception as e:
            logger.error(f"seen.json 저장 실패: {e}")
