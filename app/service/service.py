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

def getTodayWeather(area):
    
    source = requests.get("https://search.daum.net/search?q="+area+"%20날씨",headers=headers)
    soup = BeautifulSoup(source.content,"html.parser")
    
    cont_today = soup.find("div",{"class":"cont_today"})
    desc_temp = (cont_today.select("div.info_temp div span span > span"))[0].text
    now_temp = (cont_today.select("div.info_temp div span span > strong"))[0].text
    txt_desc = (cont_today.select("div.info_temp > p"))[0].text
    wind = (cont_today.select("dl.dl_weather > dt"))[0].text + " " + (cont_today.select("dl.dl_weather > dd"))[0].text
    humidity = (cont_today.select("dl.dl_weather > dt"))[1].text + " " + (cont_today.select("dl.dl_weather > dd"))[1].text
    fine_dust = (cont_today.select("dl.dl_weather > dt"))[2].text + " " + (cont_today.select("dl.dl_weather > dd"))[2].text

    area_hourly = soup.find("div",{"class":"area_hourly"})
    print(area_hourly)
    weather_hourly =  [item.select_one(".ico_wtws").text for item in area_hourly.select("ul.list_hourly > li")]
    area_rain = soup.find("div",{"class":"area_rain"})
    rain_hourly = [item.select_one(".txt_emph").text.strip() for item in area_rain.select("ul.list_hourly > li")]
    area_wind = soup.find("div",{"class":"area_wind"})
    wind_hourly = [item.select_one(".txt_num").text for item in area_wind.select("ul.list_hourly > li")]
    wind_direct_hourly = [item.select_one(".ico_wind").text for item in area_wind.select("ul.list_hourly > li")]
    area_damp = soup.find("div",{"class":"area_damp"})
    damp_hourly = [item.select_one(".txt_num").text for item in area_damp.select("ul.list_hourly > li")]
    
    data_hourly = ""
    for i in range (0, len(weather_hourly)):
        data_hourly = data_hourly + f"{str(i)}시:{weather_hourly[i]} / 강수확률({rain_hourly[i]}) / 습도({damp_hourly[i]}) / {wind_direct_hourly[i]}({wind_hourly[i]})\n"

    
    area_tab = soup.find("div",{"class":"tab_region"})
    local_area = [item.text for item in area_tab.select("ul.list_tab > li")]
    local_area = " ".join([item.strip() for item in local_area if item.strip() not in ["전국", "시·군·구", "읍·면·동"] and not item.strip().startswith("다른")])

    res = f"""[{area} 날씨 정보]
위치: {local_area}
온도: {now_temp} 
날씨: {desc_temp} ({txt_desc})   
{wind} | {humidity} | {fine_dust}

{data_hourly}
*(출처 : 다음날씨)
"""
    return res
    
def getTomorrowWeather(area):
    
    source = requests.get("https://search.daum.net/search?q="+"내일%20"+area+"%20날씨",headers=headers)
    soup = BeautifulSoup(source.content,"html.parser")
    
    cont_tomorrow = soup.find("div",{"class":"cont_tomorrow"})
    am_weather = (cont_tomorrow.select("div.info_tomorrow span.tit_ampm > span.txt_weather"))[0].text
    am_temp = (cont_tomorrow.select("div.info_tomorrow span.desc_temp > strong.txt_temp"))[0].text
    pm_weather = (cont_tomorrow.select("div.info_tomorrow span.tit_ampm > span.txt_weather"))[1].text
    pm_temp = (cont_tomorrow.select("div.info_tomorrow span.desc_temp > strong.txt_temp"))[1].text
    
    print(am_weather)
    print(am_temp)
    print(pm_weather)
    print(pm_temp)
    
    area_hourly = soup.find("div",{"class":"area_hourly"})
    weather_hourly =  [item.select_one(".ico_nws").text for item in area_hourly.select("ul.list_hourly > li")]
    area_rain = soup.find("div",{"class":"area_rain"})
    rain_hourly = [item.select_one(".txt_emph").text.strip() for item in area_rain.select("ul.list_hourly > li")]
    area_wind = soup.find("div",{"class":"area_wind"})
    wind_hourly = [item.select_one(".txt_num").text for item in area_wind.select("ul.list_hourly > li")]
    wind_direct_hourly = [item.select_one(".ico_wind").text for item in area_wind.select("ul.list_hourly > li")]
    area_damp = soup.find("div",{"class":"area_damp"})
    damp_hourly = [item.select_one(".txt_num").text for item in area_damp.select("ul.list_hourly > li")]
    
    data_hourly = ""
    for i in range (0, len(weather_hourly)):
        data_hourly = data_hourly + f"{str(i)}시:{weather_hourly[i]} / 강수확률({rain_hourly[i]}) / 습도({damp_hourly[i]}) / {wind_direct_hourly[i]}({wind_hourly[i]})\n"

    
    area_tab = soup.find("div",{"class":"tab_region"})
    local_area = [item.text for item in area_tab.select("ul.list_tab > li")]
    local_area = " ".join([item.strip() for item in local_area if item.strip() not in ["전국", "시·군·구", "읍·면·동"] and not item.strip().startswith("다른")])

    res = f"""[내일 {area} 날씨 정보]
위치: {local_area}
오전: {am_weather}({am_temp})
오후: {pm_weather}({pm_temp})

{data_hourly}
*(출처 : 다음날씨)
"""
    return res

def getOverseasWeather(area):
    
    source = requests.get("https://search.daum.net/search?q="+area+"%20날씨",headers=headers)
    soup = BeautifulSoup(source.content,"html.parser")
    
    area_today = soup.find("div",{"class":"area_today"})

    now_temp = (area_today.select("div.today_item > em.num_avg"))[0].text
    txt_info = (area_today.select("div.today_item div.wrap_txt > span.txt_info"))[0].text.strip()
    txt_time = (area_today.select("div.today_item div.wrap_txt > span.txt_time"))[0].text.strip()
    wind = (area_today.select("div.today_item dl > dt"))[0].text + " " + (area_today.select("div.today_item dl > dd"))[0].text
    humidity = (area_today.select("div.today_item dl > dt"))[1].text + " " + (area_today.select("div.today_item dl > dd"))[1].text
    fine_dust = (area_today.select("div.today_item dl > dt"))[2].text + " " + (area_today.select("div.today_item dl > dd"))[2].text

    area_hourly = soup.find("div",{"class":"area_hourly"})
    time_list = [item.select_one(".txt_time").text for item in area_hourly.select("ul.list_hourly > li")]
    weather_hourly =  [item.select_one(".ico_wtws").text for item in area_hourly.select("ul.list_hourly > li")]
    area_rain = soup.find("div",{"class":"area_rain"})
    rain_hourly = [item.select_one(".txt_emph").text.strip() for item in area_rain.select("ul.list_hourly > li")]
    area_wind = soup.find("div",{"class":"area_wind"})
    wind_hourly = [item.select('span')[-1].text for item in area_wind.select("ul.list_hourly > li")]
    wind_direct_hourly = [item.select_one(".ico_wind").text for item in area_wind.select("ul.list_hourly > li")]
    area_damp = soup.find("div",{"class":"area_damp"})
    damp_hourly = [item.select('span')[-1].text for item in area_damp.select("ul.list_hourly > li")]
    
    data_hourly = ""
    for i in range (0, len(weather_hourly)):
        data_hourly = data_hourly + f"{time_list[i]}:{weather_hourly[i]} / 강수확률({rain_hourly[i]}) / 습도({damp_hourly[i]}) / {wind_direct_hourly[i]}({wind_hourly[i]})\n"

    
    area_tab = soup.find("div",{"class":"tab_comp tab_tree"})
    local_area = [item.text for item in area_tab.select("ul.list_tab.list_opt > li")]
    local_area = " ".join([item.strip() for item in local_area if item.strip() not in ["전국", "시·군·구", "읍·면·동"] and not item.strip().startswith("다른")])

    res = f"""[{area} 날씨 정보]
위치: {local_area}
온도: {now_temp} 
날씨: {txt_info} ({txt_time})   
{wind} | {humidity} | {fine_dust}

{data_hourly}
*(출처 : 다음날씨)
"""
    return res

def getLottery(sender, num):
    if num > 10: num=10
    lotto_numbers = []
    for i in range(0,num):
        lotto_numbers.append(sorted(random.sample(range(1, 46), 6)))
    print(lotto_numbers)
    res = f'''{sender}님을 위한 로또 추천번호!\n\n'''
    
    for index,item in enumerate(lotto_numbers):
        res = res + f"번호 {str(index+1)}: {item}\n"
    
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
    for i in range(0,3):
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
    source = requests.get("https://search.naver.com/search.naver?where=news&sm=tab_jum&query=" + keyword,headers=headers)
    soup = bs4.BeautifulSoup(source.content,"html.parser")
    news_list = soup.find(class_="list_news")
    news_company = news_list.select("div.info_group > a.info.press")
    news_title = news_list.select("div > a.news_tit")
    
    res =f"""[\"{keyword.replace("+"," ")}\" 관련 뉴스 검색 결과]
    
"""
    for i in range(0,len(news_company)):
        res = res + str(i+1) + ". "+news_title[i].text + " / "+news_company[i].text + "\n"+news_title[i].get('href')
        res = res + "\n\n"
    res = res+"(출처 : 네이버뉴스)"
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
    zodiac_list = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    url = "https://i.sazoo.com/run/free/ddi_newyear/result.php?idx="+str(zodiac_list.index(keyword))
    driver.get(url) 
    html_source = driver.page_source
    soup = BeautifulSoup(html_source,"html.parser",from_encoding='cp949')
    
    total_luck = soup.find_all("li",{"class":"center"})[0].text
    
    byAge = soup.find_all("li",{"class":"center"})[1]
    byAge = byAge.get_text("\n\n", strip=True)
    print(byAge)
    
    now = datetime.now()
    # 원하는 형식으로 포맷팅
    formatted_now = now.strftime("%Y년 %m월 %d일")
    
    res = f"""[{formatted_now} {keyword} 운세]

(총평)
{total_luck}    
(나이별)
{byAge}

(출처 : 사주닷컴)
"""
    return res

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
    rest_address = soup.find_all("div","addr")
    rest_link = soup.find_all("a","moreview")

    res = f"""['{area.replace("+"," ")} 맛집' 카카오맵 검색 결과]\n\n"""
    
    count = len(rest_names) if len(rest_names) < 10 else 10
    for i in range(0,count):
        res = res + f"{str(i+1)}. {rest_names[i].text}({rest_sub[i].text})\n주소: {rest_address[i].p.text} \n링크: {rest_link[i].get('href')}\n\n"
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
    
    total_count = sum(result.cnt for result in results)
    max_count = max(result.cnt for result in results)
    min_count = min(result.cnt for result in results)
    level_range = max_count - min_count
    
    res = f"[{room}]채팅방의 채팅순위입니다.\n총 채팅 갯수 : {total_count}개\n\n"
    for index, result in enumerate(results):
        level = round(((result.cnt - min_count) / level_range) * 9) + 1
        res += f"{index+1}위 {result.sender} - 채팅 {result.cnt}개 ({result.cnt/total_count*100:.1f}% Lv.{level})\n\n"
    
    return res.strip()

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
    res = res+"\n(출처 : 네이버증권)"
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

def getHanRiverTemp():
    
    driver.get("https://hangang.ivlis.kr/") 
    time.sleep(1)
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    
    section = soup.find("div",{"class":"title-desc"})
    river_temp = section.select("div.title-desc > h1")
    sentence = section.select("div.title-desc > h4")    
    
    res = f"""[현재 한강물 온도]

온도 : {river_temp[0].text}
{sentence[0].text}
"""
    return res
    
def getSorry():
    apology_sentences = [
        "진심으로 사과드립니다. 실수를 반성하고 더 나은 방향으로 나아가겠습니다.",
        "말로는 다 할 수 없는 미안한 마음을 사과로 전합니다.",
        "지나간 일에 대해 깊이 뉘우치며 진심으로 사죄의 말씀을 드립니다.",
        "당신께 정중히 고개 숙여서 사과의 말씀을 전하고자 합니다.",
        "속 깊은 곳에서 나오는 진심 어린 사과의 말씀입니다.",
        "저의 부주의로 인해 상처를 드렸음에 대해 깊이 반성하며 송구스럽게도 사과드립니다.",
        "사람은 실수할 수밖에 없지만, 그 실수를 인정하고 책임질 줄 아는 자세로 정중한 사과를 드리겠습니다.",
        "마음이 아프시겠지만, 제 진심 어린 송구와 함께 겸허한 사과의 말씀을 전합니다.",
        "당신께 헌신하는 마음에서 비롯된 작은 실수에 대하여 진심으로 송구하며 참회하는 말씀입니다.",
        "상대방을 배려하지 못한 행동에 대하여 스스로 반성하고 죄송함을 표현하기 위해 이 자리를 빌리게 되었습니다.",
        "내 잘못인 걸 알면서도 당신께 참회와 변명 없는 진심어린 사과의 말씀을 전합니다.",
        "불미스러운 일로 인해 상처입힌 것에 대하여 깊이 후회하며 당당한 자세로 고개 숙여서 송구드립니다.",
        "상대방께 예상치 못한 아픔을 안겨드려 대단히 죄송합니다",
        "제가 저지른 잘못에 기인한 모든 상황들이 해결될 수 있길 바라며 마음속에서 영원한 용서와 감사함을 담아낼 때까지 기다리겠습니다",
        "제가 지난 시간 동안 보여준 모습들 때문에 주변분들께 힘이 될 수 있는 가치있는 시간들 보내기 위해서 최선을 다할 것임을 약속드리며 마음속으로도 다시 한 번 죄송합니다.",
        "나태와 부주의함으로 당신을 이런 지친 모습으로 만든 것 같아 너무나 미안합니다."
    ]
    res = random.choice(apology_sentences)
    return res
    
def getThanks():
    thankful_sentences = [
        "진심으로 감사드립니다. 정말로 도움이 되었습니다.",
        "너무나 고맙다는 말로 표현할 수 없을 만큼 감사합니다.",
        "정말로 감사합니다! 너무 큰 도움이 되었습니다.",
        "고맙다는 말로 다 표현할 수 없을 정도로 감사드립니다.",
        "너무나 소중한 도움에 진심으로 감사의 말씀을 전합니다.",
        "정말 고맙습니다! 이렇게 큰 도움을 주셔서 정말 감사합니다.",
        "강력하게 고맙다는 말씀을 전하고 싶습니다!",
        "진심으로 감사드리며, 저에게 주신 선물에 대해 깊은 사례를 드립니다.",
        "소중한 시간과 노력에 대해 깊은 존경과 감사의 마음을 전합니다.",
        "정말 감사합니다! 이런 큰 호의를 받아서 영원히 잊지 않겠습니다.",
        "너무나 소중한 선물에 대해 진심으로 고개 숙여서 감사의 인사를 드립니다.",
        "비록 제가 할수잇는 일들보단 한참 못하지만 제가 할수 있는 최대한의 만큼 보답 하겠습니다",
        "당신의 도움으로 마음이 따뜻해지고, 감사의 빛이 내 삶을 비추어 줍니다.",
        "감사는 마음을 풍요롭게 만들어주는 신비한 힘이며, 그 힘은 당신에게서 얻어갑니다.",
        "나에게 미소를 선물해준 당신께 깊은 감사를 드리며, 그 미소가 영원토록 가득하길 바랍니다.",
        "당신과 함께한 순간들은 곧 나에게 오는 행운의 시작이었습니다. 진심으로 감사드립니다.",
        "세상에 단 하나뿐인 당신께 감사를 드리며, 이 작은 말 한마디로도 내 마음을 전할 수 없다는 것을 알고 있습니다."
    ]
    res = random.choice(thankful_sentences)
    return res

def getOut(name):
    res = f"{name}님을 강퇴하려고 하였으나, 영험한 힘이 그를 보호하였습니다\U0001F607"
    return res

def getHentai():
    res = f"변태새끼."
    return res

def getSuicide(sender):
    
    dead_list =["과로사","뇌졸중","복상사","심장마비","자기색정사",
                "감전사","과다출혈","교통사고","동사","방사선피폭",
                "의료사고","압사","질식사","추락사","실족사","폭사",
                "폭행치사","자연재해","아사","고독사","뇌사","자살",
                "타살","전사","즉사","객사","심장사","병사","자연사",
                "익사","요절","교사","낙사","참수","추살","폭사","척살",
                "급사","독사","괴사","수장"
            ]
    res = f"{sender}님께 어울리는 죽음은 [{random.choice(dead_list)}]입니다!\U0001F92A"
    return res

def getMelonChart():
    url = "https://www.melon.com/chart/index.htm"
    driver.get(url) 
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    now = datetime.now() - timedelta(days=1)
    formatted_now = now.strftime("%Y.%m.%d")
    title = soup.find_all("div",{"class":"ellipsis rank01"})
    title_list = [item.select_one("span > a").text for item in title]
    artist = soup.find_all("div",{"class":"ellipsis rank02"})
    artist_list = [item.select_one("span > a").text for item in artist]

    res = f"[{formatted_now} 멜론 차트100\U0001F3B5]\n\n"
    for i in range(0,len(title_list)):
        res = res + f"{str(i+1)}. {title_list[i]} - {artist_list[i]}\n"
    res = res+"(출처 : Melon)"
    return res

def getMovieList():
    url = "https://www.megabox.co.kr/movie"
    driver.get(url) 
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    now = datetime.now() - timedelta(days=1)
    formatted_now = now.strftime("%Y.%m.%d")
    movie_list = soup.find("ol",{"class":"list"})
    print(movie_list)
    movie_title = movie_list.select("li > div.tit-area")
    title = [item.select_one("p.tit").text for item in movie_title] 
    movie_rate = movie_list.select("li > div.rate-date")
    rate = [item.select_one("span.rate").text for item in movie_rate]
    date = [item.select_one("span.date").text for item in movie_rate]
    

    res = f"[{formatted_now} 현재상영작\U0001F3A5]\n\n"
    for i in range(0,len(title)):
        res = res + f"{str(i+1)}. {title[i]} | {rate[i]} | {date[i]}\n"
    res = res+"(출처 : 메가박스)"
    return res
    