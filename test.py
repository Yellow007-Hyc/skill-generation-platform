import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

resp = client.chat.completions.create(
    model="glm-4.7-flash",
    messages=[{"role": "user", "content": "用一句话介绍你自己"}]
)
print(resp.choices[0].message.content)