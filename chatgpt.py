import openai

openai.api_key='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'
model = "gpt-3.5-turbo"
messages = [
        {"role": "system", "content": "답변은 항상 한국어로 해줘."},
    ]

def requestApi(question,sender):
    
    
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
    #문-답은 5쌍까지만 기억
    while(len(messages) > 11):
        messages.pop(1)
    
    return res