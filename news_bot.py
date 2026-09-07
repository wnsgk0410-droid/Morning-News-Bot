import os
import requests
import google.generativeai as genai

# 금고(환경 변수)에서 키를 꺼내오는 코드입니다.
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- 이 아래는 이전 코드와 동일합니다 ---
headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
res = requests.get("https://openapi.naver.com/v1/search/news.json?query=경제&display=3", headers=headers)
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