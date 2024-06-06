import json

from instruction_following_eval.utils.openai_config import client

# prompts_file_path="data/prompts.jsonl"
# response_file_path="data/response_data_gpt4o_' + '.jsonl"

prompts_file_path="test_new_type/data/prompts.jsonl"
response_file_path="test_new_type/data/response_data_gpt4o.jsonl"

generated_prompts = []
with open(prompts_file_path, 'r', encoding='utf-8') as file:
    for index, line in enumerate(file):
        try:
            generated_prompts.append(json.loads(line.strip()))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON on line {index + 1}: {line.strip()} - {e}")
        except Exception as e:
            print(f"Unexpected error on line {index + 1}: {line.strip()} - {e}")

# for i in range(1, 3):
#     prompt_list = []
#     response_list = []
#     index = 1
#     for item in generated_prompts:
#         prompt = item['prompt']
#
#         completion = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "user", "content": prompt}]
#         )
#
#         response = completion.choices[0].message.content
#
#         prompt_list.append(prompt)
#         response_list.append(response)
#
#         print(str(index) + "\n" + response)
#         index += 1
#
#     with open('data/response_data_gpt4o_' + str(i) + '.jsonl', 'w', encoding='utf-8') as file:
#         for prompt, response in zip(prompt_list, response_list):
#             entry = {"prompt": prompt, "response": response}
#             json_line = json.dumps(entry, ensure_ascii=False)
#             file.write(json_line + '\n')

prompt_list = []
response_list = []
index = 1
for item in generated_prompts:
    prompt = item['prompt']

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    response = completion.choices[0].message.content

    prompt_list.append(prompt)
    response_list.append(response)

    print(str(index) + "\n" + response)
    index += 1

with open(response_file_path, 'w', encoding='utf-8') as file:
    for prompt, response in zip(prompt_list, response_list):
        entry = {"prompt": prompt, "response": response}
        json_line = json.dumps(entry, ensure_ascii=False)
        file.write(json_line + '\n')
