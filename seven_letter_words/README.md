## Dataset
1. First, run `python random_token_combos.py`. This generates `random_pairs_lower.txt`, which lists all words that fulfill the following criteria:
    - 7 letters long
    - 2 subword tokens long (using the tokenizer that both GPT-3.5 and GPT-4 use; it needs to be 2 tokens long whether the word follows a space or not)
    - The first subword token is 3 letters long, and the second is 4 letters long (again, these lengths need to be identical whether the word follows a space or not).
2. Then, sort these words by the probability assigned to them by GPT-2 by running `python gpt2_prob_sevenletter.py`. This generates `random_pairs_lower_scored.txt`, which lists each word along with a log probability. The log probability is computed as the log probability that GPT-2 assigns to the sentence `The word is "WORD"`, minus the log probability that it assigns to `The word is "'; thus, this yields the log probability assigned to just the word and the following quotation mark in the context of `The word is "`. The closing quotation mark is included because it serves to indicate the end of the word.
3. Then, bin the words by running `python select_words.py` to create `words_5bins.txt`.
4. The final list of words can be found in `bin1_prob.txt`, `bin2_prob.txt`, `bin3_prob.txt`, `bin4_prob.txt`, and `bin5_prob.txt`. 
