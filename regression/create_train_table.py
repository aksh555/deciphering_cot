import os
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

df = pd.read_csv("text_cot_train_table.tsv",sep="\t")
word_list = df["input"].to_list()
print("Rows", len(word_list))

words_with_prob = []
this_batch_sentences = []
this_batch_words = []
num_tokens = []
for index, line in enumerate(word_list):
    if index % 10000 == 0:
        logging.info(str(index))

    word = line.strip()

    tokens = gpt4_enc.encode(word)
    tokens_spaced = gpt4_enc.encode(" " + word)

    this_batch_sentences.append('The word is "' + word + '"')
    this_batch_words.append(word)
    num_tokens.append(len(tokens))

    if len(this_batch_sentences) == 3000:
        logprobs = prob_gpt2(this_batch_sentences)
        for word, logprob in zip(this_batch_words, logprobs):
            words_with_prob.append(logprob.item())
        this_batch_sentences = []
        this_batch_words = []

if len(this_batch_sentences) > 0:
    logprobs = prob_gpt2(this_batch_sentences)
    for word, logprob in zip(this_batch_words, logprobs):
        words_with_prob.append(logprob.item())
    this_batch_sentences = []
    this_batch_words = []

df["input_logprob"] = words_with_prob
df["input_ntokens"] = num_tokens

df.drop(["pred","gt","input"], axis=1, inplace=True)
df = df[['input_ntokens', 'input_logprob', 'output_logprob', 'shift_level', 'shift_freq', 'bin']]
df.to_csv("./text_cot_train_table.tsv", "\t",index_label="index")






