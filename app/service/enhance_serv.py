import random
from datetime import datetime, timedelta
from sqlalchemy import desc, asc
# from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from app.model.enhancement_game import enhancement_game
from app.model.enhancement_guiness import enhancement_guiness
from app.model.enhancement_history import enhancement_history
from app import db, app
import app.config.config as conf

def create_item(sender,room,item_name):
    
    #현재 보유중인 아이템
    user_items = (
        db.session.query(enhancement_game)
        .filter(enhancement_game.user==sender)
        .order_by(desc('update_date'))
        .all()
    )

    #기존에 있는 아이템인지 확인
    existed_item= (
        db.session.query(enhancement_game)
        .filter(and_(enhancement_game.room == room, enhancement_game.item_name==item_name, enhancement_game.user==sender))
        .all()
    )
    
    after_level = 0
    
    #기존에 없던 아이템이라면!
    if not existed_item:
        #아이템을 5개 이하로 보유하고 있는지 체크
        if user_items and len(user_items)==5:
            res = "아이템은 최대 5개까지 보유할 수 있습니다."
            return res
        #강화한지 1분이 지났는지 체크
        elif user_items:
            current_time = datetime.now()
            time_difference = current_time - user_items[0].update_date
            time_difference_seconds = time_difference.total_seconds()
            if time_difference_seconds < conf.enhance_limit_second:
                res = f"다음 아이템 강화까지 남은 시간 : {int(60-time_difference_seconds)}초"
                return res
        
        result = calc_level(0)
        after_level = result.get('after_level')
        plus_level = result.get('plus_level')
        #새 아이템 생성
        new_item = enhancement_game(user=sender, item_name=item_name,room=room,item_level=after_level)
        db.session.add(new_item)
        res = f"""--------\U0001F389SUCCESS\U0001F389--------
{round((result.get('success_chances'))*100,2)}%의 확률로 강화에 성공하였습니다!!
[{item_name}] Lv.0 \U000027A1 Lv.{after_level} (+{plus_level})
--------SUCCESS--------
"""     
        #히스토리 저장
        new_history = enhancement_history(user=sender, 
                                        item_name=item_name,
                                        room=room,
                                        before_level=0,
                                        change_level=plus_level,
                                        current_level=after_level
                                        )
    else:
        #강화한지 1분이 지났는지 체크
        if user_items:
            current_time = datetime.now()
            print(current_time)
            print(user_items[0].update_date)
            time_difference = current_time - user_items[0].update_date
            time_difference_seconds = time_difference.total_seconds()
            if time_difference_seconds < conf.enhance_limit_second:
                res = f"다음 아이템 강화까지 남은 시간 : {int(conf.enhance_limit_second-time_difference_seconds)}초"
                return res    
        item = existed_item[0]
        #기존 아이템 수정
        result = calc_level(item.item_level)
        before_level = item.item_level
        after_level = result.get('after_level')
        plus_level = result.get('plus_level')
        #결과
        if after_level==0:
            res = f"""--------\U0001F4A3DESTROY\U0001F4A3--------
{round(result.get('destroy_chances')*100,2)}%의 확률로 아이템이 파괴~\U0001F631
[{item.item_name}]이 가루가 되었습니다~!!
--------\U0001F4A3DESTROY\U0001F4A3--------
"""         
            #아이템삭제
            db.session.delete(item)
        elif item.item_level > after_level:
            
            res = f"""--------\U0001F62DFAILURE\U0001F62D--------
{round((1-result.get('success_chances')-result.get('destroy_chances'))*100,2)}%의 확률로 강화에 실패하였습니다...\U0001F629
[{item.item_name}] Lv.{item.item_level} \U000027A1 Lv.{after_level} ({plus_level})
--------\U0001F62DFAILURE\U0001F62D--------
"""
            #아이템 레벨 업데이트
            item.item_level = after_level
            db.session.add(item)
        elif item.item_level < after_level:
            res = f"""--------\U0001F389SUCCESS\U0001F389--------
{round(result.get('success_chances')*100,2)}%의 확률로 강화에 성공하였습니다!!
[{item.item_name}] Lv.{item.item_level} \U000027A1 Lv.{after_level} (+{plus_level})
--------\U0001F389SUCCESS\U0001F389--------
"""     
            #아이템 레벨 업데이트
            item.item_level = after_level
            db.session.add(item)
        
        #히스토리 저장
        new_history = enhancement_history(user=sender, 
                                        item_name=item_name,
                                        room=room,
                                        before_level=before_level,
                                        change_level=plus_level,
                                        current_level=after_level
                                        )
    db.session.add(new_history)
    db.session.commit()
    

    return res

def delete_my_item(sender,room,item_name):
    
    existed_item= (
        db.session.query(enhancement_game)
        .filter(and_(enhancement_game.room == room, enhancement_game.item_name==item_name, enhancement_game.user==sender))
        .all()
    )
    
    res = ""
    if existed_item:
        item = existed_item[0]
        res = f"[{item.item_name}] Lv.{item.item_level} 을 삭제하였습니다."
        db.session.delete(item)
        db.session.commit()
    else:
        res = "보유하지 않은 아이템입니다."
    return res

def calc_level(current_level):
    success_chances = max(0.05, 1 - (0.005 * abs(current_level)))
    destroy_chances = 0.001*abs(current_level)
    result = {}
    
    rand = random.random()
    plus_level = random.randint(1,9)
    #성공
    if rand < success_chances:
        current_level += plus_level
    #실패
    else:
        #파괴
        if rand < success_chances + destroy_chances:
            plus_level=-current_level
            current_level = 0  
        #레벨다운
        else:
            current_level -= plus_level             
            plus_level=-plus_level
    
    result['success_chances'] = success_chances
    result['destroy_chances'] = destroy_chances
    result['plus_level'] = plus_level
    result['after_level'] = current_level
    
    return result
    
def get_my_item(sender,room):
    #현재 보유중인 아이템
    user_items = (
        db.session.query(enhancement_game)
        .filter(enhancement_game.user==sender)
        .order_by(desc('update_date'))
        .all()
    )
    res = f"[현재 {sender}님이 보유중인 아이템]\n\n"
    for index, item in enumerate(user_items):
        res = res + f"{str(index+1)}. [{item.item_name}] LV.{item.item_level}\n"
    return res.strip()

def get_manual():
    res ="""[강화 게임(베타)]
*해당 게임은 베타버전이며 정식오픈하면 이전 데이터는 전부 삭제됩니다.
    
!강화 (아이템 명)
 - 자신이 원하는 이름의 아이템을 강화할 수 있다. 
 - 강화 성공시 1~9레벨이 무작위로 올라가고, 실패시 레벨이 내려가거나 파괴될 수 있다. 
 - 확률은 레벨에 비례하지 절대로 수치가 아니며, 확률이 음수(-)로 표기될 수 있다. 
 - 강화는 1분마다 한 번 강화할 수 있다
 - 아이템은 인당 최고 5개까지 보유 가능하다
 
!강화 보유 (아이템명)
 - 내가 강화 중인 아이템 목록을 보여준다.
 
!강화 삭제 (아이템명)
 - 등록된 아이템은 사라진다.
 
!강화 순위
 - 채팅방의 현재 강화 순위 top 10을 보여준다.
"""
    return res

def get_room_rank(room):
    # 현재 날짜 구하기
    current_date = datetime.now()

    # 이번 주의 시작일 구하기 (월요일 기준)
    start_of_week = current_date - timedelta(days=current_date.weekday())

    # 이번 주의 끝일 구하기 (일요일 기준)
    end_of_week = start_of_week + timedelta(days=6)

    existed_item= (
        db.session.query(enhancement_game)
        .filter(and_(enhancement_game.room == room,
            enhancement_game.create_date >= start_of_week,
            enhancement_game.create_date <= end_of_week))
        .order_by(desc('item_level'))
        .limit(10)
        .all()
    )
    formatted_now = current_date.strftime("%Y년 %m월")
    week_number = get_week_number()
    
    res = f"""[{formatted_now} {week_number}주차 강화 순위]
방이름 : {room}
    
> [아이템] (레벨) - 유저
"""
    
    for index, item in enumerate(existed_item):
        res = res + f"{str(index+1)}. [{item.item_name}](Lv.{item.item_level}) - {item.user}\n"
    return res.strip()

def get_week_number():
    # 현재 날짜를 구합니다.
    current_date = datetime.now()

    # 현재 날짜의 년, 월을 얻습니다.
    year = current_date.year
    month = current_date.month

    # 현재 날짜가 포함된 주의 첫 날을 얻습니다.
    first_day_of_month = datetime(year, month, 1)
    first_day_of_week = first_day_of_month - timedelta(days=first_day_of_month.weekday())

    # 현재 날짜가 속한 주차를 계산합니다.
    week_number = ((current_date - first_day_of_week).days // 7) + 1
    return week_number


#### 스케줄러용 함수
def save_guiness():
     # 현재 날짜 구하기
    current_date = datetime.now()

    # 이번 주의 시작일 구하기 (월요일 기준)
    start_of_week = current_date - timedelta(days=current_date.weekday())

    # 이번 주의 끝일 구하기 (일요일 기준)
    end_of_week = start_of_week + timedelta(days=6)

    rooms = getRooms()
    
    for i in range(0,len(rooms)):
        best_item_this_week = (
            db.session.query(enhancement_game)
            .filter(and_(enhancement_game.room == rooms[i],
                enhancement_game.create_date >= start_of_week,
                enhancement_game.create_date <= end_of_week))
            .order_by(desc('item_level'))
            .first()
        )
        
        if best_item_this_week:
            item = best_item_this_week[0]
            print("item : "+item)
            new_guiness = enhancement_guiness(user=item.user,item_name=item.item_name,
                                            item_level=item.item_name,room=rooms[i])
            db.session.add(new_guiness)
            db.session.commit()
            
def getRooms():
    
    rooms = (
        db.session.query(enhancement_game.room)
        .distinct()
        .all()
    )
    return rooms