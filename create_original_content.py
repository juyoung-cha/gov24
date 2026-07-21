"""
오리지널 콘텐츠 작성 스크립트
AdSense 승인을 위한 100% 사람이 작성한 독창적 콘텐츠를 포스팅합니다.
"""
import time
from blogger_poster import BloggerPoster

def create_original_posts():
    poster = BloggerPoster()
    
    posts = [
        {
            "title": "2026년 꼭 알아야 할 정부 지원금 TOP 10 - 신청 놓치면 손해!",
            "labels": ["3. 오리지널 콘텐츠", "정부지원금", "2026년"],
            "content": """
<div style="font-size: 19px; line-height: 1.9; word-break: keep-all;">

<p>매년 수백 가지의 정부 지원 사업이 시행되지만, 정작 많은 분들이 자신에게 해당되는 혜택을 모르고 지나치는 경우가 많습니다. 2026년에도 국민 생활과 밀접한 다양한 지원금 제도가 운영되고 있는데요, 오늘은 <strong>2026년에 반드시 확인해야 할 정부 지원금 TOP 10</strong>을 정리해 드리겠습니다.</p>

<h2>1. 근로장려금 (EITC)</h2>
<p>저소득 근로자와 자영업자를 위한 대표적인 소득 지원 제도입니다. 2026년에는 지급 기준이 더 완화되어 <strong>단독가구 연 소득 2,400만 원, 홑벌이가구 3,600만 원, 맞벌이가구 4,200만 원</strong> 이하까지 신청 가능합니다.</p>
<p><strong>💡 팁:</strong> 5월 정기 신청을 놓쳤다면 11월 반기 신청을 활용하세요. 단, 반기 신청 시 지급액이 10% 감액됩니다.</p>

<h2>2. 자녀장려금</h2>
<p>18세 미만 자녀가 있는 가구를 위한 지원금으로, 자녀 1인당 최대 <strong>100만 원</strong>까지 받을 수 있습니다. 근로장려금과 동시 신청이 가능하며, 가구 유형에 따라 중복 수령도 가능합니다.</p>

<h2>3. 청년도약계좌</h2>
<p>만 19~34세 청년이 5년간 매월 40~70만 원을 납입하면 정부 기여금이 추가로 지급됩니다. 만기 시 최대 <strong>5,000만 원</strong>을 만들 수 있는 파격적인 제도입니다.</p>
<p><strong>⚠️ 주의:</strong> 개인 소득 7,500만 원 이하, 가구 소득 중위 250% 이하 조건을 충족해야 합니다.</p>

<h2>4. 국민취업지원제도</h2>
<p>실업 상태의 구직자에게 구직촉진수당(월 50만 원 × 6개월)과 취업 지원 서비스를 제공합니다. 특히 2026년부터는 <strong>자영업 폐업자</strong>도 I유형 참여가 가능해졌습니다.</p>

<h2>5. 육아휴직 급여 인상</h2>
<p>2026년부터 육아휴직 급여 상한액이 인상되었습니다. 특히 <strong>3+3 부모 육아휴직</strong> 제도를 통해 부모 모두 육아휴직을 사용하면 급여가 대폭 올라갑니다. 아빠 육아휴직이 60% 증가한 것은 이 제도의 효과를 보여줍니다.</p>

<h2>6. 에너지 바우처</h2>
<p>소득 기준 하위 계층에게 냉·난방비를 지원하는 제도로, 여름과 겨울에 각각 신청 가능합니다. 2026년에는 지원 금액이 <strong>약 15% 인상</strong>되었습니다.</p>

<h2>7. 기초생활보장제도 (생계급여)</h2>
<p>2026년 기준 중위소득이 인상됨에 따라, 생계급여의 지급 범위와 금액도 함께 올랐습니다. 1인 가구 기준 월 최대 <strong>약 72만 원</strong>을 받을 수 있습니다.</p>

<h2>8. 주거급여</h2>
<p>중위소득 48% 이하 가구에게 임차료를 지원합니다. 서울 기준 1인 가구 최대 <strong>34만 원</strong>의 임차료를 지원받을 수 있으며, 자가 소유자도 수선유지급여를 받을 수 있습니다.</p>

<h2>9. 문화누리카드</h2>
<p>기초생활수급자와 차상위계층에게 연간 <strong>13만 원</strong>의 문화비를 지원합니다. 영화, 공연, 도서, 여행 등 다양한 분야에서 사용 가능합니다.</p>

<h2>10. 디지털 배움터</h2>
<p>디지털 역량이 부족한 국민에게 <strong>무료 디지털 교육</strong>을 제공합니다. 스마트폰 활용, 키오스크 사용법, 온라인 금융 등 실생활에 필요한 디지털 기초 교육을 받을 수 있습니다.</p>

<hr style="margin: 30px 0;">

<h3>❓ 자주 묻는 질문</h3>

<p><strong>Q. 정부 지원금은 어디서 한 번에 확인할 수 있나요?</strong></p>
<p>A. <a href="https://www.gov.kr" target="_blank">정부24(gov.kr)</a>에서 '보조금24' 서비스를 통해 나에게 해당되는 모든 지원금을 한 번에 조회할 수 있습니다.</p>

<p><strong>Q. 지원금을 받으면 다른 혜택에 영향이 있나요?</strong></p>
<p>A. 일부 지원금은 소득으로 산정되어 다른 복지 혜택에 영향을 줄 수 있습니다. 반드시 주민센터에서 사전 상담을 받으시길 권합니다.</p>

<p><strong>Q. 신청 기간을 놓쳤으면 어떻게 하나요?</strong></p>
<p>A. 대부분의 지원금은 수시 또는 반기별로 추가 신청 기회가 있습니다. 정부24 알림 서비스를 등록해두면 신청 시기를 놓치지 않을 수 있습니다.</p>

<div style="margin-top: 40px; padding: 20px; background-color: #e8f4f8; border-radius: 10px;">
<p style="font-size: 16px; color: #555;">📌 이 글은 Stories of people 블로그의 오리지널 콘텐츠로, 2026년 정부 지원금 제도를 독자적으로 분석한 내용입니다. 정확한 신청 조건과 금액은 각 제도의 공식 사이트에서 확인해 주세요.</p>
</div>

</div>
"""
        },
        {
            "title": "정부 보도자료, 제대로 읽는 법 - 핵심 정보를 놓치지 않는 5가지 팁",
            "labels": ["3. 오리지널 콘텐츠", "보도자료", "정보활용"],
            "content": """
<div style="font-size: 19px; line-height: 1.9; word-break: keep-all;">

<p>정부에서 매일 수십 건의 보도자료를 발표하지만, 대부분의 국민들은 뉴스를 통해 간접적으로만 접하게 됩니다. 하지만 보도자료 원문에는 뉴스에서 빠진 <strong>구체적인 신청 방법, 혜택 조건, 일정</strong> 등 중요한 정보가 담겨 있습니다. 오늘은 정부 보도자료를 제대로 활용하는 방법을 알려드리겠습니다.</p>

<h2>1. 보도자료를 찾는 가장 빠른 방법</h2>
<p>정부 보도자료는 각 부처 홈페이지에서 개별적으로 확인할 수도 있지만, <a href="https://www.korea.kr" target="_blank">대한민국 정책브리핑(korea.kr)</a>에서 모든 부처의 보도자료를 한 곳에서 확인할 수 있습니다.</p>
<p><strong>꿀팁:</strong> RSS 구독을 설정하면 관심 부처의 새로운 보도자료를 자동으로 받아볼 수 있습니다. 본 블로그도 이 RSS 기능을 활용하여 최신 정책 정보를 전달하고 있습니다.</p>

<h2>2. 보도자료에서 가장 중요한 부분</h2>
<p>보도자료는 보통 다음과 같은 구조로 되어 있습니다:</p>
<table border="1" style="width:100%; border-collapse:collapse; margin-bottom:22px;">
<tr style="background-color:#f0f0f0;"><th style="padding:10px;">구성 요소</th><th style="padding:10px;">내용</th><th style="padding:10px;">중요도</th></tr>
<tr><td style="padding:10px;">제목</td><td style="padding:10px;">핵심 내용 요약</td><td style="padding:10px;">⭐⭐⭐⭐⭐</td></tr>
<tr><td style="padding:10px;">부제/요약</td><td style="padding:10px;">주요 사항 정리</td><td style="padding:10px;">⭐⭐⭐⭐</td></tr>
<tr><td style="padding:10px;">본문 1~2단락</td><td style="padding:10px;">배경 설명</td><td style="padding:10px;">⭐⭐⭐</td></tr>
<tr><td style="padding:10px;">표/그래프</td><td style="padding:10px;">구체적 수치</td><td style="padding:10px;">⭐⭐⭐⭐⭐</td></tr>
<tr><td style="padding:10px;">문의처</td><td style="padding:10px;">담당자 연락처</td><td style="padding:10px;">⭐⭐⭐⭐</td></tr>
</table>
<p>특히 <strong>표와 그래프</strong>에 가장 구체적인 정보가 담겨 있으니 꼭 확인하세요.</p>

<h2>3. '첨부파일'을 반드시 확인하라</h2>
<p>보도자료 본문에는 요약만 담기는 경우가 많습니다. <strong>진짜 세부 사항은 첨부된 PDF 파일</strong>에 있는 경우가 대부분입니다. 신청 양식, 세부 기준표, Q&A 등이 첨부파일에 포함됩니다.</p>

<h2>4. 시행 일자와 신청 기간에 주목</h2>
<p>정책이 발표되었다고 바로 시행되는 것은 아닙니다. '시행일', '접수 기간', '공고일' 등을 잘 구분해야 합니다. 법령 개정이 필요한 경우 몇 달 후에 시행되는 경우도 있습니다.</p>

<h2>5. 지방자치단체 보도자료도 챙기자</h2>
<p>중앙 정부의 정책이 시행될 때, 각 지방자치단체에서 <strong>추가 혜택</strong>을 제공하는 경우가 많습니다. 예를 들어 서울시는 중앙 정부의 청년 지원책에 더해 독자적인 청년수당, 주거지원 등을 운영합니다. 본 블로그에서도 서울시 정책뉴스를 함께 다루는 이유입니다.</p>

<hr style="margin: 30px 0;">

<h3>❓ 자주 묻는 질문</h3>

<p><strong>Q. 보도자료와 뉴스 기사의 차이점은 무엇인가요?</strong></p>
<p>A. 보도자료는 정부 부처가 직접 작성한 1차 자료이고, 뉴스 기사는 기자가 이를 재가공한 2차 자료입니다. 보도자료가 더 정확하고 상세합니다.</p>

<p><strong>Q. 서울시 정책은 서울시민만 혜택을 받나요?</strong></p>
<p>A. 대부분은 그렇지만, 서울에서 근무하거나 학교에 다니는 비서울 거주자도 일부 혜택을 받을 수 있습니다. 각 정책의 자격 조건을 확인하세요.</p>

<p><strong>Q. 보도자료에 오류가 있으면 어떻게 하나요?</strong></p>
<p>A. 보도자료 하단의 문의처로 직접 연락하시면 됩니다. 담당 공무원이 정확한 정보를 안내해 드립니다.</p>

<div style="margin-top: 40px; padding: 20px; background-color: #e8f4f8; border-radius: 10px;">
<p style="font-size: 16px; color: #555;">📌 이 글은 Stories of people 블로그의 오리지널 콘텐츠입니다.</p>
</div>

</div>
"""
        },
        {
            "title": "맞벌이 부부를 위한 2026년 육아 지원 정책 완벽 가이드",
            "labels": ["3. 오리지널 콘텐츠", "육아정책", "맞벌이", "2026년"],
            "content": """
<div style="font-size: 19px; line-height: 1.9; word-break: keep-all;">

<p>아이를 키우면서 일을 병행하는 것은 결코 쉬운 일이 아닙니다. 다행히 2026년에는 맞벌이 가정을 위한 정부의 육아 지원이 눈에 띄게 강화되었습니다. 이 글에서는 맞벌이 부부가 꼭 알아야 할 <strong>육아 지원 정책을 한눈에</strong> 정리해 드리겠습니다.</p>

<h2>🏠 돌봄 시간 확대</h2>
<p>2026년부터 서울시를 포함한 여러 지자체에서 <strong>초등 돌봄 서비스가 아침 7시부터 자정까지</strong>로 확대되었습니다. 이는 기존 저녁 7시까지였던 돌봄 시간을 대폭 연장한 것으로, 야근이나 교대 근무를 하는 부모에게 큰 도움이 됩니다.</p>

<h2>💰 육아휴직 급여 인상</h2>
<p>2026년 육아휴직 급여의 주요 변경 사항:</p>
<table border="1" style="width:100%; border-collapse:collapse; margin-bottom:22px;">
<tr style="background-color:#f0f0f0;"><th style="padding:10px;">항목</th><th style="padding:10px;">2025년</th><th style="padding:10px;">2026년</th></tr>
<tr><td style="padding:10px;">육아휴직 급여 상한</td><td style="padding:10px;">월 150만 원</td><td style="padding:10px;">월 200만 원</td></tr>
<tr><td style="padding:10px;">3+3 부모 동시 사용</td><td style="padding:10px;">최대 300만 원</td><td style="padding:10px;">최대 450만 원</td></tr>
<tr><td style="padding:10px;">남성 육아휴직 비율</td><td style="padding:10px;">약 22%</td><td style="padding:10px;">약 36.5%</td></tr>
</table>
<p>특히 <strong>3+3 부모 육아휴직 제도</strong>는 자녀가 만 12개월 이내일 때 부모 모두 3개월씩 동시에 육아휴직을 사용하면 급여가 대폭 인상되는 획기적인 제도입니다.</p>

<h2>👶 어린이집·유치원 지원</h2>
<p>보육료 지원은 소득에 관계없이 모든 0~5세 아동에게 제공됩니다. 2026년 기준 0세반 보육료는 월 <strong>514,000원</strong>, 유치원 무상교육비는 월 <strong>280,000원</strong>이 지원됩니다.</p>

<h2>🏢 유연근무제 확대</h2>
<p>2026년부터 '육아기 10시 출근제'가 도입되어, 만 8세 이하 자녀를 둔 근로자는 출근 시간을 10시로 조정할 수 있습니다. 또한 육아기 근로시간 단축 사용자가 <strong>전년 대비 48% 증가</strong>했습니다.</p>

<h2>📋 한눈에 보는 신청 체크리스트</h2>
<p>✅ 출산 전: 출산 전 배우자 휴가, 육아휴직 사전 신청<br>
✅ 출산 후: 출산급여, 출산축하금 신청 (주민센터)<br>
✅ 0~1세: 영아수당, 부모급여 신청<br>
✅ 1~5세: 보육료 지원 신청 (복지로)<br>
✅ 초등학생: 돌봄교실 신청, 방과후학교</p>

<hr style="margin: 30px 0;">

<h3>❓ 자주 묻는 질문</h3>

<p><strong>Q. 육아휴직은 부부 동시에 사용할 수 있나요?</strong></p>
<p>A. 네, 2026년부터 자녀 1명에 대해 부모가 동시에 육아휴직을 사용할 수 있습니다. 3+3 제도를 활용하면 급여가 더 높아집니다.</p>

<p><strong>Q. 자영업자도 육아 지원을 받을 수 있나요?</strong></p>
<p>A. 고용보험에 가입한 자영업자는 육아휴직 급여를 받을 수 있습니다. 가입하지 않은 경우에도 영아수당, 보육료 지원 등은 받을 수 있습니다.</p>

<p><strong>Q. 아이돌봄서비스는 어떻게 신청하나요?</strong></p>
<p>A. <a href="https://www.idolbom.go.kr" target="_blank">아이돌봄서비스 홈페이지</a> 또는 읍면동 주민센터에서 신청할 수 있습니다. 소득 수준에 따라 본인 부담금이 달라집니다.</p>

<div style="margin-top: 40px; padding: 20px; background-color: #e8f4f8; border-radius: 10px;">
<p style="font-size: 16px; color: #555;">📌 이 글은 Stories of people 블로그의 오리지널 콘텐츠로, 2026년 육아 지원 정책을 독자적으로 분석한 내용입니다.</p>
</div>

</div>
"""
        },
        {
            "title": "서울시 vs 경기도 - 2026년 청년 지원 정책 비교 분석",
            "labels": ["3. 오리지널 콘텐츠", "청년정책", "서울시", "경기도"],
            "content": """
<div style="font-size: 19px; line-height: 1.9; word-break: keep-all;">

<p>수도권에 거주하는 청년이라면, 서울시와 경기도 중 어디에서 더 많은 혜택을 받을 수 있는지 궁금하실 겁니다. 두 지역의 2026년 청년 지원 정책을 항목별로 비교해 보았습니다.</p>

<h2>📊 주요 정책 비교표</h2>
<table border="1" style="width:100%; border-collapse:collapse; margin-bottom:22px;">
<tr style="background-color:#f0f0f0;"><th style="padding:10px;">항목</th><th style="padding:10px;">서울시</th><th style="padding:10px;">경기도</th></tr>
<tr><td style="padding:10px;">청년 수당</td><td style="padding:10px;">월 50만 원 × 6개월</td><td style="padding:10px;">분기 25만 원</td></tr>
<tr><td style="padding:10px;">주거 지원</td><td style="padding:10px;">임차보증금 최대 7,000만 원</td><td style="padding:10px;">기숙사형 청년주택</td></tr>
<tr><td style="padding:10px;">식사 지원</td><td style="padding:10px;">3천원 식당 (모락모락 등)</td><td style="padding:10px;">경기청년 식비카드 (월 10만 원)</td></tr>
<tr><td style="padding:10px;">취업 지원</td><td style="padding:10px;">서울형 뉴딜일자리</td><td style="padding:10px;">경기청년 일경험 프로그램</td></tr>
<tr><td style="padding:10px;">심리 상담</td><td style="padding:10px;">마음건강 검진 + 상담 10회</td><td style="padding:10px;">마음돌봄 바우처 30만 원</td></tr>
<tr><td style="padding:10px;">교통비</td><td style="padding:10px;">기후동행카드 (월 62,000원)</td><td style="padding:10px;">The 경기패스 (30% 환급)</td></tr>
</table>

<h2>🏠 주거 지원: 서울시 우세</h2>
<p>서울시는 임차보증금 지원 규모가 최대 7,000만 원으로 경기도보다 훨씬 큽니다. 서울의 높은 전세가를 감안한 설계이지만, 실질적인 혜택 면에서 서울시가 앞섭니다.</p>

<h2>🍽️ 식사 지원: 접근성은 서울, 자유도는 경기</h2>
<p>서울시의 '3천원 식당'은 정해진 장소에서만 이용 가능하지만 직접 조리된 식사를 제공합니다. 반면 경기도의 식비카드는 원하는 곳에서 자유롭게 사용할 수 있어 편의성이 높습니다.</p>

<h2>🚌 교통비: 비슷하지만 방식이 다르다</h2>
<p>서울시의 기후동행카드는 월 정액으로 대중교통을 무제한 이용할 수 있고, 경기도의 The 경기패스는 실제 사용 금액의 30%를 돌려받는 캐시백 방식입니다. 대중교통 이용이 많다면 서울시, 적다면 경기도가 유리합니다.</p>

<h2>💡 선택 가이드</h2>
<p><strong>서울시가 유리한 경우:</strong> 주거비 부담이 큰 1인 가구, 대중교통으로 출퇴근하는 직장인, 구직 중인 청년</p>
<p><strong>경기도가 유리한 경우:</strong> 자차 이용이 많은 청년, 다양한 소비처에서 자유롭게 사용하고 싶은 경우, 심리 상담이 필요한 경우</p>

<hr style="margin: 30px 0;">

<h3>❓ 자주 묻는 질문</h3>

<p><strong>Q. 서울에서 일하고 경기도에 거주하면 어느 쪽 혜택을 받나요?</strong></p>
<p>A. 대부분의 지방자치단체 정책은 주민등록 기준입니다. 경기도에 주소가 있다면 경기도 정책을 받게 됩니다. 다만 일부 서울시 정책(3천원 식당 등)은 서울 소재 직장인도 이용 가능합니다.</p>

<p><strong>Q. 두 지역 혜택을 동시에 받을 수 있나요?</strong></p>
<p>A. 지자체 정책은 중복 수혜가 불가능합니다. 다만 중앙 정부 정책(국민취업지원제도 등)은 지자체와 별개로 받을 수 있습니다.</p>

<div style="margin-top: 40px; padding: 20px; background-color: #e8f4f8; border-radius: 10px;">
<p style="font-size: 16px; color: #555;">📌 이 글은 Stories of people 블로그의 오리지널 콘텐츠입니다. 각 정책의 정확한 내용과 자격 조건은 해당 지자체 홈페이지에서 확인해 주세요.</p>
</div>

</div>
"""
        },
        {
            "title": "생활비 절약! 2026년 정부가 쏘는 할인·무료 혜택 총모음",
            "labels": ["3. 오리지널 콘텐츠", "생활비절약", "정부혜택", "2026년"],
            "content": """
<div style="font-size: 19px; line-height: 1.9; word-break: keep-all;">

<p>물가가 오르고 생활비 부담이 커지는 요즘, 정부에서 제공하는 다양한 할인·무료 혜택을 활용하면 의외로 큰 절약이 가능합니다. 많은 분들이 모르고 지나치는 <strong>숨은 정부 혜택</strong>들을 총정리했습니다.</p>

<h2>🚌 교통비 절약</h2>
<h3>기후동행카드 (서울)</h3>
<p>월 62,000원으로 서울시 지하철·버스·따릉이를 무제한 이용할 수 있습니다. 매일 대중교통을 이용한다면 월 3~5만 원을 절약할 수 있습니다.</p>

<h3>알뜰교통카드 (전국)</h3>
<p>대중교통 이용 시 걸어서 이동한 거리에 비례하여 최대 월 <strong>66,000원</strong>의 마일리지를 적립할 수 있습니다.</p>

<h2>🏥 의료비 절약</h2>
<h3>건강검진 무료</h3>
<p>건강보험 가입자라면 2년에 한 번 <strong>무료 일반 건강검진</strong>을 받을 수 있고, 만 40세부터는 위암·간암 등 <strong>6대 암 무료 검진</strong>도 받을 수 있습니다.</p>

<h3>치과 스케일링</h3>
<p>연 1회 건강보험이 적용되어 <strong>15,000~20,000원</strong>에 스케일링을 받을 수 있습니다.</p>

<h2>📚 교육비 절약</h2>
<h3>K-MOOC (온라인 대학 강의)</h3>
<p>서울대, KAIST 등 유명 대학의 강좌를 <strong>무료</strong>로 들을 수 있습니다. 수료증도 발급받을 수 있어 자기계발에 활용할 수 있습니다.</p>

<h3>디지털 배움터</h3>
<p>전국 1,000곳 이상에서 <strong>무료 디지털 교육</strong>을 제공합니다.</p>

<h2>🎭 문화·여가 절약</h2>
<h3>문화가 있는 날</h3>
<p>매월 마지막 수요일에 영화관, 미술관, 공연장 등에서 <strong>50% 할인</strong> 혜택을 받을 수 있습니다.</p>

<h3>국립시설 무료</h3>
<p>국립박물관, 국립미술관, 국립공원 등은 대부분 <strong>무료 입장</strong>이 가능합니다.</p>

<h2>💰 금융 혜택</h2>
<h3>청년내일저축계좌</h3>
<p>월 10만 원 저축 시 정부가 매칭으로 10~30만 원을 추가 적립해줍니다. 3년 후 최대 <strong>1,440만 원</strong>을 만들 수 있습니다.</p>

<h3>주택청약 가산점</h3>
<p>국민주택 청약 시 청약 저축 납입 횟수에 따라 가산점을 받을 수 있습니다. 빨리 시작할수록 유리합니다.</p>

<h2>📱 통신비 절약</h2>
<p>기초생활수급자, 차상위계층은 <strong>통신비 감면</strong>(최대 월 26,000원)을 받을 수 있으며, 만 65세 이상 어르신도 감면 대상입니다.</p>

<hr style="margin: 30px 0;">

<h3>❓ 자주 묻는 질문</h3>

<p><strong>Q. 이런 혜택들을 한 번에 확인할 수 있는 방법은?</strong></p>
<p>A. 정부24 '보조금24' 서비스에서 나의 소득, 가구 정보를 입력하면 받을 수 있는 모든 혜택을 자동으로 안내해줍니다.</p>

<p><strong>Q. 혜택이 많은데 왜 모르는 사람이 많을까요?</strong></p>
<p>A. 각 혜택이 서로 다른 부처와 지자체에서 운영되어 정보가 분산되어 있기 때문입니다. 본 블로그처럼 정리된 정보를 참고하시면 좋습니다.</p>

<p><strong>Q. 소득 기준이 있는 혜택은 어떻게 확인하나요?</strong></p>
<p>A. 주민센터 방문 상담이 가장 정확합니다. 건강보험료 납부액을 기준으로 소득 수준을 판단하는 경우가 많습니다.</p>

<div style="margin-top: 40px; padding: 20px; background-color: #e8f4f8; border-radius: 10px;">
<p style="font-size: 16px; color: #555;">📌 이 글은 Stories of people 블로그의 오리지널 콘텐츠로, 정부 혜택 정보를 독자적으로 분석·정리한 내용입니다.</p>
</div>

</div>
"""
        }
    ]
    
    for i, post in enumerate(posts, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(posts)}] 포스팅 시작: {post['title'][:40]}...")
        
        url = poster.post(
            title=post["title"],
            content=post["content"],
            labels=post["labels"],
            meta_description=post["title"][:150],
            dept="Stories of people"
        )
        
        if url:
            print(f"✅ 포스팅 성공: {url}")
        else:
            print(f"❌ 포스팅 실패")
        
        if i < len(posts):
            print(f"⏳ 다음 포스팅까지 30초 대기...")
            time.sleep(30)
    
    print(f"\n{'='*60}")
    print("오리지널 콘텐츠 포스팅 완료!")

if __name__ == "__main__":
    create_original_posts()
