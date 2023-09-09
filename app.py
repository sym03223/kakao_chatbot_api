from flask import Flask, request
import service

app = Flask(__name__)
command = {"!안녕","!날씨","!운세"}

@app.route("/hello", methods=['GET'])
def hello():
  return "hello world"

@app.route("/dosomething", methods=['GET'])
def do_something():
    msg=request.args.get("msg")
    sender=request.args.get("sender")
    room=request.args.get("room")
    isGroupChat=request.args.get("isGroupChat")
    
    #print("msg="+msg+", sender="+sender+", room="+room+", isGroupChat="+isGroupChat)
    
    msgSplit = msg.split()
    res = "명령을 인식할 수 없습니다."
    
    if msgSplit[0][0] == "!":
        if msgSplit[0] in ["!명령어","!도움말","!help"]:
            res = f'''안녕하세요, {sender}님!\U0001F60D
민초사랑 나라사랑 챗봇 민초봇입니다\U0001F603

************************************************      
<MintchocoBot General Commands Manual>
************************************************

NAME
    민초봇 -- MintChocoBot

[기본 명령어]
    !명령어: 인사 & 도움말
    
[정보 검색]

o !뉴스
o !날씨
o !구글
o !유튜브
o !실검
o !환율
o !비트
o !점심추천
o !저녁추천
o !노래추천

[재밋거리]

o !이미지
o !띠별운세
o !별자리운세
o !로또
o !퀴즈
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
                # print("area : "+area.strip())
                res = service.getWeatherData(area.strip())       
            else :
                res = "지역을 입력해주세요. \n사용법 : !날씨 [지역명]"
                 
        elif msgSplit[0] == "!띠별운세":
            if len(msgSplit)!=1:
                if len(msgSplit) < 3 :
                    keyword = msgSplit[1]
                    keyword = keyword if keyword[-1]=="띠" else keyword+"띠"
                    print("123123123"+keyword)
                    res = service.getZodiac(keyword)
                else :
                    res = "띠는 한개만 입력해 주세요."
            else :
                res = "검색어를 입력해주세요. \n사용법 : !띠별운세 [쥐띠|소띠|호랑이띠|토끼띠|용띠|뱀띠|말띠|양띠|원숭이띠|닭띠|개띠|돼지띠]"
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
                try:
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
                except Exception as e:
                    print("Error : ", e)
                    res = "명령어를 인식할 수 없습니다."
                
            else :
                res = """분야를 입력해주세요.
사용법 : !뉴스 [0|1|2|3|4]

0 : 정치
1 : 경제
2 : 사회
3 : 생활/문화
4 : IT/과학
"""
        elif msgSplit[0] == "!실검":
            res = service.realtime()
        elif msgSplit[0] == "!환율":
            res = service.getExchangeRate()
        elif msgSplit[0] == "!비트":
            if len(msgSplit)!=1:
                keyword = msg.replace(msgSplit[0],"").strip()
                keyword = keyword.replace(" ","+")  
                print(keyword)
                res = service.youtubeSearch(keyword)
            else :
                res = service.getAllCoins()
        elif msgSplit[0] == "!맛집":
            area = ""
            if len(msgSplit) != 1:
                if len(msgSplit) >= 3:
                    for i in range(1, len(msgSplit)):
                        print(i)
                        area = area + msgSplit[i]+" "
                else:
                    area = msgSplit[1]    
                res = service.getRestaurantByArea(area.strip())       
            else :
                res = "지역을 입력해주세요. \n사용법 : !맛집 [지역명]"
        elif msgSplit[0] == "!지도":
            print(0)
        elif msgSplit[0] == "!점심추천":
            print(0)
        elif msgSplit[0] == "!저녁추천":
            print(0)
    return (res)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
    