import random
from datetime import datetime, timedelta
from sqlalchemy import desc, asc
from sqlalchemy import text
from sqlalchemy.sql import func
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
        .filter(and_(enhancement_game.user==sender, enhancement_game.room==room))
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
                res = f"다음 아이템 강화까지 남은 시간 : {int(conf.enhance_limit_second-time_difference_seconds)}초"
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
--------\U0001F389SUCCESS\U0001F389--------
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
            res = f"""--------💥DESTROY💥--------
{round(result.get('destroy_chances')*100,2)}%의 확률로 아이템이 파괴~\U0001F631
[{item.item_name}]이 가루가 되었습니다~!!
[{item.item_name}] Lv.{item.item_level} \U000027A1 Lv.0 (-{item.item_level})
--------\U0001F4A3DESTROY\U0001F4A3--------
"""         
            #아이템삭제
            db.session.delete(item)
        #강화실패
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
            #강화 대성공
            if plus_level >= 10:
                res = f"""-------🌟WONDERFUL🌟-------
{round(result.get('success_chances')*100,2)}%의 확률로 강화에 대성공하였습니다!!
[{item.item_name}] Lv.{item.item_level} \U000027A1 Lv.{after_level} (+{plus_level})
-------🌟WONDERFUL🌟-------
"""         #강화 일반성공
            else:
                res = f"""--------\U0001F389SUCCESS\U0001F389--------
{round(result.get('success_chances')*100,2)}%의 확률로 강화에 성공하였습니다!!
[{item.item_name}] Lv.{item.item_level} \U000027A1 Lv.{after_level} (+{plus_level})
--------\U0001F389SUCCESS\U0001F389--------
"""     
            #아이템 레벨 업데이트
            item.item_level = after_level
            db.session.add(item)
        #파괴방지
        elif plus_level==0:
            res = f"""--------🛡️DEFENSE🛡️--------
{round(result.get('talisman')*100,2)}%의 확률로 파괴를 막았습니다!!
[{item.item_name}] Lv.{item.item_level} \U000027A1 Lv.{after_level} (+{plus_level})
--------🛡️DEFENSE🛡️--------
"""    
            #아이템 레벨 업데이트
            item.item_level = after_level
            item.update_date = datetime.now()
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
    success_chances = max(0.2, 1 - (0.00478 * abs(current_level)))
    destroy_chances = 0.0005*abs(current_level)
    result = {}
    talisman=0
    rand = random.random()
    plus_level = random.randint(1,9)
    print("rand : ",rand)
    print("success_chances : ",success_chances)
    print("destroy_chances : ",destroy_chances)
    print("plus_level : ",plus_level)
    #대성공
    if rand <= 0.01:
        plus_level = random.randint(10,50)
        current_level += plus_level
        success_chances = 0.01
    else:
        #성공
        if rand < success_chances:
            current_level += plus_level
        #실패
        else:
            #파괴
            if rand < success_chances + destroy_chances and current_level >= 40:
                talisman = random.random()
                print(talisman)
                #파괴방지부적작동
                if talisman <= 0.3:
                    current_level=current_level
                    talisman=destroy_chances*0.3
                    plus_level=0
                else:    
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
    result['talisman'] = talisman
    
    return result
    
def get_my_item(sender,room):
    #현재 보유중인 아이템
    user_items = (
        db.session.query(enhancement_game)
        .filter(and_(enhancement_game.user==sender,enhancement_game.room==room))
        .order_by(desc('item_level'),desc('update_date'))
        .all()
    )
    if user_items:
        res = f"[현재 {sender}님이 보유중인 아이템]\n\n"
        for index, item in enumerate(user_items):
            res = res + f"{str(index+1)}. [{item.item_name}] Lv.{item.item_level}\n"
    else:
        res = "보유한 아이템이 없습니다."
    return res.strip()

def get_manual():
    res ="""[강화 게임]
    
!강화 (아이템 명)
 - 자신이 원하는 이름의 아이템을 강화할 수 있다. 
 - 강화 성공시 1~9레벨이 무작위로 올라가고, 실패시 레벨이 내려가거나 파괴될 수 있다. 
 - 파괴 시 30% 확률로 파괴방지부적이 작동된다.
 - 1%확률로 강화 대성공시 10~50 레벨이 무작위로 올라간다.
 - 확률은 레벨에 비례하지 절대로 수치가 아니며, 확률이 음수(-)로 표기될 수 있다. 
 - 강화는 1분마다 한 번 강화할 수 있다
 - 아이템은 인당 최고 5개까지 보유 가능하다
 - 매주 일요일 자정 마다 최고 레벨의 아이템을 기네스에 기록하고 전체 강화 데이터를 초기화한다.
 
!강화 보유 (아이템명)
 - 내가 강화 중인 아이템 목록을 보여준다.
 
!강화 삭제 (아이템명)
 - 등록된 아이템은 사라진다.
 
!강화 순위
 - 채팅방의 현재 강화 순위 top 10을 보여준다.
 
!강화 내기록
 - 강화 성공/실패/파괴 횟수 등 출력
 
!강화 기네스
 - 주차별 역대 강화 기록 출력
 
!강화 무덤
- 해당 주차동안 파괴된 아이템 목록
"""
    return res

def get_room_rank(room):
    # 현재 날짜 구하기
    current_date = datetime.now()

    # 이번 주의 시작일 구하기 (월요일 기준)
    start_of_week = current_date - timedelta(days=current_date.weekday(), hours=current_date.hour, minutes=current_date.minute, seconds=current_date.second)

    # 이번 주의 끝일 구하기 (일요일 기준)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    # print("이번 주의 시작일:", start_of_week.strftime("%Y-%m-%d %H:%M:%S"))
    # print("이번 주의 끝일:", end_of_week.strftime("%Y-%m-%d %H:%M:%S"))
    existed_item= (
        db.session.query(enhancement_game)
        .filter(and_(enhancement_game.room == room,
            enhancement_game.create_date >= start_of_week,
            enhancement_game.create_date <= end_of_week))
        .order_by(desc('item_level'))
        .limit(10)
        .all()
    )
    if existed_item:
        
        formatted_now = current_date.strftime("%Y년 %m월")
        week_number = get_week_number()
        
        res = f"""[{formatted_now} {week_number}주차 강화 순위]
방이름 : {room}
    
> [아이템] (레벨) - 유저
"""
        
        for index, item in enumerate(existed_item):
            res = res + f"{str(index+1)}. [{item.item_name}](Lv.{item.item_level}) - {item.user}\n"
    else:
        res = "순위 내역이 없습니다."
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

def get_my_record(sender, room):
    
    # 현재 날짜 구하기
    current_date = datetime.now()

    # 이번 주의 시작일 구하기 (월요일 기준)
    start_of_week = current_date - timedelta(days=current_date.weekday(), hours=current_date.hour, minutes=current_date.minute, seconds=current_date.second)

    # 이번 주의 끝일 구하기 (일요일 기준)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    destroy_count = db.session.query(enhancement_history).filter(
        enhancement_history.room == room,
        enhancement_history.user == sender,
        enhancement_history.current_level == 0,
        enhancement_history.create_date >= start_of_week,
        enhancement_history.create_date <= end_of_week
    ).count()

    success_count = db.session.query(enhancement_history).filter(
        enhancement_history.room == room,
        enhancement_history.user == sender,
        enhancement_history.change_level > 0,
        enhancement_history.create_date >= start_of_week,
        enhancement_history.create_date <= end_of_week
    ).count()

    fail_count = db.session.query(enhancement_history).filter(
        enhancement_history.room == room,
        enhancement_history.user == sender,
        enhancement_history.change_level < 0,
        enhancement_history.create_date >= start_of_week,
        enhancement_history.create_date <= end_of_week
    ).count()

    total_level_up = db.session.query(enhancement_history).filter(
        enhancement_history.room == room,
        enhancement_history.user == sender,
        enhancement_history.change_level > 0,
        enhancement_history.create_date >= start_of_week,
        enhancement_history.create_date <= end_of_week
    ).with_entities(func.sum(enhancement_history.change_level)).scalar()

    total_level_down = db.session.query(enhancement_history).filter(
        enhancement_history.room == room,
        enhancement_history.user == sender,
        enhancement_history.change_level < 0,
        enhancement_history.create_date >= start_of_week,
        enhancement_history.create_date <= end_of_week
    ).with_entities(func.sum(enhancement_history.change_level)).scalar()
    
    res = f"""[금주 {sender}님의 기록입니다.]

총 강화 횟수 : {success_count+fail_count+destroy_count} 
성공횟수 : {success_count}
실패횟수 : {fail_count}
파괴횟수 : {destroy_count}

총 레벨 업 : {total_level_up or 0}
총 레벨 다운 : {total_level_down or 0}
"""
    
    return res

def call_procedure():
    db.session.execute(text("call save_guiness()"))
    
def get_guiness(room):
    
    result = (
        db.session.query(enhancement_guiness)
        .filter(enhancement_guiness.room==room)
        .order_by(desc('item_level'))
        .limit(10)
        .all()
    )
    if result:
        
        res = f"""✨🌟💐[명예의 전당]💐🌟✨
방 이름 : {room}

"""
        for index,item in enumerate(result):
            res = res + f"{str(index+1)}. [{item.item_name}](Lv.{item.item_level}) - {item.user}\n"
    else:
        res = "아직 명예의 전당에 오른 아이템이 없습니다."
    return res.strip()

#### 스케줄러용 함수
def save_guiness():
     # 현재 날짜 구하기
    current_date = datetime.now()

    # 이번 주의 시작일 구하기 (월요일 기준)
    start_of_week = current_date - timedelta(days=current_date.weekday(), hours=current_date.hour, minutes=current_date.minute, seconds=current_date.second)

    # 이번 주의 끝일 구하기 (일요일 기준)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    rooms = getRooms()
    for room in rooms:
        best_item_this_week = (
            db.session.query(enhancement_game)
            .filter(and_(enhancement_game.room == room[0],
                enhancement_game.create_date >= start_of_week,
                enhancement_game.create_date <= end_of_week))
            .order_by(desc('item_level'), desc('update_date'))
            .first()
        )
        if best_item_this_week:
            item = best_item_this_week
            new_guiness = enhancement_guiness(user=item.user,item_name=item.item_name,
                                            item_level=item.item_level,room=item.room)
            db.session.add(new_guiness)
            db.session.commit()
    #game 테이블 초기화
    db.session.query(enhancement_game).delete()
    db.session.commit()
    
def getRooms():

    rooms = (
        db.session.query(enhancement_game.room)
        .distinct()
        .all()
    )
    return rooms

def get_my_grave(sender,room):
     # 현재 날짜 구하기
    current_date = datetime.now()

    # 이번 주의 시작일 구하기 (월요일 기준)
    start_of_week = current_date - timedelta(days=current_date.weekday(), hours=current_date.hour, minutes=current_date.minute, seconds=current_date.second)

    # 이번 주의 끝일 구하기 (일요일 기준)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    print(start_of_week)
    print(end_of_week)
    grave_items = (
            db.session.query(enhancement_history)
            .filter(and_(enhancement_history.room == room,
                enhancement_history.user == sender,
                enhancement_history.current_level == 0,
                enhancement_history.create_date >= start_of_week,
                enhancement_history.create_date <= end_of_week))
            .order_by(desc('before_level'),desc('update_date'))
            .all()
    )
    print(grave_items)
    if grave_items:
    
        res = f"""[{sender}님의 파괴된 아이템 목록]

> [아이템] (최종레벨) - 유저
"""
        
        for index, item in enumerate(grave_items):
            res = res + f"{str(index+1)}. {item.item_name} (Lv.{item.before_level}) - {item.user}\n"
    else:
        res = "데이터가 존재하지 않습니다."
    return res