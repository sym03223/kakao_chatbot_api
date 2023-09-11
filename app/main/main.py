from flask import Flask, request
from app.service import service, chatgpt
import logging
from logging.handlers import RotatingFileHandler
from app import app, db

from app.model.chats import chats



app.logger.setLevel(logging.INFO)
# 파일 핸들러 설정
log_handler = RotatingFileHandler('./logs/app.log', maxBytes=1024 * 1024 * 10, backupCount=50, encoding='utf-8')
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(log_handler)

zodiac_commands = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
horoscope_commands = ["양","황소","쌍둥이","게","사자","처녀","천칭","전갈","사수","염소","물병","물고기"]

@app.route("/dosomething", methods=['GET'])
def do_something():

    msg=request.args.get("msg")
    sender=request.args.get("sender")
    room=request.args.get("room")
    isGroupChat=request.args.get("isGroupChat")
    
    # db 로깅
    new_chat = chats(room=room, sender=sender, msg=msg, isGroupChat=bool(isGroupChat))
    db.session.add(new_chat)
    db.session.commit()
    
    msgSplit = msg.split()
    res = "none"
    try:
        if "vs" in msg:
            msgSplit = (msg.replace(" ","")).split("vs")
            res = service.getVs(msgSplit,sender)
             #로그 생성
            app.logger.info(f'sender = {sender}, msg = {msg}, room = {room}, isGroupChat = {isGroupChat}')

        if msgSplit[0][0] == "!":
            
            if msgSplit[0] in ["!명령어","!도움말","!help"]:
                res = f'''안녕하세요, {sender}님!\U0001F60D
민초사랑 나라사랑 챗봇 민초봇입니다\U0001F603

<MintchocoBot 커맨드 매뉴얼>

NAME
    민초봇 -- MintChocoBot

[기본 명령어]
    !명령어, !도움말, !help : 커맨드 목록
    
[정보 검색]

>>  !뉴스
>>  !날씨
        사용법 : !날씨 [오늘|내일|모레] [지역명]
>>  !구글
        사용법 : !구글 [검색어]
>>  !나무
        사용법 : !나무 [검색어]
>>  !유튜브
        사용법 : !유튜브 [검색어]
>>  !맛집        
        사용법 : !맛집 [지역명]
>>  !지도
        사용법 : !지도 [지역명]
>>  !실검
>>  !환율
>>  !비트
>>  !챗
        사용법 : !챗 [질문]

[재밋거리]

>>  !메뉴추천
>>  !운세
        사용법 : 띠별운세 - !운세 [띠]
                별자리운세 - !운세 [별자리]
>>  !로또
>>  vs 
        사용법 : [키워드] vs [키워드]
'''

            elif msgSplit[0] == "!날씨":
                area = ""
                if len(msgSplit) != 1:
                    if len(msgSplit) >= 3:
                        for i in range(1, len(msgSplit)):
                            print(i)
                            area = area + msgSplit[i]+" "
                    else:
                        area = msgSplit[1]    
                    res = service.getWeatherData(area.strip())       
                else :
                    res = "지역을 입력해주세요. \n사용법 : !날씨 [오늘|내일|모레] [지역명]"
                    
            elif msgSplit[0] == "!운세":
                if len(msgSplit)!=1:
                    if len(msgSplit) < 3 :
                        keyword = msgSplit[1]
                        if keyword in zodiac_commands:
                            res = service.getZodiac(keyword)    
                        elif keyword in horoscope_commands:
                            res = service.getHoroscope(keyword)    
                        else :
                            res = "다시 입력해 주세요."
                else :
                    res = """검색어를 입력해주세요. 

사용법 : 
!운세 [쥐띠|소띠|호랑이띠|토끼띠|용띠|뱀띠|말띠|양띠|원숭이띠|닭띠|개띠|돼지띠]

!운세 [양|황소|쌍둥이|게|사자|처녀|천칭|전갈|사수|염소|물병|물고기]"
"""
            elif msgSplit[0] == "!로또":
                res = service.getLottery(sender)
            elif msgSplit[0] == "!구글":
                if len(msgSplit)!=1:
                    keyword = msg.replace(msgSplit[0],"").strip()
                    keyword = keyword.replace(" ","+")  
                    res = service.googleSearch(keyword)
                else :
                    res = "검색어를 입력해주세요. \n사용법 : !구글 [검색어]"
                
            elif msgSplit[0] == "!나무":
                if len(msgSplit)!=1:
                    keyword = msg.replace(msgSplit[0],"").strip()
                    keyword = keyword.replace(" ","+")  
                    res = service.namuSearch(keyword)
                else :
                    res = "검색어를 입력해주세요. \n사용법 : !나무 [검색어]"
            elif msgSplit[0] == "!유튜브":
                if len(msgSplit)!=1:
                    keyword = msg.replace(msgSplit[0],"").strip()
                    keyword = keyword.replace(" ","+")  
                    print(keyword)
                    res = service.youtubeSearch(keyword)
                else :
                    res = "검색어를 입력해주세요. \n사용법 : !유튜브 [검색어]"
            elif msgSplit[0] == "!뉴스":
                if len(msgSplit)!=1:
                    keyword = msg.replace(msgSplit[0],"").strip()
                    if keyword.isdigit():
                        keyword = int(keyword)    
                        if keyword < 5:
                            res = service.getNews(keyword)    
                        else :
                            res = "분야를 다시 입력해 주세요."
                    else:
                        keyword = keyword.replace(" ","+")
                        res = service.getNewsSearch(keyword)
                else :
                    res = """분야를 입력해주세요.
사용법 : !뉴스 [0|1|2|3|4|검색어]

0 : 정치
1 : 경제
2 : 사회
3 : 생활/문화
4 : IT/과학
검색어 : 관련 뉴스 검색
"""
            elif msgSplit[0] == "!실검":
                res = service.realtime()
            elif msgSplit[0] == "!환율":
                res = service.getExchangeRate()
            elif msgSplit[0] == "!비트":
                res = service.getAllCoins()
            elif msgSplit[0] == "!맛집":
                area = ""
                if len(msgSplit) != 1:
                    area = msg.replace(msgSplit[0],"").strip()
                    area = area.replace(" ","+")  
                    # if len(msgSplit) >= 3:
                    #     for i in range(1, len(msgSplit)):
                    #         print(i)
                    #         area = area + msgSplit[i]+" "
                    # else:
                    #     area = msgSplit[1]    
                    res = service.getRestaurantByArea(area.strip())       
                else :
                    res = "지역을 입력해주세요. \n사용법 : !맛집 [지역명]"
            elif msgSplit[0] == "!지도":
                area = ""
                if len(msgSplit) != 1:
                    area = msg.replace(msgSplit[0],"").strip()
                    area = area.replace(" ","+")    
                    res = service.getMapSearch(area.strip())       
                else :
                    res = "지역을 입력해주세요. \n사용법 : !지도 [지역명]"
            elif msgSplit[0] == "!메뉴추천":
                res = service.getMenu(sender)
            elif msgSplit[0] == "!저녁추천":
                print(0)
            elif msgSplit[0] == "!채팅순위":
                res = service.getChatRank()
            elif msgSplit[0] == "!챗":
                if len(msgSplit)!=1:
                    question = msg.replace(msgSplit[0],"").strip()
                    res = chatgpt.requestApi(question,sender)
                else :
                    res = "챗 GPT에게 질문을 입력해주세요. \n사용법 : !챗 [질문]"
            else:
                res = "명령을 인식할 수 없습니다.\n!명령어로 명령어를 조회할 수 있습니다."
           
    except Exception as e:
        print(e)
        app.logger.error(f'response = {e}')
        res = "오류가 발생하였습니다."
    
    if res != 'none':
        #로그 생성
        app.logger.info(f'sender = {sender}, msg = {msg}, room = {room}, isGroupChat = {isGroupChat}')
        app.logger.info(f'response = {res}')    
    return (res)