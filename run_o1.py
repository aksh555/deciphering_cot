import logging
import json
import argparse
from tqdm import tqdm
import os
logging.getLogger().setLevel(logging.INFO)
from openai import OpenAI,BadRequestError
client = OpenAI()

def o1_responses(prompt_list):
    responses = []
    completion_tokens = []
    for prompt in tqdm(prompt_list):
        try:
            response = client.chat.completions.create(
                    model="o1-preview",
                    messages=[
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ]
                )
            responses.append(response.choices[0].message.content)
            completion_tokens.append(response.usage.completion_tokens_details["reasoning_tokens"])
        except BadRequestError:
            response = "BLOCKED_BY_OPENAI"
            responses.append(response)
            completion_tokens.append(0)
        except Exception as e:
            print(e)
            response = "ERROR"

    return responses, completion_tokens

def solve_file(name, model):
    # o1 does not require CoT prompts
    file = f'stimuli/standard/{name}.jsonl'
    if not os.path.exists(file):
        print(f'File {file} does not exist')
        return None
    with open(file, 'r') as f:
        lines = f.readlines()
    lines = [json.loads(line) for line in lines]
    print(file)
    prompts = [line['instruction_plus_input'] for line in lines][:50]
    gts = [line['correct_output'] for line in lines][:50]
    
    res, completion_tokens = o1_responses(prompts)
    mean_tokens = sum(completion_tokens)/len(completion_tokens)

    # These accs are not what we use in the paper - they're just for quick estimates. 
    # The stats used in the paper are computed in the evaluation/ folder
    accs = [(gt.replace('"', "") in r.replace('"', "")) for r, gt in zip(res, gts)]
    acc = sum(accs) / len(accs)
    print("Completion tokens", mean_tokens)

    d = {'prompts': prompts, 'gts': gts, 'res': res, 'accs': accs, 'acc': acc, 'mean_completion_tokens':mean_tokens}

    output_file = f'logs/standard/{model}'
    with open(output_file, 'w') as f:
        json.dump(d, f)
    
    return d


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--tasks', type=str, required=True, help='split by comma')
    args.add_argument('--conditions', type=str, required=True, help='split by comma')
    args.add_argument('--model', type=str, default='o1-preview-2024-09-12')
    
    args = args.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    tasks = args.tasks.split(',')
    conditions = args.conditions.split(',')
    model = args.model

    for task in tasks:
        for condition in conditions:
            name = f'{task}_{condition}'
            d = solve_file(name, model=model)
            if d is not None:
                print(f'{name}, {model}: {d["acc"]:.2f}')
                print("Completion tokens", d["mean_completion_tokens"])

