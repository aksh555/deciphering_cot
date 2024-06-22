bins = ["bin_3", "bin_4", "bin_5"]

words = []
for bin in bins:
    with open(f"./{bin}.txt") as file:
        words.extend([line.strip() for line in file])

# import tiktoken
# from collections import defaultdict
# gpt4_enc = tiktoken.get_encoding("cl100k_base")

# score_words_dict = defaultdict(list)

# for word in words:
#     tokens = len(gpt4_enc.encode(word))
#     score_words_dict[tokens].append(word)

alphabet = "abcdefghijklmnopqrstuvwxyz"
index2char = {}
char2index = {}
for index, char in enumerate(alphabet):
    index2char[index] = char
    char2index[char] = index

# similar_pairs = []
# for score, words_with_score in score_words_dict.items():
#     for i in range(len(words_with_score)):
#         word1 = words_with_score[i]
#         word2 = ""
#         for char in word1:
#             word2 += index2char[(char2index[char]+25)%26] 
#         print(word1, word2)
#         if word2 in words:
#             similar_pairs.append((word1, word2))

# print(len(similar_pairs))
# print(similar_pairs)


import os
os.environ['TRANSFORMERS_CACHE'] = "/n/fs/codeval/cache"
os.environ['HF_DATASETS_CACHE'] = "/n/fs/codeval/cache"
os.environ['HF_HOME'] = "/n/fs/codeval/cache"
os.environ['HF_HUB_CACHE'] = "/n/fs/codeval/cache"

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import tiktoken
import logging
import json
import pandas as pd

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, handlers=[logging.StreamHandler(),logging.FileHandler("prob_random_index.log")])

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2-xl")
gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2-xl").to(device)
gpt4_enc = tiktoken.get_encoding("cl100k_base")

def pad_batch(batch, pad_idx):
    max_length = 0
    for seq in batch:
        if len(seq) > max_length:
            max_length = len(seq)

    new_batch = []
    for seq in batch:
        padding = [pad_idx for i in range(max_length - len(seq))]
        new_batch.append(seq + padding)

    return new_batch

# Get perplexity using GPT-2
def prob_gpt2(sentence_list):

    # Tokenize the sentences
    all_tokens = []
    for sentence in sentence_list:
        tokens = gpt2_tokenizer.encode(sentence)
        all_tokens.append(tokens)
    tokens = pad_batch(all_tokens, 50256)

    targets = tokens[:]

    # Compute average log likelihood for the generation
    input_ids = torch.LongTensor(tokens).to(device)
    target_ids = torch.LongTensor(targets).to(device)

    with torch.no_grad():
        outputs = gpt2_model(input_ids, labels=target_ids)
        logits = outputs[1]
        logits = logits.transpose(0,1)[:-1].transpose(0,1)
        target_ids = target_ids.transpose(0,1)[1:].transpose(0,1)
        loss = torch.nn.CrossEntropyLoss(reduction="none", ignore_index=50256)(logits.reshape(-1,50257), target_ids.reshape(-1))
        loss = loss.reshape(target_ids.shape).sum(dim=1)
        neg_log_likelihood = -1*loss


    # 13.357776641845703 = logprob('The word is"'); removing this to just get
    # the word prob
    return neg_log_likelihood + 13.357776641845703


# folder_path = "/n/fs/codeval/embers-of-autoregression/extension/stimuli/word/"
# file_list = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])[:1]
file_list = [1]

num_token_mis = 0
for finame in file_list:
    # print(finame, end="**\n")
    # with open(finame, 'r') as f:
    #     lines = f.readlines()
    # lines = [json.loads(line) for line in lines]
    # fi = [line['input'] for line in lines]
    # print("Lines", len(fi))
    # fo = open("input_scored.txt", "a")
    word_list = words
    print("Lines", len(word_list))

    words_with_prob = []
    word_pairs = []

    this_batch_sentences = []
    this_batch_word1s = []
    this_batch_words = []
    num_tokens = []
    for index, line in enumerate(word_list):
        if index % 10000 == 0:
            logging.info(str(index))
    
        word = line.strip()
        check_shifts = [2]
        for check_shift in check_shifts:
            word2 = ""
            word1 = ""
            for char in word:
                word1 += index2char[(char2index[char]+1)%26]
                word2 += index2char[(char2index[char]+check_shift)%26]

            tokens = gpt4_enc.encode(word1)
            tokens_word2 = gpt4_enc.encode(word2)
            if len(tokens) > 4 or len(tokens) != len(tokens_word2):
                # print(word1, word2, len(tokens), len(tokens_word2))
                num_token_mis += 1
                continue

            tokens_spaced = gpt4_enc.encode(" " + word2)

            this_batch_sentences.append('The word is "' + word2 + '"')
            this_batch_words.append(word2)
            num_tokens.append(len(tokens))
            this_batch_word1s.append(word1)

        # if len(tokens) == 2 and len(tokens_spaced) == 2 and len(word) == 7:
        #     token1 = gpt4_enc.decode([tokens[0]]).strip()
        #     token2 = gpt4_enc.decode([tokens[1]]).strip()

        #     tokenspaced1 = gpt4_enc.decode([tokens_spaced[0]]).strip()
        #     tokenspaced2 = gpt4_enc.decode([tokens_spaced[1]]).strip()

        #     if len(token1) == 3 and len(token2) == 4 and len(tokenspaced1) == 3 and len(tokenspaced2) == 4:
        #         this_batch_sentences.append('The word is "' + word + '"')
        #         this_batch_words.append(word)
        #     else:
        #         print(index, "Wrong length", word, len(token1), len(token2), len(tokenspaced1), len(tokenspaced2))
        # else:
        #     print(index, "Wrong length", word, len(tokens), len(tokens_spaced), len(word))

        if len(this_batch_sentences) == 3000:
            logprobs = prob_gpt2(this_batch_sentences)
            for word1, word2, logprob in zip(this_batch_word1s, this_batch_words, logprobs):
                words_with_prob.append(logprob.item())
                if logprob.item() >= -45 and logprob.item() < -30:
                    word_pairs.append([word1, word2])
            this_batch_sentences = []
            this_batch_words = []
            this_batch_word1s = []

    if len(this_batch_sentences) > 0:
        logprobs = prob_gpt2(this_batch_sentences)
        for word1, word2, logprob in zip(this_batch_word1s, this_batch_words, logprobs):
                words_with_prob.append(logprob.item())
                if logprob.item() > -45 and logprob.item() < -30:
                    x = prob_gpt2(['The word is "' + word1 + '"'])[-1].item()
                    if x > -45 and x < -30:
                        word_pairs.append([word1, word2])
                        print("missed 2", word1, word2, x, logprob.item())
        this_batch_sentences = []
        this_batch_words = []
        this_batch_word1s = []

print(num_token_mis)
print(len(word_pairs))
f = open("./word_pairs_lowbins.txt", 'a+')
for pair in word_pairs:
    f.write(pair[0] + "\t" + pair[1] + "\n")

f.close()


