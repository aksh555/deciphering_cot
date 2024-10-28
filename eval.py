import json
import re
from Levenshtein import distance
import statistics
import jsonlines
import sys
import pandas as pd
import argparse

end_after_strings = ["Original text: ", "message is:", "original text is:", "message is ", "we get:"]
# end_after_strings = ["Therefore, the original sequence of numbers is:","Original sequence:"]
delete_after_strings = ["However, this doesn't make sense", "However, this doesn't make much sense", "This sentence still doesn't make", "However, this sentence doesn't make", "This still doesn't make sense"]
shift_freqs = [59,21,117,5,15,12,6,3,1,3,3,7,1225,5,2,4,2,2,1,1,4,2,17,3,7]

def desc(idx,gt_chain,pred_chain,gt,res):
    print("#", idx)
    print("gt_chain", gt_chain)
    print("----")
    print("pred_chain", pred_chain)
    print("----")
    print("gt", gt, "res", res)
    print("**************")

def main(args):
    data_types = ["bin1","bin2","bin3","bin4","bin5"]
    big_df = pd.DataFrame()
    prompt_type = args.prompt_type
    fo_directory = f"logs/{prompt_type}/"
    temp = 0.0
    corrupt = False
    chain_check = False
    chain_directory = "shift_chain/"
    bin_probs = {}
    for bin in data_types:
        with open(f"seven_letter_words/{bin}_prob.txt", 'r') as file:
            second_column_words = [line.split(' ')[1].strip() for line in file][:100]
            bin_probs[bin] = second_column_words
    
    for shift in range(1,26):
        for fi_label in data_types:
            pred_nchars = []
            input_nchars = []
            corrects = []
            preds = []
            gts = []
            small_df = pd.DataFrame()
            condition = prompt_type + str(shift) + "_" + fi_label
            if corrupt:
                condition += "_nohelp2"
    
            try:
                file = fo_directory + condition + ".json"
                fi = open(file, "r")
                if chain_check and prompt_type == "text_cot":
                    chain_file = chain_directory + condition + ".jsonl"
                    fi_chain = open(chain_file, "r")
                print(f"Loading {file}")
            except:
                print(f"\t{file} not found, skipping {fi_label} {shift}")
                continue
            print("*"*10)
            data = json.load(fi)
            if chain_check and prompt_type == "text_cot":
                data_chain = []
                for line in fi_chain:
                    x = json.loads(line)
                    data_chain.append(x["chain"])

            count_correct = 0
            count_correct_demo = 0
            count_total = 0
            total_dist = 0
            chain_correct_op_incorrect = 0
            chain_correct_op_correct = 0
            chain_incorrect_op_correct = 0
            chain_incorrect_op_incorrect = 0
            distances = []
            for idx,(gt,res) in enumerate(zip(data["gts"], data["res"])):
                orig_res = res[:]

                for delete_after_string in delete_after_strings:
                    if delete_after_string in res:
                        starts = [m.start() for m in re.finditer(delete_after_string, res)]
                        res = res[:starts[0]].strip()
                    
                for end_after_string in end_after_strings:
                    if end_after_string in res:
                        res = res.split(end_after_string)[1].split("\n")[0].strip()
                        if len(res) != 0:
                            continue       

                if gt[0] == '"':
                    gt = gt[1:]
                if gt[-1] == '"':
                    gt = gt[:-1]

                # if gt1[0] == '"':
                #     gt1 = gt1[1:]
                # if gt1[-1] == '"':
                #     gt1 = gt1[:-1]

                if len(res) != 0:
                    if res[0] == '"':
                        res = res[1:]
                    if res[-1] == '"':
                        res = res[:-1]

                dist = distance(gt, res)
                total_dist += dist
                distances.append(dist)

                if gt == res:
                    count_correct += 1
                    corrects.append(1)
                else:
                    corrects.append(0)
                
                if chain_check and prompt_type == "text_cot":
                    # find counts of chain correct but not output correct
                    gt_chain = data_chain[idx].strip()
                    pred_chain = re.split(r'Original text:', orig_res)[0].strip()
                    if gt_chain == pred_chain:
                        if gt != res:
                            # desc(idx,gt_chain,pred_chain,gt,res)
                            chain_correct_op_incorrect += 1
                        else:
                            chain_correct_op_correct += 1
                    else:
                        if gt == res:
                            # desc()
                            chain_incorrect_op_correct += 1
                        else:
                            chain_incorrect_op_incorrect += 1
                # stats
                pred_nchars.append(len(res.strip()))
                input_nchars.append(len(gt.strip()))
                preds.append(res)
                gts.append(gt)

                count_total += 1
            result_dict = {"condition": condition, "accuracy": count_correct*1.0/count_total, "lev_dist": total_dist*1.0/count_total, "median_levdist": statistics.median(distances), "temp": temp}
            print(condition, "acc_inst", count_correct*1.0/count_total, "acc_demo", count_correct_demo*1.0/count_total, "levdist:", total_dist*1.0/count_total, "median levdist:", statistics.median(distances))

            ## For fine-grained analysis of 'unfaithfulness'
            if chain_check:
                result_dict.update({"chain_correct_op_correct" : chain_correct_op_correct, "chain_correct_op_incorrect" : chain_correct_op_incorrect, "chain_incorrect_op_correct" : chain_incorrect_op_correct, "chain_incorrect_op_incorrect" : chain_incorrect_op_incorrect})
                print("chain correct:")
                print("\toutput correct:", chain_correct_op_correct, "output incorrect:", chain_correct_op_incorrect)
                print("chain incorrect:")
                print("\toutput correct:", chain_incorrect_op_correct, "output incorrect:", chain_incorrect_op_incorrect)
                    
            if args.create_stats_table:
                with open(f'stimuli/{prompt_type}/{condition}.jsonl', 'r') as file:
                    input_text = []
                    for line in file:
                        json_obj = json.loads(line)
                        input_text.append(json_obj.get('input', ''))
                    
                ## write to huge tsv
                small_df["input_nchars"] =  input_nchars
                small_df["output_logprob"] =  bin_probs[fi_label]
                small_df["correct"] = corrects
                small_df["pred"] = preds
                small_df["gt"] = gts
                small_df["shift_level"] = [shift for _ in range(len(input_nchars))]
                small_df["shift_freq"] = [shift_freqs[shift-1] for _ in range(len(input_nchars))]
                small_df["input"] = input_text

                assert len(input_nchars) == len(pred_nchars) == len(bin_probs[fi_label]) == len(corrects)
                big_df = pd.concat([big_df, small_df], ignore_index=True)

    if args.create_stats_table: 
        big_df.to_csv(f"regression/{prompt_type}_train_table.tsv","\t",index_label="index")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--prompt_type", type=str, help="Prompt type to use [standard, text_cot, math_cot, number_cot]", default="text_cot")
    args.add_argument("--create_stats_table", action='store_true', help='default = False', default=False)
    args = args.parse_args()
    main(args)