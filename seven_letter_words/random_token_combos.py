
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

alphabet = "abcdefghijklmnopqrstuvwxyz"
alphabet_dict = {}
for char in alphabet:
    alphabet_dict[char] = 1

def is_roman_lower(string):
    for char in string:
        if char not in alphabet_dict:
            return False
    return True

all_threes_lower = []
all_fours_lower = []


for i in range(100256):
    token = enc.decode([i])
    if len(token) == 4:
        if token[0] == " " and is_roman_lower(token[1:]):
            all_threes_lower.append(token)
        elif is_roman_lower(token):
            all_fours_lower.append(token)

print(len(all_threes_lower), len(all_fours_lower), len(all_threes_lower)*len(all_fours_lower))
print(all_threes_lower[:10])
print(all_fours_lower[:10])
print("")

fo_lower = open("random_pairs_lower.txt", "w")

for start in all_threes_lower:
    for end in all_fours_lower:
        candidate = start.strip() + end.strip()
        tokens_unspaced = enc.encode(candidate)
        tokens_spaced = enc.encode(" " + candidate)

        if len(tokens_unspaced) == 2 and len(tokens_spaced) == 2:
            if len(enc.decode([tokens_unspaced[0]]).strip()) == 3 and len(enc.decode([tokens_unspaced[1]]).strip()) == 4 and len(enc.decode([tokens_spaced[0]]).strip()) == 3 and len(enc.decode([tokens_spaced[1]]).strip()) == 4:
                fo_lower.write(start.strip() + end.strip() + "\n")




