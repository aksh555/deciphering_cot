import random

all_scores, all_words = [], []

with open("seven_letter_words/random_pairs_lower_scored.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        score, word = line.split()
        all_scores.append(float(score))
        all_words.append(word)
    
# Function to select 100 words closest to a given score
def select_closest_words(score, num_words=150):

    # Sort the scores based on proximity to the target score
    sorted_indices = sorted(range(len(all_scores)), key=lambda i: abs(all_scores[i] - score))

    # Select the 100 closest words
    selected_indices = sorted_indices[:num_words]
    selected_words = [all_words[i] for i in selected_indices]
    scores = [all_scores[i] for i in selected_indices]

    return [selected_words, scores]

# Select 100 words closest to each specified score level
selected_words_closest_to_levels = {}
selected_words = []
for score_level in [-15, -22.5, -30, -37.5, -45]:
    selected_words_closest_to_levels[score_level] = select_closest_words(score_level)
    selected_words += selected_words_closest_to_levels[score_level][0]

selected_words = set(selected_words)
print("Number of selected words: " + str(len(selected_words)))

with open("seven_letter_words/words_5bins.txt", "w") as f:
    for score in [-15, -22.5, -30, -37.5, -45]:
        for word,sc in zip(selected_words_closest_to_levels[score][0], selected_words_closest_to_levels[score][1]):
            f.write(word + " " + str(sc) + "\n")
