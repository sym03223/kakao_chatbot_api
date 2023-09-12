from flask import Flask
import openai, app.config.config

openai.api_key=app.config.config.chat_gpt_api_key

model = "gpt-3.5-turbo"
messages = [
        {"role": "system", "content": "답변은 항상 한국어로 해줘."},
    ]

def requestApi(question,sender):
    
    if question in ["리셋","reset","초기화"]:
       messages = [
            {"role": "system", "content": "답변은 항상 한국어로 해줘."},
       ]
       res = "chatGPT가 초기화 되었습니다."
       return res
    
    messages.append({"role": "user", "content": question})
    
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