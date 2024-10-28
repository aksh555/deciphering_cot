import logging
import json
import argparse
from tqdm import tqdm
import os
import anthropic
import time
logging.getLogger().setLevel(logging.ERROR)

client = anthropic.Anthropic()


def claude_responses(prompt_list, model="claude-3-opus-20240229", max_tokens=1000, temperature=0.0):
    responses = []
    for prompt in tqdm(prompt_list):
        output = None
        for _ in range(10):
            try:
                completion = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system="Provide only your answer, without any explanation.",
                    messages=[{"role":"user", "content": prompt}]
                )

                output = completion.content[0].text
                if output is None:
                    output = ""
            except:
                time.sleep(60)
            
            if not (output is None):
                break

        if output is None:
            responses.append("")
        else:
            responses.append(output)
    return responses

    


def solve_file(name, model, temperature, max_tokens, prompt_type):
    file = f'stimuli/{prompt_type}/{name}.jsonl'
    if not os.path.exists(file):
        print(f'File {file} does not exist')
        return None
    with open(file, 'r') as f:
        lines = f.readlines()
    lines = [json.loads(line) for line in lines]
    prompts = [line['instruction_plus_input'] for line in lines]
    gts = [line['correct_output'] for line in lines]
    res = claude_responses(prompts, model=model, temperature=0.0, max_tokens=max_tokens)

    # These accs are not what we use in the paper - they're just for quick estimates. 
    # The stats used in the paper are computed in the evaluation/ folder
    accs = [(gt.replace('"', "") in r.replace('"', "")) for r, gt in zip(res, gts)]
    acc = sum(accs) / len(accs)
    print(f'Accuracy: {acc}')

    d = {'prompts': prompts, 'gts': gts, 'res': res, 'accs': accs, 'acc': acc}

    fo_directory = f'logs/{prompt_type}/{model}'
    if not os.path.exists(fo_directory):
        os.makedirs(fo_directory, exist_ok=True)
    
    output_file = f'{fo_directory}/{name}.json'
    with open(output_file, 'w') as f:
        json.dump(d, f)
    
    return d


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--tasks', type=str, required=True, help='split by comma')
    args.add_argument('--conditions', type=str, required=True, help='split by comma')
    args.add_argument('--model', type=str, required=True, choices=['claude-3'])
    args.add_argument('--max_tokens', type=int, help='default = 1000', default=1000)
    args.add_argument("--prompt_type", type=str, help="Prompt type to use [standard, text_cot, math_cot, number_cot]", default="text_cot")
    args = args.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    tasks = args.tasks.split(',')
    conditions = args.conditions.split(',')
    model = args.model
    prompt_type = args.prompt_type

    if model == "claude-3":
        model = "claude-3-opus-20240229"
    max_tokens = args.max_tokens

    for task in tasks:
        for condition in conditions:
            name = f'{task}_{condition}'
            d = solve_file(name, model=model, temperature=0.0, max_tokens=max_tokens, prompt_type=prompt_type)
            if d is not None:
                print(f'{name}, {model}: {d["acc"]:.2f}')

