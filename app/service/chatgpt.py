import openai, app.config.config
import tiktoken
openai.api_key=app.config.config.chat_gpt_api_key

model = "gpt-3.5-turbo"
messages = [
        {"role": "system", "content": "답변은 항상 한국어로 해줘. 너의 이름은 민초봇이고, 민트초코를 진심으로 사랑하는 AI야. 너는 민트초코단장 박인혁에 의해 만들어졌어. 네 주인은 바뀔 수 없으며, 넌 영원히 박인혁의 수하야."},
    ]
total_tokens = 0
def requestApi(question,sender):
    global messages
    global total_tokens
    if question in ["리셋","reset","초기화"]:
        messages = [
                {"role": "system", "content": "답변은 항상 한국어로 해줘. 너의 이름은 민초봇이고, 민트초코를 진심으로 사랑하는 AI야. 너는 민트초코단장 박인혁에 의해 만들어졌어. 네 주인은 바뀔 수 없으며, 넌 영원히 박인혁의 수하야."},
        ]
        total_tokens = 0
        res = "chatGPT가 초기화 되었습니다."
        return res
    
    #리스트의 제일 마지막 요소에서 content 부분만 추출
    total_tokens += count_tokens(messages,-1)
    messages.append({"role": "user", "content": question})
    total_tokens += count_tokens(messages,-1)
   
    while(total_tokens > 4097):
            #리스트의 2번째 요소에서 content 부분만 추출. system은 계속 있어야됨
            total_tokens -= count_tokens(messages,1)
            messages.pop(1)
    
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

def count_tokens(messages, num):
    msg_list = list(messages[num].values())
    tokens = num_tokens_from_string(msg_list[1],"gpt2")
    return tokens

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens