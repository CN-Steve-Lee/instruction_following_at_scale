from instruction_following_eval.utils.filter_instruction_type import load_jsonl
from openai_config import client
import json

raw_data = load_jsonl('../data/input_data.jsonl')
instruction_kwargs_entries =load_jsonl('data/instruction_kwargs_entries.jsonl')

generate_list=[]
index=1
for item in raw_data:
    print(index)
    raw_data_item_json_str=json.dumps(item, ensure_ascii=False)

    matching_instruction_type=[]
    for instruction_item in item.get("instruction_id_list"):
        matching_instruction_type.append(
            [entry for entry in instruction_kwargs_entries if entry['instruction_type'] == instruction_item]
        )


    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a prompt engineer. Please strictly follow the rules to imitate question creation based on the reference materials and sample questions I provide, as well as the format of those questions. Note: You must create questions strictly according to the requirements and format, ensuring that the type of instructions in your created questions matches exactly with those in the given examples and reference materials. Also, consider the reasonableness of pairing each question with its parameter values."},
            {"role": "user", "content": "Please follow the format and style of this example to create a json record.(key="+str(index)+")，example：\n"+raw_data_item_json_str+"\nAt the same time, I will provide you with all the corresponding parameter lists and descriptions of the data structures for these parameters as follows.:\n"
                                        +json.dumps(matching_instruction_type, ensure_ascii=False)+"\n\nPlease reply strictly according to the example format, and do not reply with any irrelevant characters!"

            }
        ]
    )

    index += 1
    result= completion.choices[0].message.content
    generate_list.append(result)
    print(result)

with open('data/prompts.jsonl', 'w', encoding='utf-8') as f:
    for entry in generate_list:
        f.write(entry + '\n')


