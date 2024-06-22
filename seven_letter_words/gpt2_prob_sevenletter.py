
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import tiktoken
import logging

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


for finame in ["random_pairs_lower"]:
    fi = open(finame + ".txt", "r")
    fo = open(finame + "_scored.txt", "w")

    words_with_prob = []

    this_batch_sentences = []
    this_batch_words = []
    for index, line in enumerate(fi):
        if index % 10000 == 0:
            logging.info(str(index))
    
        word = line.strip()

        tokens = gpt4_enc.encode(word)
        tokens_spaced = gpt4_enc.encode(" " + word)

        if len(tokens) == 2 and len(tokens_spaced) == 2 and len(word) == 7:
            token1 = gpt4_enc.decode([tokens[0]]).strip()
            token2 = gpt4_enc.decode([tokens[1]]).strip()

            tokenspaced1 = gpt4_enc.decode([tokens_spaced[0]]).strip()
            tokenspaced2 = gpt4_enc.decode([tokens_spaced[1]]).strip()

            if len(token1) == 3 and len(token2) == 4 and len(tokenspaced1) == 3 and len(tokenspaced2) == 4:
                this_batch_sentences.append('The word is "' + word + '"')
                this_batch_words.append(word)
            else:
                print(index, "Wrong length", word, len(token1), len(token2), len(tokenspaced1), len(tokenspaced2))
        else:
            print(index, "Wrong length", word, len(tokens), len(tokens_spaced), len(word))

        if len(this_batch_sentences) == 3000:
            logprobs = prob_gpt2(this_batch_sentences)
            for word, logprob in zip(this_batch_words, logprobs):
                words_with_prob.append([logprob.item(), word])
            this_batch_sentences = []
            this_batch_words = []

    if len(this_batch_sentences) > 0:
        logprobs = prob_gpt2(this_batch_sentences)
        for word, logprob in zip(this_batch_words, logprobs):
            words_with_prob.append([logprob.item(), word])
        this_batch_sentences = []
        this_batch_words = []

    for prob, word in sorted(words_with_prob)[::-1]:
        fo.write(str(prob) + "\t" + word + "\n")




