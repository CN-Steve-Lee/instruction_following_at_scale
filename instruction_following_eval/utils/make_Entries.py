import re
import os
import json
from instruction_following_eval.instructions_registry import INSTRUCTION_DICT

instruction_dict = {}
for key, value in INSTRUCTION_DICT.items():
    class_name = value.__name__
    instruction_dict[key] = class_name


def extract_class_definition(file_content, class_name):
    pattern = rf'class {class_name}\(.*\):[\s\S]*?(?=\nclass |\Z)'
    match = re.search(pattern, file_content)
    return match.group(0) if match else None

def extract_function_args_with_docs(class_body):
    # Extract the build_description method's definition
    pattern = r'def build_description\([\s\S]*?\):[\s\S]*?"""([\s\S]*?)"""'
    match = re.search(pattern, class_body)
    if match:
        docstring = match.group(1)
        # Extract the arguments from the docstring
        arg_pattern = r'(\w+): ([\s\S]*?)(?=\n\s+\w+:|\n\n|$)'
        args_with_docs = dict(re.findall(arg_pattern, docstring.replace('\n        ', ' ')))
        return args_with_docs
    return {}

# 从instructions.py开抓
instructions_file_path = os.path.join('..', 'instructions.py')
with open(instructions_file_path, 'r', encoding='utf-8') as f:
    instructions_content = f.read()

final_dict = []

for typeName, class_name in instruction_dict.items():

    class_body = extract_class_definition(instructions_content, class_name)

    if class_body:
        args_with_docs = extract_function_args_with_docs(class_body)
    else:
        args_with_docs = {}

    final_dict.append({
        "instruction_type": typeName,
        "kwargs": args_with_docs
    })


with open('data/instruction_kwargs_entries.jsonl', 'w', encoding='utf-8') as f:
    for entry in final_dict:
        f.write(json.dumps(entry) + '\n')