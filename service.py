import bs4, requests, random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
import random
import pandas as pd

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

    #현재기온
    now_temp = (soup.find("div",{"class":"temperature_text"})).strong.text[5:]
    #최고기온
    up_temp = (soup.find("span",{"class":"lowest"})).text[4:]
    #최저기온
    down_temp = (soup.find("span",{"class":"highest"})).text[4:]
    
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
    
    res = f'''[현재 {area} 날씨]
    
현재기온 : {now_temp}
최고 : {up_temp} | 최저 : {down_temp} | 체감 : {feel_temp}
습도 : {humidity} | 풍향 : {wind_direction}

{summary}

{chart}
'''
    return res
    
def getLottery(sender):
    lotto_numbers = random.sample(range(1, 46), 6)
    print(sorted(lotto_numbers))
    
    res = f'''{sender}님을 위한 로또 추천번호!

번호 : {sorted(lotto_numbers)}

1등 당첨되면 반띵 아시죠?
'''
    
    return res

def googleSearch(keyword):
    link = "https://www.google.com/search?q="+keyword
    return link

def namuSearch(keyword):
    link = "https://namu.wiki/w/"+keyword
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
        res = res + content_total_title[i] + "\n" + content_total_link[i]
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
    
    for i in range(0, 9):
        res = res + rank_num[i].text+". "+rank_text[i].text+"\n"
            
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
    print(area)
    source = requests.get("https://map.kakao.com/?q="+area+"맛집", headers=headers)
    soup = bs4.BeautifulSoup(source.content,"html.parser")
    
    rest_names = soup.find_all("strong","tit_name")
    rest_sub = soup.find_all("span","subcategory clickable")
    open_time = soup.find_all("p","periodWarp")
    rest_link = soup.find_all("div","contact clickArea")
    print(soup)
    
    
    
    return "test"
