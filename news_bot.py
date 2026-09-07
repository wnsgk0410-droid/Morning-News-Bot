import os
import requests
from google import genai

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

headers = {
    "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
    "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
}

# 1. 수집할 카테고리 설정 (종합뉴스, 경제, IT)
keywords = ["종합뉴스", "경제", "IT"]
collected_news = []
seen_links = set()

# 2. 날짜 필터링 없이, 지금 이 순간 가장 최신 뉴스들을 안전하게 수집
for keyword in keywords:
  url = f"https://naverapihub.apigw.ntruss.com/search/v1/news?query={keyword}&display=50&sort=date"
  res = requests.get(url, headers=headers)

  if res.status_code == 200:
    items = res.json().get("items", [])
    for item in items:
      link = item.get("link")
      if link in seen_links:
        continue
      seen_links.add(link)
      collected_news.append(item)
  else:
    print(f"네이버 API 에러 발생 ({keyword}): {res.text}")

print(f"최신 뉴스 총 {len(collected_news)}개 확보 완료")

# 3. 수집된 뉴스를 제미나이가 읽을 수 있는 텍스트로 병합
raw_news_text = ""
for idx, news in enumerate(collected_news, 1):
  title = news["title"].replace("<b>", "").replace("</b>", "")
  description = news["description"].replace("<b>", "").replace("</b>", "")
  pub_date = news.get("pubDate", "")
  raw_news_text += (
      f"[{idx}번 기사]\n발행일시: {pub_date}\n제목: {title}\n내용:"
      f" {description}\n\n"
  )

# 4. 제미나이 큐레이션 요청 (날짜 오류 방지 지침 추가)
client = genai.Client(api_key=GEMINI_API_KEY)

prompt = f"""
너는 최고급 수석 시사/경제 및 IT 뉴스 큐레이터야.
아래에 수집된 최신 뉴스 기사 총 {len(collected_news)}개가 있어. 
이 중에서 가장 중요하고 파급력 있는 핵심 이슈들을 분야별로 골고루 총 8~10개 엄선해서 종합 브리핑해 줘.

[엄격한 작성 규칙]
1. 절대 과거 년도(예: 2024년 등)의 지난 기사를 가져와서 오늘 일어난 일처럼 쓰지 말고, 제공된 데이터 중 **가장 최근에 보도된 실시간 주요 이슈** 위주로 다룰 것.
2. 각 뉴스는 반드시 글머리 기호(-)를 사용하여 딱 '3줄'로 핵심만 압축해서 요약할 것.
3. 뉴스 원문 링크나 URL은 절대 포함하지 말 것.
4. 비슷한 성격의 기사나 중복 이슈는 하나로 강력하게 통합할 것.
5. 3줄 요약이 끝난 후 줄을 바꾼 뒤, 반드시 '💡 인사이트:' 로 시작하여 이 이슈가 소프트웨어/AI 산업 트렌드나 개발자 업계에 미칠 영향이나 시사점을 1줄로 예리하게 분석할 것.
6. 디스코드에서 가독성이 좋도록 카테고리별로 섹션을 나누고 깔끔한 마크다운 형식을 사용할 것.

[수집된 뉴스 원본 데이터]
{raw_news_text}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash", contents=prompt
)

full_message = response.text

# 5. 글자 수 1900자 기준 스마트 분할 전송
chunk_size = 1900
messages = [
    full_message[i : i + chunk_size]
    for i in range(0, len(full_message), chunk_size)
]

for idx, msg in enumerate(messages, 1):
  header = (
      f"📰 **[아침 뉴스 브리핑 ({idx}/{len(messages)})]**\n\n"
      if len(messages) > 1
      else ""
  )
  payload = {"content": header + msg}
  requests.post(DISCORD_WEBHOOK_URL, json=payload)

print(f"디스코드 전송 완료! (총 {len(messages)}개 메시지 발송)")
