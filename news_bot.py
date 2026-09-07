import os
import requests
import google.generativeai as genai

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 1. 완전히 바뀐 네이버 API 헤더 규격 적용
headers = {
    "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
    "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET
}

# 2. 완전히 바뀐 네이버 API 주소 적용 (경제 뉴스 3개, 최신순 정렬)
url = "https://naverapihub.apigw.ntruss.com/search/v1/news?query=경제&display=3&sort=date"
res = requests.get(url, headers=headers)

if res.status_code != 200:
    print(f"네이버 API 에러 발생: {res.text}")
    exit(1)

news_data = res.json()['items']

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

final_message = "☀️ 오늘의 아침 뉴스 브리핑\n\n"

for news in news_data:
    title = news['title'].replace("<b>", "").replace("</b>", "")
    link = news['link']
    description = news['description'].replace("<b>", "").replace("</b>", "")
    
    prompt = f"다음 기사 내용을 기본 3줄로 요약해 줘. 만약 사안이 중대하거나 복잡하면 최대 5~6줄까지 상세히 요약해도 돼:\n\n{description}"
    summary = model.generate_content(prompt).text
    
    final_message += f"📰 **{title}**\n{summary}\n🔗 링크: {link}\n\n"

requests.post(DISCORD_WEBHOOK_URL, json={"content": final_message})
print("디스코드 전송 완료!")
