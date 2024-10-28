# python run_llama3.py --tasks cot1 --conditions bin1 --max_tokens 200 --model llama-3.1-405b

import logging
import json
import argparse
from tqdm import tqdm
import os
import together
import time
logging.getLogger().setLevel(logging.ERROR)

client = together.Together()

def process_prompt(prompt):
    prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n" + prompt + "\n<|start_header_id|>assistant<|end_header_id|>"
    return prompt


def llama_responses(prompt_list, model="llama-3-70b-chat-hf", max_tokens=1000, temperature=0.0):
    responses = []
    for prompt in tqdm(prompt_list):
        prompt = process_prompt(prompt)
        output = None
        for _ in range(10):
            try:
                if "chat" in model:
                    output = client.chat.completions.create(
                                messages = [{"role": "user", "content": prompt}], 
                                model = "meta-llama/" + model,
                                max_tokens = max_tokens,
                                temperature = temperature,
                            )
                else:
                    output = client.completions.create(
                                prompt=prompt,
                                model = "meta-llama/" + model,
                                max_tokens = max_tokens,
                                temperature = temperature,
                            )
            except:
                time.sleep(1)
            
            if not (output is None):
                break
        if "chat" in model:
            responses.append(output.choices[0].message.content)
        else:
            responses.append(output.choices[0].text)
    return responses


def solve_file(name, model, temperature, max_tokens, prompt_type):
    file = f'stimuli/{prompt_type}/{name}.jsonl'
    print(f"Loading {file}")
    if not os.path.exists(file):
        print(f'File {file} does not exist')
        return None
    with open(file, 'r') as f:
        lines = f.readlines()
    lines = [json.loads(line) for line in lines]
    prompts = [line['instruction_plus_input'] for line in lines]
    gts = [line['correct_output'] for line in lines]
    res = llama_responses(prompts, model=model, temperature=0.0, max_tokens=max_tokens)

    # These accs are not what we use in the paper - they're just for quick estimates. 
    # The stats used in the paper are computed in the evaluation/ folder
    accs = [(gt.replace('"', '') in r.replace('"', '')) for r, gt in zip(res, gts)]
    acc = sum(accs) / len(accs)
    print(f"Done {name}")
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
    args.add_argument('--model', type=str, required=True, choices=['llama-3-70b-chat', 'llama-3-70b', 'llama3-405b', 'llama3.1-70b'], default='llama3.1-405b')
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
    if model == 'llama-3-70b-chat':
        model = 'llama-3-70b-chat-hf'
    elif model == 'llama-3-70b':
        model = 'meta-llama-3-70b'
    elif model == 'llama3.1-405b':
        model = 'Meta-Llama-3.1-405B-Instruct-Turbo'
    elif model == 'llama3.1-70b':
        model = 'Meta-Llama-3.1-70B-Instruct-Turbo'
    max_tokens = args.max_tokens

    for task in tasks:
        for condition in conditions:
            name = f'{task}_{condition}'
            d = solve_file(name, model=model, temperature=0.0, max_tokens=max_tokens, prompt_type=prompt_type)
            if d is not None:
                print(f'{name}, {model}: {d["acc"]:.2f}')

