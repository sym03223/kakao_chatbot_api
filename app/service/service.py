import bs4, requests, random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np
import time
from app import db
from sqlalchemy.sql import func
from app.model.menues import menues
from app.model.chats import chats
import re
from pykrx import stock

headers = {"User-Agent":"mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/116.0.0.0 safari/537.36"}
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("window-size=1920x1080") # 화면크기(전체화면)
options.add_argument("disable-gpu") 
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
driver = webdriver.Chrome("C:\chromedriver116-win64\chromedriver-win64\chromedriver.exe", options=options)

# 속도 향상을 위한 옵션 해제



def getWeatherData(area):
    
    # 스크래핑 할 URL 세팅
    URL = "https://m.search.naver.com/search.naver?&query=" + area + "%20날씨"
    # 크롬 드라이버를 통해 지정한 URL의 웹 페이지 오픈
    driver.get(URL)
    # 페이지 소스 추출
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    
    check = soup.find_all("li",{"class":"sub_tab item"})
    

    if check[0].get("aria-selected")=="true":
        
        #현재기온
        now_temp = (soup.find("div",{"class":"temperature_text"})).strong.text[5:]
        #최고기온
        up_temp = (soup.find("span",{"class":"highest"})).text[4:]
        #최저기온
        down_temp = (soup.find("span",{"class":"lowest"})).text[4:]
        
        #요약
        summary = (soup.find("p",{"class":"summary"})).text.replace("  "," / ")
        
        summary_list = soup.find("dl",{"class":"summary_list"})
        #체감온도
        feel_temp = (summary_list.select("div.sort > dd"))[0].text
        #습도
        humidity = (summary_list.select("div.sort > dd"))[1].text
        #풍향
        wind_direction=(summary_list.select("div.sort > dt"))[2].text + " " +(summary_list.select("div.sort > dd"))[2].text
        
        chart = (soup.find("ul",{"class":"today_chart_list"})).text.strip()
        chart = chart.replace("     ","\n")
    
        res = f'''[{area} 날씨]
    
현재기온 : {now_temp}
최고 : {up_temp} | 최저 : {down_temp} | 체감 : {feel_temp}
습도 : {humidity} | 풍향 : {wind_direction}

{summary}

{chart}
'''
    else:
        if check[1].get("aria-selected")=="true":
            tomorrow_data = soup.find("ul",{"class":"weather_info_list _tomorrow"})
        elif check[2].get("aria-selected")=="true":
            tomorrow_data = soup.find("ul",{"class":"weather_info_list _after_tomorrow"})
            
        #오전
        am_temp = (tomorrow_data.select("div._am div div > strong")[0]).text[5:]
        am_info = (tomorrow_data.select("div._am div.temperature_info > p")[0]).text
        am_summary = (tomorrow_data.select("div._am div.temperature_info > dl")[0]).text.strip()
        print(am_temp)
        print(am_info)
        print(am_summary)
        
        #오후
        pm_temp = (tomorrow_data.select("div._pm div div > strong")[0]).text[5:]
        pm_info = (tomorrow_data.select("div._pm div.temperature_info > p")[0]).text
        pm_summary = (tomorrow_data.select("div._pm div.temperature_info > dl")[0]).text.strip()
        print(pm_temp)
        print(pm_info)
        print(pm_summary)
        
        
        dust = tomorrow_data.select("li > a")
        print(dust)
        print(dust[0].text)
        print(dust[1].text)
        print(dust[2].text)
        print(dust[3].text)
        print("dududududu")
        res = f'''[{area} 날씨]
<오전>    
날씨 : {am_info}
예측기온 : {am_temp} | {am_summary}
{dust[0].text} | {dust[1].text}

<오후>
날씨 : {pm_info}
예측기온 : {pm_temp} | {pm_summary}
{dust[2].text} | {dust[3].text}
'''
    return res
    
def getLottery(sender):
    lotto_numbers = random.sample(range(1, 46), 6)
    print(sorted(lotto_numbers))
    
    res = f'''"{sender}"님을 위한 로또 추천번호!

번호 : {sorted(lotto_numbers)}
'''
    
    return res

def googleSearch(keyword):
    link = "https://www.google.com/search?q="+keyword
    return link

def namuSearch(keyword):
    URL = "https://www.google.com/search?q="+keyword
    # 크롬 드라이버를 통해 지정한 URL의 웹 페이지 오픈
    driver.get(URL)
    html_source = driver.page_source
    soup_source = BeautifulSoup(html_source, 'html.parser')
    
    html = soup_source.find("div",{"class":"yuRUbf"})
    link = (html.select("div span > a")[0]).get("href")
    
    return link

def youtubeSearch(keyword):
    
    # 스크래핑 할 URL 세팅
    URL = "https://www.youtube.com/results?search_query=" + keyword
    # 크롬 드라이버를 통해 지정한 URL의 웹 페이지 오픈
    driver.get(URL)
    # 페이지 소스 추출
    html_source = driver.page_source
    soup_source = BeautifulSoup(html_source, 'html.parser')
    # 콘텐츠 모든 정보
    content_total = soup_source.find_all(class_ = 'yt-simple-endpoint style-scope ytd-video-renderer')
    # 콘텐츠 제목만 추출
    content_total_title = list(map(lambda data: data.get_text().replace("\n", ""), content_total))
    # 콘텐츠 링크만 추출
    content_total_link = list(map(lambda data: "https://youtube.com" + data["href"], content_total))
    
    res = f"""[\"{keyword.replace("+"," ")}\" 유튜브 검색 결과입니다.]"""
    res = res+"\n\n"
    for i in range(0,5):
        res = res + str(i+1)+". "+ content_total_title[i] + "\n" + content_total_link[i]
        res = res + "\n\n"
    
    return res.strip()


def getNews(keyword):
    
    
    url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1="+str(100+keyword)
    
    driver.get(url) 
    html_source = driver.page_source
    soup_source = BeautifulSoup(html_source, 'html.parser')
    
    snb = soup_source.find("td",{"class":"snb"})
    subject = snb.select("div.snb h2 > a")[0].text
    head = soup_source.find("ul",{"class":"sh_list"})
    headline = head.select("div.sh_text > a")
    
    now = datetime.now()
    # 원하는 형식으로 포맷팅
    formatted_now = now.strftime("%Y년 %m월 %d일 %H시 %M분")
    
    res = f"""[{subject} 분야 Top 10]
검색일시 : {formatted_now}
"""
    res = res + "\n\n"
    
    
    for index, news in enumerate(headline):
        res = res + str(index+1)+". " + news.text + "\n" + news.get('href')
        res = res + "\n\n"
    
    return res

def getNewsSearch(keyword):
    source = requests.get("https://search.naver.com/search.naver?where=news&sm=tab_jum&query=" + keyword)
    soup = bs4.BeautifulSoup(source.content,"html.parser")
    news_list = soup.find(class_="list_news")
    news_company = news_list.select("div.info_group > a.info.press")
    news_title = news_list.select("div > a.news_tit")
    
    res =f"""[\"{keyword.replace("+"," ")}\" 관련 뉴스 검색 결과]
    
"""
    for i in range(0,len(news_company)):
        res = res + str(i+1) + ". "+news_title[i].text + " / "+news_company[i].text + "\n"+news_title[i].get('href')
        res = res + "\n\n"
    
    return res.strip()
    

def realtime():
    
    url = "https://signal.bz/"
    driver.get(url) 
    html_source = driver.page_source
    soup_source = BeautifulSoup(html_source, 'html.parser')
    
    rank = soup_source.find("div",{"class":"realtime-rank"})

    rank_num = rank.find_all("span","rank-num")
    rank_text = rank.find_all("span","rank-text")
    now = datetime.now()
    # 원하는 형식으로 포맷팅
    formatted_now = now.strftime("%Y년 %m월 %d일 %H시 %M분")
    
    res=f"""[실시간 검색어 TOP 10]
검색일시 : {formatted_now}
"""
    res=res+"\n"
    
    for i in range(0, 10):
        res = res + rank_num[i].text+". "+rank_text[i].text+"\n"
    
    res = res + "\n(출처 : 시그널 실시간검색어)"
    return res.strip()

def getZodiac(keyword):
    url = "https://unse.daily.co.kr/?p=zodiac#unseback"
    source = requests.get(url, headers=headers)
    soup = BeautifulSoup(source.content,"html.parser",from_encoding='cp949')
    
    zodiac = soup.find("section",{"class":"container_zodiac"})
    zodiac_name = zodiac.find_all("b")
    zodiac_content = zodiac.find_all("p")
    
    now = datetime.now()
    # 원하는 형식으로 포맷팅
    formatted_now = now.strftime("%Y년 %m월 %d일")
    
    res = f"""[{formatted_now} {keyword} 운세]"""
    res = res + "\n\n"
    for i in range(0,len(zodiac_name)):
        if keyword == zodiac_name[i].text+"띠":
            res = res + zodiac_content[i].text
            break
    
    return res.strip()

def getHoroscope(keyword):
    url = "https://www.fortunade.com/unse/free/star/daily.php?gtype=2"
    source = requests.get(url, headers=headers)
    soup = BeautifulSoup(source.content,"html.parser",from_encoding='cp949')
    horoscope_commands = ["양","황소","쌍둥이","게","사자","처녀","천칭","전갈","사수","염소","물병","물고기"]
    scope = horoscope_commands.index(keyword) if keyword in horoscope_commands else None
    
    element = soup.find(id=f"result_{int(scope+1)}")
    contents = element.select("div.today_item > div.desc")[0]
    now = datetime.now()
    # 원하는 형식으로 포맷팅
    formatted_now = now.strftime("%Y년 %m월 %d일")
    
    res = f"""[{formatted_now} {keyword}자리 운세]

{contents.text}
"""
    
    
    
    return res
            
def getExchangeRate():
    source = requests.get("https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=환율", headers=headers)
    soup = bs4.BeautifulSoup(source.content,"html.parser")
    
    
    nation_name= list(map(lambda row: [th.text for th in row.find_all("th")], soup.find_all("tr")))
    price = list(map(lambda row: [td.text for td in row.find_all("td")], soup.find_all("tr")))
    price.pop(0)
    nation_name.pop(0)    
    res = """\U0001F4B2[환율 정보]\U0001F4B2\n\n"""
    
    for i in range(0, len(nation_name)):

        res = res + nation_name[i][0]+" : \U000020A9"+price[i][0]+"\n"
        
    res = res + "\n출처(네이버 환율)"        
    return res.strip()
    
def getAllCoins():
    import re
    
    url = "https://kr.investing.com/crypto/currencies?currency=krw"
    # url = "https://kr.investing.com/crypto/"
    driver.get(url) 
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    
    # title =soup.find_all("td","left bold elp name cryptoName first js-currency-name")
    # ticker = soup.find_all("td","left noWrap elp symb js-currency-symbol")
    # price = soup.find_all("td","price js-currency-price")
    title =soup.find_all("div","crypto-coins-table_cellNameText__aaXmK")
    ticker = soup.find_all("span","text-common-grey pt-0.5 text-xs")
    price = soup.find_all("td","datatable_cell__LJp3C datatable_cell--align-end__qgxDQ text-secondary !text-sm crypto-coins-table_thirdMobileCell__f8EsE")
    now = datetime.now()
    # 원하는 형식으로 포맷팅
    formatted_now = now.strftime("%m월 %d일 %H시 %M분")
    res = f"""[{formatted_now} \U000020BF 시세]"""
    res = res + "\n\n"
    
    for i in range(0,10):
        cleaned_number = re.sub(r"\.\d+", "", price[i].text)
        res = res + str(i+1)+ "." + (title[i].text).strip() + f"({ticker[i].text})"+f': {cleaned_number}\n'
        
    res = res + "\n(출처 : 인베스팅닷컴)"
    return res.strip()

def getRestaurantByArea(area):
    
    url = "https://map.kakao.com/?q="+area+"맛집"
    
    driver.get(url) 
    time.sleep(1)
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    
    rest_names = soup.find_all("a","link_name")
    rest_sub = soup.find_all("span","subcategory clickable")
    # open_time = soup.find_all("p","periodWarp")
    rest_link = soup.find_all("a","moreview")

    res = f"""['{area.replace("+"," ")} 맛집' 카카오맵 검색 결과]\n\n"""
    
    count = len(rest_names) if len(rest_names) < 10 else 10
    for i in range(0,count):
        res = res + f"{str(i+1)}. {rest_names[i].text}({rest_sub[i].text}) \n{rest_link[i].get('href')}\n\n"
    return res
    
def getVs(msgSplit,sender):
    print(msgSplit)
    random_choice = random.choice(msgSplit)
    res = f"""선택이 어려운 "{sender}"님을 위한 결과는~
[{random_choice.strip()}] 입니다!
"""
    return res

def getMapSearch(area):
    link = "https://map.naver.com/p/search/"+area
    return link

def getChatRank(room,sender):
    from sqlalchemy import desc  
    results = (
        db.session.query(chats.sender, func.count().label('cnt'))
        .filter(chats.room == room)
        .group_by(chats.sender)
        .order_by(desc('cnt'))
        .all()
    )
    res = f"[{room}]채팅방의 채팅순위입니다.\n\n"
    total_count = sum(result.cnt for result in results)
    max_count = max(result.cnt for result in results)
    min_count = min(result.cnt for result in results)
    level_range = max_count - min_count

    for index, result in enumerate(results):
        level = round(((result.cnt - min_count) / level_range) * 9) + 1
        res += f"{index+1}위 {result.sender} - 채팅 {result.cnt}개 ({result.cnt/total_count*100:.1f}% Lv.{level})\n\n"
    
    return res

def getMenu(sender):
    random_menu = db.session.query(menues).order_by(func.rand()).first()
    res=f"""\U00002728{sender}님\U00002728을 위한 추천메뉴!
[{random_menu.menu}] 어떠신가요?\U0001F61D
"""
    return res

def getRandomTest():
    contens_url = ["https://www.simcong.com/", "https://www.banggooso.com/"]
    
    url = random.choice(contens_url)
    
    source = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(source.content,"html.parser")
    res = ""
    if url == contens_url[0]:
        links = [item.a['href'] for item in soup.find_all('li', {'class': 'main_hot_item'})]
        get_one_link = random.choice(links)
        res = url+get_one_link
    elif url == contens_url[1]:
        feed_list = soup.find('ul', {'class': 'feed-list'})
        links = [item.a['href'] for item in feed_list.select("ul > li")]
        get_one_link = random.choice(links)
        if get_one_link.startswith("javascript"):
            res = extract_url(get_one_link)
        else:
            res = url+get_one_link
    return res

#문자열에서 링크만 추출
def extract_url(input_string):
    pattern = r'(https?://[^\s"\';]+)'
    url = re.search(pattern, input_string)
    if url:
        return url.group(0)
    else:
        return None

def getStockData(stock_name,sender):
    stock_code = get_stock_code(stock_name)
    if stock_code == 'none':
        return "존재하지 않는 종목입니다."
    
    url = "https://finance.naver.com/item/main.naver?code="+stock_code
    
    driver.get(url) 
    time.sleep(1)
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    today = soup.find('div', {'class':'rate_info'})
    
    down_emoji = "\U0001F4C9"
    up_emoji = "\U0001F4C8"
    now = datetime.now()
    formatted_now = now.strftime("%Y년 %m월 %d일 %H시 %M분")
    
    today_price = today.select("div p.no_today em > span ")
    today_price = ''.join([item.text for item in today_price])
    
    no_exday = today.select("div p.no_exday > em")
    
    if len(no_exday)>0:    
        no_exday_text1=(no_exday[0].text).replace("\n","")
        no_exday_text2=(no_exday[1].text).replace("\n","")
    else:
        no_exday_text1="정보없음"
        no_exday_text2="정보없음"
    
    no_exday_info=""
    
    
    if "상승" in no_exday_text1:
        no_exday_info = f"전일대비 {up_emoji}{no_exday_text1} | {no_exday_text2}"
    elif "하락" in no_exday_text1:
        no_exday_info = f"전일대비 {down_emoji}{no_exday_text1} | {no_exday_text2}"
    else:
        no_exday_info = f"전일대비 {no_exday_text1} | {no_exday_text2}"
    
    summary_info = soup.find('table', {'class':'no_info'})
    summary = summary_info.select("tbody tr td > em")
    highest = (summary[1].text).replace("\n","")
    lowest = (summary[4].text).replace("\n","")
    upper_limit = (summary[2].text).replace("\n","")
    lower_limit = (summary[6].text).replace("\n","")
    trading_volume = (summary[3].text).replace("\n","")
    transaction_amount = (summary[7].text).replace("\n","")
    print(upper_limit)
    print(lower_limit)
    
    	
    res=f"""\U0001F4B0[{stock_name}]의 실시간 주가정보!\U0001F4B0
현재시각 : {formatted_now}

시장가 : {today_price}원
등락율 : {no_exday_info}

고가 : {highest} (상한가:{upper_limit})
저가 : {lowest} (하한가:{lower_limit})
거래량 : {trading_volume}
거래대금 : {transaction_amount}백만
"""
    return res

#종목명 -> 종목코드
def get_stock_code(stock_name):
    now = datetime.now() - timedelta(days=1)
    formatted_now = now.strftime("%Y%m%d")
    
    df = stock.get_market_price_change(formatted_now, formatted_now ,market="ALL")
    row = df[df['종목명'] == stock_name]
    if len(row)==0:
        return "none"    
    else:
        stock_code = row.index[0]
    
    return stock_code
