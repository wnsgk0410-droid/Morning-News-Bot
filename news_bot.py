import requests
import google.generativeai as genai

# 1. 내 API 키 설정 (발급받은 키를 여기에 넣으세요)
NAVER_CLIENT_ID = "oo1rxhv1w1"
NAVER_CLIENT_SECRET = "Nyvxhf96HuzEtF49P7ouw2IThs1IQRS9UwMmK3ZG"
GEMINI_API_KEY = "제미나이_API_키"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1546468573260550196/jMFs7BgEwBt5HEC9rfo691qx-V7xF5EOss9GAj4mbBAQiLnW2z-fbGrAaEbq1gxD2kdB"

# 2. 네이버 뉴스 검색하기 (예: '경제' 키워드로 3개 가져오기)
headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
res = requests.get("https://openapi.naver.com/v1/search/news.json?query=경제&display=3", headers=headers)
news_data = res.json()['items']

# 3. Gemini로 요약하기
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

final_message = "☀️ 오늘의 아침 뉴스 브리핑\n\n"

for news in news_data:
    title = news['title'].replace("<b>", "").replace("</b>", "")
    link = news['link']
    description = news['description'].replace("<b>", "").replace("</b>", "")
    
    # 프롬프트: 중요도에 따라 개수를 유연하게 조절하라고 지시!
    prompt = f"다음 기사 내용을 기본 3줄로 요약해 줘. 만약 사안이 중대하거나 복잡하면 최대 5~6줄까지 상세히 요약해도 돼:\n\n{description}"
    summary = model.generate_content(prompt).text
    
    final_message += f"📰 **{title}**\n{summary}\n🔗 링크: {link}\n\n"

# 4. 디스코드로 보내기
requests.post(DISCORD_WEBHOOK_URL, json={"content": final_message})
print("디스코드 전송 완료!")