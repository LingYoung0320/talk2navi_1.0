import openai
import os
import sys


openai.api_key = os.environ["openai_apikey"]

print(openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "你好！"
        }
    ]
))
