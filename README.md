# deciphering_cot

Code implementation and data for the paper: 

**[Deciphering the Factors Influencing the Efficacy of Chain-of-Thought: Probability, Memorization, and Noisy Reasoning](https://arxiv.org/abs/2407.01687)**

[Akshara Prabhakar](https://aksh555.github.io/), [Thomas L. Griffiths](https://cocosci.princeton.edu/tom/index.php), [R. Thomas McCoy](https://rtmccoy.com/)

## Overview
### Data
We construct a dataset of seven-letter words divided into 5 probability bins {bin1 to bin 5} each having around 150 words (first 100 to evaluate GPT-4 and remaining to evaluate the logistic regression model that was fitted on the first 100 words). The binning is done based on the log probability value assigned by GPT-2. 

The seven-letter word dataset is in [seven_letter_words](seven_letter_words):
- bin1_prob.txt
- bin2_prob.txt
- bin3_prob.txt
- bin4_prob.txt
- bin5_prob.txt

### Stimuli
Using the dataset prepared earlier, we prepare stimuli -- these are shift cipher encoded versions of the words from the 5 probability bins across 25 shift levels (1 to 25).

The stimuli are prepared for the different types of prompts we use: `standard`, `text_cot`, `math_cot`, `number_cot`.

Can be created by running,
```bash
python stimulus_generator.py --prompt_type text_cot 
```

### GPT-4 evaluation
GPT-4 decoding experiments can be run using the `run_openai.py` script. 
An OpenAI key must be set in the environemnt before doing so using
```bash
echo "export OPENAI_API_KEY='yourkey'" >> ~/.zshrc
source ~/.zshrc
```

Create a `logs` directory to save the logs.
For example to run experiments with Text-CoT for shift_level=1 across all 5 bins,
```bash
python run_openai.py --tasks text_cot1 --conditions bin1,bin2,bin3,bin4,bin5 --max_tokens 200 --prompt_type text_cot
```

To evaluate the GPT-4 generations, run
```bash 
python eval.py --prompt_type text_cot --create_stats_table
```
Run this after evaluating GPT-4 across all shift levels and bins. This will generate the evluation statistics for `text_cot` across all shift levels and the `{prompt_type}_train_table.tsv` file which is the train statistics table for fitting the logistic regression.

### Logistic regression
The logistic regression is implemented in R in [regression.ipynb](regression/regression.ipynb). The predictions on the test set are saved in `regression/text_cot_test_results.tsv`.

### Outputs
All GPT-4 generations and ouputs are stored in the `logs` directory.

## Citation
If you find this repository helpful, feel free to cite our [publication](https://arxiv.org/abs/2407.01687).
```
@misc{prabhakar2024decipheringfactorsinfluencingefficacy,
      title={Deciphering the Factors Influencing the Efficacy of Chain-of-Thought: Probability, Memorization, and Noisy Reasoning}, 
      author={Akshara Prabhakar and Thomas L. Griffiths and R. Thomas McCoy},
      year={2024},
      eprint={2407.01687},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2407.01687}, 
}
```
