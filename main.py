import requests
from datetime import date, timedelta
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_KEY = "R13FI6MO75DO5JNP"
NEWS_KEY = "c32e828a021b4fb49e3038fd12acb62e"


def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate


def calculate_stock_difference(yesterday_stock_data: dict, weekday_before_yesterday_data: dict):
    yesterday_close = float(yesterday_stock_data["4. close"])
    weekday_before_yesterday_close = float(weekday_before_yesterday_data["4. close"])
    stock_close_diff = yesterday_close - weekday_before_yesterday_close

    if stock_close_diff > 0:
        percentage_close = ((yesterday_close - weekday_before_yesterday_close) / weekday_before_yesterday_close) * 100
        return f"🔺 {STOCK} {round(percentage_close, 2)}%"
    elif stock_close_diff < 0:
        percentage_close = ((weekday_before_yesterday_close - yesterday_close) / weekday_before_yesterday_close) * 100
        return f"🔻 {STOCK} {round(percentage_close, 2)}%"


# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
yesterday_date = prev_weekday(date.today())
previous_weekday_date = prev_weekday(date.today() - timedelta(days=1))

stock_params = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : STOCK,
    "outputsize" : "COMPACT",
    "apikey" : STOCK_KEY
}
stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()

yesterday_stock_data = stock_data["Time Series (Daily)"][f"{yesterday_date}"]
day_before_yesterday_stock_data = stock_data["Time Series (Daily)"][f"{previous_weekday_date}"]
stock_percentage = calculate_stock_difference(yesterday_stock_data, day_before_yesterday_stock_data)


# Fetch the first 3 articles for the COMPANY_NAME.
news_params = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_KEY,
    "sortBy": "popularity"
}
news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()
news_data = news_response.json()
top_news = news_data["articles"][0:3]

sms_alert_msg = f"{stock_percentage} \n \n" \
                f"Top News: \n"
for news in top_news:
    sms_alert_msg += f"{news['source']['name']}: {news['title']} \n \n"

account_sid = 'ACb48e197753bdc7de17db72af186759fa'
auth_token = '44c2ee7848639c54605726c602349531'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  body=sms_alert_msg,
  to='whatsapp:+60176652940'
)

print(message.sid)
