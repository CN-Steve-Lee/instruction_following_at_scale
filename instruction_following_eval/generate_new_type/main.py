import json
import os
import tempfile
import importlib.util
import runpy

from absl import app, flags, logging
from instruction_following_eval.evaluation_main import read_prompt_list, read_prompt_to_response_dict, write_outputs, print_report,test_instruction_following_strict,test_instruction_following_loose
from instruction_following_eval.instructions_registry import INSTRUCTION_DICT
from instruction_following_eval.utils.make_Entries import extract_class_definition, extract_function_args_with_docs
from instruction_following_eval.utils.openai_config import client


def generate_checker_code(instruction_name='a'):
    global code_string
    instruction_name = "avb"
    flag = False

    while not flag:
        try:
            prompt = '生成一段检测字符串中是否有各国常用标点符号的代码，代码不用markdown返回，也不返回除代码外的任何内容，不用markdown格式返回，直接返回代码就行'
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一个代码生成者"},
                    {"role": "user", "content": prompt}
                ]
            )
            code_string = completion.choices[0].message.content


            while True:
                try:
                    # exec(code_string)

                    file_path = f'checkers/{instruction_name}.py'
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(code_string)
                    print(f"save {instruction_name}.py success")


                    runpy.run_path(file_path)


                    check_prompt = f"{code_string}"
                    check_completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "你是一个代码检查者，检查以下代码是否符合[生成一段检测字符串中是否有各国常用标点符号的代码,除了代码不返回任何内容]规范，如果符合规范就输出true，否则输出false，不输出其他任何内容，不用markdown格式返回，直接返回代码就行"},
                            {"role": "user", "content": check_prompt}
                        ]
                    )
                    check_result = check_completion.choices[0].message.content.strip().lower()

                    if "true" in check_result:
                        flag = True
                        print("代码已成功生成、运行并通过检查")
                        break
                    else:
                        print("代码未通过检查，重新生成")
                        break

                except Exception as exec_e:
                    print(f"代码运行出错: {exec_e}")

                    correction_prompt = f"{code_string}\n\n错误信息：{exec_e}"
                    correction_completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "你是一个代码纠错师，以下代码运行时出错，请修正代码并返回正确的代码字符串，不用markdown格式返回，直接返回代码就行"},
                            {"role": "user", "content": correction_prompt}
                        ]
                    )
                    code_string = correction_completion.choices[0].message.content
                    print("代码已纠正，重新运行")

        except Exception as e:
            print(f"gpt出错: {e}")

    return code_string


def generate_instruction_kwargs_entries(instruction_name='a'):

    # 从checker开抓
    checker_file_path = f'{instruction_name}.py'
    with open(checker_file_path, 'r', encoding='utf-8') as f:
        instructions_content = f.read()
    class_body = extract_class_definition(instructions_content, instruction_name)
    if class_body:
        args_with_docs = extract_function_args_with_docs(class_body)
    else:
        args_with_docs = {}

    #todo: 加检查gpt

    with open(f'entries/{instruction_name}_instruction_kwargs_entry.jsonl', 'w', encoding='utf-8') as f:
            f.write(json.dumps({"instruction_type": instruction_name,"kwargs": args_with_docs}) + '\n')

def generate_prompt(instruction_name=''):
    #todo:用已有的entry+entry对应的prompt --> 生成当前entry对应的新prompt

    template_entry_file_path = f'prompt_template/entry.txt'
    with open(template_entry_file_path, 'r', encoding='utf-8') as s:
        template_entry_json = s.read()

    template_prompt_file_path = f'prompt_template/entry.txt'
    with open(template_prompt_file_path, 'r', encoding='utf-8') as d:
        template_prompt_json = d.read()

    target_entry_file_path = f'entries/{instruction_name}_instruction_kwargs_entry.jsonl'
    with open(target_entry_file_path, 'r', encoding='utf-8') as f:
        target_entry_json = f.read()

    target_prompt = f"xxxxx{template_entry_json}xxxx{template_prompt_json}xxxx{target_entry_json}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个数据生成者"},
            {"role": "user", "content": target_prompt}
        ]
    )
    prompt_record = completion.choices[0].message.content

    with open(f'prompts/{instruction_name}_prompt.jsonl', 'w', encoding='utf-8') as f:
        f.write(prompt_record)
    return prompt_record

def generate_response(instruction_name='',prompt=''):
    #todo:根据prompt的json中的prompt 生成response

    prompt_json = {}
    with open(f'prompts/{instruction_name}_prompt.jsonl', 'r', encoding='utf-8') as file:
        for index, line in enumerate(file):
            try:
                prompt_json=json.loads(line.strip())
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {index + 1}: {line.strip()} - {e}")
            except Exception as e:
                print(f"Unexpected error on line {index + 1}: {line.strip()} - {e}")

    prompt=prompt_json['prompt']

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个xxxxx"},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message.content

    response_file_path=f'responses/{instruction_name}_response_gpt4o.jsonl'
    with open(response_file_path, 'w', encoding='utf-8') as file:
        entry = {"prompt": prompt, "response": response}
        json_line = json.dumps(entry, ensure_ascii=False)
        file.write(json_line)

    return response

def save_checker_to_temp_file(checker_code):
    fd, path = tempfile.mkstemp(suffix='.py')
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(checker_code)
    return path

def load_temp_module(module_path):
    try:
        spec = importlib.util.spec_from_file_location("temp_module", module_path)
        temp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(temp_module)
        return temp_module
    except Exception as e:
        print(f"Failed to load module from path {module_path}: {e}")
        raise

def register_checker(temp_module, instruction_name='DateFormatChecker'):
    try:
        instruction_class = getattr(temp_module, instruction_name)
        INSTRUCTION_DICT[instruction_name] = instruction_class
    except Exception as e:
        print(e)

def generate_and_register_checkers(num_checkers=1):
    for i in range(num_checkers):
        try:
            instruction_name = "DateFormatChecker"
            checker_code = generate_checker_code(instruction_name)
            temp_file_path = save_checker_to_temp_file(checker_code)

            try:
                temp_module = load_temp_module(temp_file_path)
                register_checker(temp_module, instruction_name)
            finally:
                # 确保临时文件被删除
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    print(f"Error removing temp file: {e}")
        except Exception as e:
            print(f"Error in generating or registering checker {instruction_name}: {e}")

def main(argv):
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")

    # 生成和注册新的checker
    num_checkers = 1
    generate_and_register_checkers(num_checkers)

    instruction_name=''

    prompt_file_path= f'prompts/{instruction_name}_prompt.jsonl'
    response_file_path= f'responses/{instruction_name}_response_gpt4o.jsonl'
    result_file_path='eval_result/'

    _INPUT_DATA = flags.DEFINE_string("input_data", prompt_file_path, "path to input data", required=False)
    _INPUT_RESPONSE_DATA = flags.DEFINE_string("input_response_data", response_file_path, "path to input response data", required=False)
    _OUTPUT_DIR = flags.DEFINE_string("output_dir",result_file_path, "Output directory for inference and eval results.", required=False)


    # 读取输入和响应数据
    inputs = read_prompt_list(_INPUT_DATA.value)
    prompt_to_response = read_prompt_to_response_dict(_INPUT_RESPONSE_DATA.value)

    # 执行原有评估逻辑
    for func, output_file_name in [
        (test_instruction_following_strict, "eval_results_strict"),
        (test_instruction_following_loose, "eval_results_loose"),
    ]:
        logging.info("Generating %s...", output_file_name)
        outputs = []

        success_items = 0
        error_items = 0

        for inp in inputs:
            try:
                outputs.append(func(inp, prompt_to_response))
                success_items += 1
            except Exception as e:
                print(f"Error in key: {inp.key}, {e}")
                error_items += 1

        follow_all_instructions = [o.follow_all_instructions for o in outputs]
        accuracy = sum(follow_all_instructions) / len(outputs)
        logging.info("Accuracy: %f", accuracy)

        output_file_name = os.path.join(_OUTPUT_DIR.value, output_file_name + ".jsonl")
        write_outputs(output_file_name, outputs)
        logging.info("Generated: %s", output_file_name)

        print("=" * 64)
        print(f"{output_file_name} Accuracy Scores:")
        print_report(outputs)
        print("Generated question accuracy: " + str(success_items / (success_items + error_items)))

if __name__ == "__main__":
    app.run(main)
