import os
import requests
from google import genai

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

headers = {
    "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
    "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET
}

# 1. AI가 비교하고 고를 수 있도록 뉴스를 넉넉하게 10개 가져옵니다.
url = "https://naverapihub.apigw.ntruss.com/search/v1/news?query=경제&display=10&sort=date"
res = requests.get(url, headers=headers)

if res.status_code != 200:
    print(f"네이버 API 에러 발생: {res.text}")
    exit(1)

news_data = res.json()['items']

# 2. 제미나이에게 한 번에 전달하기 위해 뉴스 10개를 하나의 텍스트로 묶습니다.
raw_news_text = ""
for idx, news in enumerate(news_data, 1):
    title = news['title'].replace("<b>", "").replace("</b>", "")
    description = news['description'].replace("<b>", "").replace("</b>", "")
    raw_news_text += f"[{idx}번 기사]\n제목: {title}\n내용: {description}\n\n"

# 3. 제미나이 호출
client = genai.Client(api_key=GEMINI_API_KEY)

# 💡 여기에 핵심 프롬프트(지시문)가 모두 들어갑니다.
prompt = f"""
너는 시사/경제 전문 뉴스 큐레이터야.
아래에 오늘 수집된 최신 뉴스 기사 10개가 있어. 이 중에서 가장 핵심적이고 중요한 뉴스 5개를 엄선해서 브리핑해 줘. 
단, 오늘 정말 중요한 이슈가 많다면 네 판단하에 6~7개까지 개수를 늘려도 좋아.

[작성 가이드라인]
1. 각 뉴스는 무조건 딱 '3줄'로만 요약해.
2. 뉴스 원문 링크나 URL은 절대 포함하지 마.
3. 중복되거나 비슷한 내용의 기사는 하나로 묶어서 요약해 줘.
4. 각 기사 요약 끝에 💡(인사이트) 이모지를 달고, 이 뉴스가 향후 소프트웨어/AI 산업 트렌드나 개발자 취업 시장에 미칠 수 있는 영향을 1줄로 덧붙여 줘.
5. 디스코드에서 읽기 좋게 깔끔한 마크다운과 이모지를 활용해 줘.

[오늘의 뉴스 후보]
{raw_news_text}
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

final_message = response.text

# 디스코드 메시지 글자 수 제한(2000자) 방지
if len(final_message) > 1900:
    final_message = final_message[:1900] + "\n\n...(내용이 길어 요약되었습니다)"

requests.post(DISCORD_WEBHOOK_URL, json={"content": final_message})
print("디스코드 전송 완료!")
