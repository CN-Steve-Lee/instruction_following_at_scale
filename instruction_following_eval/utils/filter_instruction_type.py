import os
import json


def load_jsonl(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line.strip()) for line in file]


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def filter_and_save(data, instruction_ids):

    filtered_data = {id: {} for id in instruction_ids}


    for item in data:
        item_key = item['key']
        for instruction_id in item['instruction_id_list']:
            if instruction_id in filtered_data and item_key not in filtered_data[instruction_id]:
                filtered_data[instruction_id][item_key] = item


    base_directory = './instruction_type/'
    ensure_directory(base_directory)


    for instruction_id, items_dict in filtered_data.items():
        if items_dict:
            items = list(items_dict.values())
            safe_instruction_id = instruction_id.replace(':', '#')
            sub_directory = os.path.join(base_directory, safe_instruction_id)
            ensure_directory(sub_directory)
            file_name = os.path.join(sub_directory, 'example.jsonl')
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(items, file, ensure_ascii=False, indent=4)
                print(f'Saved {len(items)} items to {file_name}')

def main():
    file_path = '../data/input_data.jsonl'
    data = load_jsonl(file_path)

    instruction_ids = set()
    for item in data:
        instruction_ids.update(item['instruction_id_list'])

    filter_and_save(data, instruction_ids)

if __name__ == '__main__':
    main()
