import json

from instruction_following_eval.utils.openai_config import client

prompt = 'prompt'

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)

response = completion.choices[0].message.content