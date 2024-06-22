from models.openai_help import gpts
import logging
import json
import argparse
import os

logging.getLogger().setLevel(logging.WARNING)

def edit_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def solve_file(name, model, temperature, max_tokens, prompt_type):
    file = f'./stimuli/{prompt_type}/{name}.jsonl'
    print(f"Loading {file}")
    if not os.path.exists(file):
        print(f'File {file} does not exist')
        return None
    with open(file, 'r') as f:
        lines = f.readlines()
    lines = [json.loads(line) for line in lines]
    prompts = [line['instruction_plus_input'] for line in lines]
    gts = ['"' + line['correct_output'] + '"' for line in lines]
    res = gpts(prompts, model=model, temperature=temperature, max_tokens=max_tokens)
    accs = [(r == gt) for r, gt in zip(res, gts)]
    eds = [edit_distance(r, gt) for r, gt in zip(res, gts)]
    acc = sum(accs) / len(accs)
    ed = sum(eds) / len(eds)
    print(f"Done {name}")
    d = {'prompts': prompts, 'gts': gts, 'res': res, 'accs': accs, 'acc': acc, 'eds': eds, 'ed': ed}

    fo_directory = f'./logs/{prompt_type}'
    if not os.path.exists(fo_directory):
        os.makedirs(fo_directory, exist_ok=False)
    
    output_file = f'{fo_directory}/{name}.json'
    with open(output_file, 'w') as f:
        json.dump(d, f)
    
    return d


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--tasks', type=str, required=True, help='split by comma')
    args.add_argument('--conditions', type=str, required=True, help='split by comma')
    args.add_argument('--model', type=str, default='gpt-4-0613')
    args.add_argument('--max_tokens', type=int, help='default = 200', default=200)
    args.add_argument('--temperature', type=float, help='default = 0.0', default=0.0)
    args.add_argument("--prompt_type", type=str, help="Prompt type to use [standard, text_cot, math_cot, number_cot]", default="text_cot")
    args = args.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    tasks = args.tasks.split(',')
    conditions = args.conditions.split(',')
    model = args.model
    max_tokens = args.max_tokens
    temperature = args.temperature
    prompt_type = args.prompt_type

    for task in tasks:
        for condition in conditions:
            name = f'{task}_{condition}'
            d = solve_file(name, model=model, temperature=temperature, max_tokens=max_tokens, prompt_type=prompt_type)
            if d is not None:
                print(f'{name}, {model}: {d["acc"]:.2f} ({d["ed"]:.2f})')

