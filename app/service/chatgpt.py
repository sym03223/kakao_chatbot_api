from flask import Flask
import openai, app.config.config
from konlpy.tag import Okt
openai.api_key=app.config.config.chat_gpt_api_key

okt = Okt()

model = "gpt-3.5-turbo"
messages = [
        {"role": "system", "content": "답변은 항상 한국어로 해줘. 너의 이름은 민초봇이고, 민트초코를 사랑하는 AI야. 너는 민트초코단장 박인혁에 의해 만들어졌어"},
    ]
total_tokens = 0
def requestApi(question,sender):
    global messages
    global total_tokens
    if question in ["리셋","reset","초기화"]:
        messages = [
                {"role": "system", "content": "답변은 항상 한국어로 해줘. 너의 이름은 민초봇이고, 민트초코를 사랑하는 AI야. 너는 민트초코단장 박인혁에 의해 만들어졌어"},
        ]
        total_tokens = 0
        res = "chatGPT가 초기화 되었습니다."
        return res
    
    messages.append({"role": "user", "content": question})
    
    for message_dic in messages:
        messages_list = list(message_dic.values())
        for message in messages_list:
            total_tokens += count_tokens(message)
    
    print(messages)
    print("11111total_tokens : ",total_tokens)        
    while(total_tokens > 4097):
            total_tokens -= count_tokens(list(messages[1].values())[0])
            total_tokens -= count_tokens(list(messages[1].values())[1])
            messages.pop(1)
    print(messages)
    print("22222total_tokens : ",total_tokens)
    response = openai.ChatCompletion.create(
    model=model,
    messages=messages
    )
    
    answer = response['choices'][0]['message']['content']
    
    # 챗 GPT 답변 기억
    messages.append({"role": "assistant", "content": answer})
    
    res = f"""[{sender}님, Chat GPT의 답변입니다.]
    
Q : {question}

A : {answer}    

*Chat GPT-3 모델은 2021년 9월까지의 데이터만 반영되어있습니다.
"""
    #문-답은 6쌍까지만 기억
    while(len(messages) > 13):
        messages.pop(1)
    
    return res

def count_tokens(text):
    tokens = okt.morphs(text)
    return len(tokens)
