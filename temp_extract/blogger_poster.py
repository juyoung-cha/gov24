"""
Google Blogger API 연동 모듈
OAuth 인증 및 자동 포스팅을 처리합니다.
"""
import logging
from typing import Dict, Optional, List
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle

logger = logging.getLogger(__name__)


class BloggerPoster:
    """Blogger 자동 포스팅"""
    
    SCOPES = ['https://www.googleapis.com/auth/blogger']
    
    def __init__(self, blog_id: str = None, credentials_file: str = "credentials.json", gcs_bucket: str = None):
        """
        Args:
            blog_id: Blogger 블로그 ID (선택, None이면 자동으로 첫 번째 블로그 사용)
            credentials_file: OAuth 인증 정보 파일 경로
            gcs_bucket: GCS 버킷 이름 (클라우드 환경용)
        """
        self.blog_id = blog_id
        self.credentials_file = credentials_file
        self.gcs_bucket = gcs_bucket
        self.service = None
        self._authenticate()
        
        if not self.blog_id:
            self.blog_id = self._get_default_blog_id()
        
        logger.info(f"BloggerPoster 초기화 완료 (블로그 ID: {self.blog_id})")
    
    def _authenticate(self):
        """OAuth 인증 처리"""
        creds = None
        token_file = "token.pickle"
        
        # 1. GCS 버킷이 설정된 경우 먼저 확인
        if self.gcs_bucket:
            try:
                from storage_manager import StorageManager
                sm = StorageManager(self.gcs_bucket)
                token_data = sm.load_token(token_file)
                if token_data:
                    creds = pickle.loads(token_data)
                    logger.info("GCS에서 token.pickle 로드 완료")
            except Exception as e:
                logger.warning(f"GCS 토큰 로드 시도 실패: {e}")

        # 2. 로컬 토큰 확인 (GCS가 없거나 실패한 경우)
        if not creds and os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 토큰이 없거나 유효하지 않으면 재인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"{self.credentials_file} 파일이 없습니다.")
                    raise FileNotFoundError(
                        f"{self.credentials_file} 파일을 다운로드하여 프로젝트 폴더에 저장하세요.\n"
                        "다운로드: https://console.cloud.google.com/apis/credentials"
                    )
                
                # GCP/Serverless 환경인지 확인
                if self.gcs_bucket or os.getenv("K_SERVICE") or os.getenv("FUNCTION_TARGET"):
                    logger.error("GCP 서버 환경에서는 브라우저 로그인(OAuth flow)을 진행할 수 없습니다.")
                    logger.error("로컬에서 먼저 실행하여 'token.pickle'을 생성한 뒤, GCS 버킷에 업로드해 주세요.")
                    raise RuntimeError("OAuth 인증 토큰이 없거나 만료되었습니다. 클라우드 환경에서는 자동 갱신이 불가능합니다.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            token_bytes = pickle.dumps(creds)
            
            # 로컬 저장 (GCS 버킷이 없을 때만 시도 - 클라우드에서는 실패함)
            if not self.gcs_bucket:
                try:
                    with open(token_file, 'wb') as token:
                        token.write(token_bytes)
                except Exception as e:
                    logger.warning(f"로컬 토큰 저장 실패 (정상적인 클라우드 환경): {e}")
            
            # GCS 버킷이 있으면 GCS에도 저장
            if self.gcs_bucket:
                try:
                    from storage_manager import StorageManager
                    sm = StorageManager(self.gcs_bucket)
                    sm.save_token(token_bytes, token_file)
                    logger.info("token.pickle GCS 백업 완료")
                except Exception as e:
                    logger.error(f"token.pickle GCS 저장 실패: {e}")
        
        self.service = build('blogger', 'v3', credentials=creds)
        logger.info("Blogger API 인증 성공")
    
    def _get_default_blog_id(self) -> str:
        """첫 번째 블로그 ID 가져오기"""
        try:
            blogs = self.service.blogs().listByUser(userId='self').execute()
            
            if 'items' in blogs and len(blogs['items']) > 0:
                blog_id = blogs['items'][0]['id']
                blog_name = blogs['items'][0]['name']
                logger.info(f"기본 블로그 선택: {blog_name} (ID: {blog_id})")
                return blog_id
            else:
                raise ValueError("Blogger 블로그가 없습니다. blogspot.com에서 블로그를 먼저 생성하세요.")
        
        except HttpError as e:
            logger.error(f"블로그 목록 조회 실패: {e}")
            raise
    
    def post(self, title: str, content: str, labels: List[str] = None, 
             is_draft: bool = False) -> Optional[str]:
        """
        블로그 글 포스팅
        
        Args:
            title: 글 제목
            content: HTML 형식 본문
            labels: 라벨(태그) 리스트
            is_draft: True면 임시저장, False면 바로 게시
            
        Returns:
            포스팅 URL 또는 None
        """
        try:
            logger.info(f"Blogger 포스팅 시작: {title[:30]}...")
            
            post_data = {
                'kind': 'blogger#post',
                'blog': {'id': self.blog_id},
                'title': title,
                'content': content
            }
            
            # 라벨(태그) 추가 (Blogger 길이 제한 40자 준수)
            if labels:
                trimmed_labels = []
                for label in labels:
                    if len(label) > 40:
                        label = label[:37] + "..."
                    trimmed_labels.append(label)
                post_data['labels'] = trimmed_labels
            
            # 포스팅
            if is_draft:
                # 임시저장
                result = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_data,
                    isDraft=True
                ).execute()
            else:
                # 바로 게시
                result = self.service.posts().insert(
                    blogId=self.blog_id,
                    body=post_data
                ).execute()
            
            post_url = result.get('url')
            logger.info(f"포스팅 성공: {post_url}")
            return post_url
        
        except HttpError as e:
            logger.error(f"Blogger 포스팅 오류: {e}")
            return None
        except Exception as e:
            logger.error(f"포스팅 오류: {str(e)}")
            return None

    def create_page(self, title: str, content: str, is_draft: bool = False) -> Optional[str]:
        """
        블로그 고정 페이지(About, Privacy 등) 생성
        
        Args:
            title: 페이지 제목
            content: HTML 형식 본문
            is_draft: True면 임시저장, False면 바로 게시
            
        Returns:
            페이지 URL 또는 None
        """
        try:
            logger.info(f"Blogger 페이지 생성 시작: {title}")
            
            page_data = {
                'kind': 'blogger#page',
                'blog': {'id': self.blog_id},
                'title': title,
                'content': content
            }
            
            result = self.service.pages().insert(
                blogId=self.blog_id,
                body=page_data,
                isDraft=is_draft
            ).execute()
            
            page_url = result.get('url')
            logger.info(f"페이지 생성 성공: {page_url}")
            return page_url
        
        except HttpError as e:
            logger.error(f"Blogger 페이지 생성 오류: {e}")
            return None
        except Exception as e:
            logger.error(f"페이지 생성 오류: {str(e)}")
            return None
    
    def get_blogs(self) -> Optional[List[Dict]]:
        """
        사용자의 블로그 목록 조회
        
        Returns:
            블로그 정보 리스트
        """
        try:
            result = self.service.blogs().listByUser(userId='self').execute()
            
            if 'items' in result:
                blogs = []
                for blog in result['items']:
                    blogs.append({
                        'id': blog.get('id'),
                        'name': blog.get('name'),
                        'url': blog.get('url'),
                        'description': blog.get('description', '')
                    })
                logger.info(f"블로그 조회 성공: {len(blogs)}개")
                return blogs
            else:
                logger.info("블로그가 없습니다")
                return []
        
        except HttpError as e:
            logger.error(f"블로그 조회 오류: {e}")
            return None

    def update_post(self, post_id: str, title: str, content: str, labels: List[str] = None) -> bool:
        """
        기존 게시물 수정
        """
        try:
            post_data = {
                'title': title,
                'content': content
            }
            if labels:
                post_data['labels'] = labels
                
            self.service.posts().update(
                blogId=self.blog_id,
                postId=post_id,
                body=post_data
            ).execute()
            
            logger.info(f"게시물 수정 성공 (ID: {post_id})")
            return True
            
        except HttpError as e:
            logger.error(f"Blogger 수정 오류 (ID: {post_id}): {e}")
            return False
        except Exception as e:
            logger.error(f"수정 오류: {str(e)}")
            return False

    def list_posts(self, max_results: int = 10) -> List[Dict]:
        """
        게시물 목록 조회
        """
        try:
            result = self.service.posts().list(
                blogId=self.blog_id,
                maxResults=max_results,
                fetchBodies=True
            ).execute()
            
            return result.get('items', [])
            
        except HttpError as e:
            logger.error(f"게시물 목록 조회 오류: {e}")
            return []

    def delete_post(self, post_id: str) -> bool:
        """
        게시물 삭제
        
        Args:
            post_id: 삭제할 게시물 ID
            
        Returns:
            성공 여부
        """
        try:
            self.service.posts().delete(
                blogId=self.blog_id,
                postId=post_id
            ).execute()
            logger.info(f"게시물 삭제 성공: {post_id}")
            return True
        except HttpError as e:
            logger.error(f"게시물 삭제 실패 ({post_id}): {e}")
            return False


class BloggerAuthHelper:
    """Blogger OAuth 인증 헬퍼 (초기 설정용)"""
    
    @staticmethod
    def setup_credentials():
        """
        OAuth 인증 정보 설정 가이드
        """
        print("=" * 60)
        print("Blogger API 인증 설정")
        print("=" * 60)
        print()
        print("1. Google Cloud Console 접속:")
        print("   https://console.cloud.google.com/")
        print()
        print("2. 프로젝트 선택 (또는 새로 생성)")
        print()
        print("3. 'Blogger API v3' 활성화:")
        print("   - API 및 서비스 > 라이브러리")
        print("   - 'Blogger API' 검색")
        print("   - '사용 설정' 클릭")
        print()
        print("4. OAuth 동의 화면 구성:")
        print("   - API 및 서비스 > OAuth 동의 화면")
        print("   - 외부 선택 > 만들기")
        print("   - 앱 이름 입력")
        print()
        print("5. 사용자 인증 정보 만들기:")
        print("   - API 및 서비스 > 사용자 인증 정보")
        print("   - '+ 사용자 인증 정보 만들기' > OAuth 클라이언트 ID")
        print("   - 애플리케이션 유형: 데스크톱 앱")
        print("   - 이름 입력 > 만들기")
        print()
        print("6. JSON 다운로드:")
        print("   - 생성된 클라이언트 ID 옆의 다운로드 아이콘 클릭")
        print("   - 파일을 'credentials.json'으로 저장")
        print("   - 프로젝트 폴더(d:\\AI\\gov24)에 복사")
        print()
        print("=" * 60)
        print("완료 후 python test_blogger.py 실행")
        print("=" * 60)
