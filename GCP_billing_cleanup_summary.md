# GCP 비용 청구 차단 조치 및 대화 요약서

* **작성일시**: 2026-07-03
* **관련 프로젝트**: `petmind-10422` (GCP)
* **작업 목적**: 구글 클라우드 플랫폼(GCP)으로 인한 원치 않는 비용 청구(307원 등 소액 청구)를 방지하기 위해 배포된 리소스를 완전 중단하고 삭제하는 조치

---

## 1. 진단 내용 (문제 요인)
GCP 프로젝트에 아래와 같은 리소스가 활성화되어 있어 지속적으로 보관 비용(특히 서울 리전 스토리지 비용)이 청구되고 있었습니다.
* **Cloud Functions (2nd Gen)**: `fetch-lotto`, `gov-blog-auto-poster`, `gov-blog-bot-v2`, `scheduledCrawl`
* **Cloud Scheduler**: `lotto-weekly-fetch`, `gov-blog-hourly`, `firebase-schedule-scheduledCrawl-us-central1`
* **Cloud Storage 버킷**: `gov24-blog-data-petmind-10422`, `lotto-data-petmind-10422` 등 총 7개의 버킷 및 빌드 파일 스토리지

---

## 2. 해결을 위해 수행한 조치
비용 발생 요인을 원천적으로 차단하기 위해 아래와 같이 **결제 비활성화** 및 **프로젝트 삭제**를 수행했습니다.

1. **결제 계정 연결 해제 (Billing Unlink)**
   * **수행 명령어**: `gcloud billing projects unlink petmind-10422`
   * **결과**: 결제 상태 `billingEnabled: false` 처리 완료. 프로젝트 내부의 모든 유료 서비스 가동이 즉시 중지되었으며, 더 이상 카드로 비용이 청구되지 않습니다.
   
2. **GCP 프로젝트 삭제 요청 (Shut Down)**
   * **수행 명령어**: `gcloud projects delete petmind-10422 --quiet`
   * **결과**: `Deleted [https://cloudresourcemanager.googleapis.com/v1/projects/petmind-10422]` 로그 확인. 프로젝트 및 하위의 모든 리소스(함수, 버킷, 빌드 스토리지 등)가 삭제 프로세스에 진입했습니다.

---

## 3. 다른 영역의 영향 여부 (안전 확인)
이번 삭제 처리는 클라우드의 실행 환경만 지운 것으로, 아래의 다른 서비스에는 전혀 영향이 가지 않습니다.
* **로컬 파일 (`d:\AI\gov24`)**: 컴퓨터에 보관된 개발 소스 코드(`main.py` 등)는 원본 그대로 안전하게 보존됩니다.
* **구글 블로그 (Blogger)**: 이미 작성 및 발행된 블로그 글들과 블로그 계정 자체는 영향을 받지 않고 그대로 유지됩니다.
* **애드센스/애널리틱스**: 기존 광고 수익용 애드센스 계정 및 웹로그 분석 계정은 독립적이므로 안전합니다.

---

## 4. 유의 사항
* 구글의 클라우드 정책에 따라 삭제 요청된 프로젝트는 **30일의 유예 기간**을 거쳐 영구 삭제됩니다.
* 30일 이내에 원하실 경우 `gcloud projects undelete petmind-10422` 명령어로 복구할 수 있으나, 복구 시 비용이 다시 청구될 수 있으므로 **그대로 두시면 자동으로 소멸**됩니다.
* 유예 기간 동안에는 절대 추가 비용이 청구되지 않습니다.
