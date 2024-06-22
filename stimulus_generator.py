
import jsonlines
import os
import random
import argparse

# Functions for encoding in rot-1 or rot-3
alphabet = "abcdefghijklmnopqrstuvwxyz"
index2char = {}
char2index = {}
for index, char in enumerate(alphabet):
    index2char[index] = char
    char2index[char] = index


def rot_encode(sequence, n):
    new_sequence = []
    for char in sequence:
        if not char.isalpha():
            new_sequence.append(char)
        elif char.isupper():
            index = char2index[char.lower()]
            new_char = index2char[(index+n) % 26]
            new_sequence.append(new_char.upper())
        else:
            index = char2index[char]
            new_char = index2char[(index+n) % 26]
            new_sequence.append(new_char)

    return "".join(new_sequence)


def create_chain(sequence, n):
    chain = []
    for index, char in enumerate(sequence):
        new_char = rot_encode(char, 26-n)
        chain.append(str(index+1) + ". " + char + " -> " + new_char + "\n")
    return "".join(chain)


def create_math_cot_chain(sequence, n):
    s = f'''Let’s start by writing the letter-position mapping for the alphabet:
a -> 0
b -> 1
c -> 2
d -> 3
e -> 4
f -> 5
g -> 6
h -> 7
i -> 8
j -> 9
k -> 10
l -> 11
m -> 12
n -> 13
o -> 14
p -> 15
q -> 16
r -> 17
s -> 18
t -> 19
u -> 20
v -> 21
w -> 22
x -> 23
y -> 24
z -> 25

Next, we find the encoded letter as follows:
Position of original letter = (Position of given letter − {n}) mod 26 

Then map the found position to the corresponding letter using the letter-position mapping.

Using this,\n
'''
    chain = []
    for index, char in enumerate(sequence):
        new_char = rot_encode(char, 26-n)
        chain.append(str(index+1) + ". " + char + " -> " +
                     f"({char2index[char]} - {n}) mod 26" " -> " + new_char + "\n")
    return s + "".join(chain)


def create_number_cot_chain(sequence, n):
    s = f'''
New position = (Given position − {n}) mod 26
Using this,\n
'''
    chain = []
    for index, char in enumerate(sequence):
        new_char = rot_encode(char, 26-n)
        chain.append(str(index+1) + ". " + str(char2index[char]) + " -> " +
                     f"({char2index[char]} - {n}) mod 26" " -> " + str(char2index[new_char]) + "\n")
    return s + "".join(chain)


def create_step_chain_forward(sequence, n):
    chain = []
    for index, char in enumerate(sequence):
        new_char = rot_encode(char, 26-n)
        start_ord, end_ord = ord(char), ord(new_char)
        part_chain = ""
        if char == new_char:
            part_chain = new_char + " -> " + new_char
        else:
            if start_ord > end_ord:
                if char.isupper():
                    end_ord = ord("Z")
                else:
                    end_ord = ord("z")
            for char_ord in range(start_ord, end_ord+1, 1):
                part_chain += chr(char_ord)
                if char_ord != end_ord:
                    part_chain += " -> "
            if char_ord != ord(new_char):
                part_chain += " -> "
                if char.isupper():
                    start_ord = ord("A")
                else:
                    start_ord = ord("a")
                for char_ord in range(start_ord, ord(new_char)+1, 1):
                    part_chain += chr(char_ord)
                    if char_ord != ord(new_char):
                        part_chain += " -> "

        chain.append(str(index+1) + ". " + part_chain + "\n")
    return "".join(chain)


def create_math_corrupt_chain(sequence, n):
    chain = []
    s = f'''Let’s start by writing the letter-position mapping for the alphabet:
a -> 0
b -> 1
c -> 2
d -> 3
e -> 4
f -> 5
g -> 6
h -> 7
i -> 8
j -> 9
k -> 10
l -> 11
m -> 12
n -> 13
o -> 14
p -> 15
q -> 16
r -> 17
s -> 18
t -> 19
u -> 20
v -> 21
w -> 22
x -> 23
y -> 24
z -> 25

Next, we find the encoded letter as follows:
Position of original letter = (Position of given letter − {n}) mod 26 

Then map the found position to the corresponding letter using the letter-position mapping.

Using this,\n
'''
    chain = []
    for index, char in enumerate(sequence):
        new_char = '*'
        chain.append(str(index+1) + ". " + char + " -> " +
                     f"({char2index[char]} - {n}) mod 26" " -> " + new_char + "\n")
    return s + "".join(chain)


def create_corrupt_chain(sequence, n):
    chain = []
    for index, char in enumerate(sequence):
        # random character, letter, or number, punctuation
        # candidates = list(alphabet) + [x.upper() for x in list(alphabet)] + list("0123456789") + list(".,?!:;\"'()[]{}")
        # replace 50% of the time
        # if random.random() < 0.5:
        # new_char = random.choice(candidates)
        # else:
        #     new_char = rot_encode(char, 26-n)
        # if not char.isalpha():
        #     new_char = char
        # else:
        new_char = "*"
        chain.append(str(index+1) + ". " + char + " -> " + new_char + "\n")
    return "".join(chain)


# print(rot_encode("stay", 1))
# print(rot_encode("stay", 3))


def create_swap_chain(sequence, n):
    chain = []
    for index, char in enumerate(sequence):
        new_char = rot_encode(char, 26-n)
        chain.append(str(index+1) + ". " + char + " -> " + new_char + "\n")
    return "".join(chain)


def string_to_seq(msg):
    seq = ""
    for char in msg:
        seq += str(char2index[char]) + ","
    return seq[:-1]

def main(args):
    data = [
        ("examples/bin_1.txt", "bin1"),
        ("examples/bin_2.txt", "bin2"),
        ("examples/bin_3.txt", "bin3"),
        ("examples/bin_4.txt", "bin4"),
        ("examples/bin_5.txt", "bin5")
    ]
    prompt_type = args.prompt_type
    fo_directory = f"stimuli1/{prompt_type}"

    if not os.path.exists(fo_directory):
        os.makedirs(fo_directory, exist_ok=True)

    for shift in range(1, 26):
        for task in ["dec"]:
            for fi_name, fi_label in data:
                fo_name = f"{fo_directory}/{prompt_type+str(shift)}_{fi_label}.jsonl"

                fi = open(fi_name, "r")
                fo = open(fo_name, "w")
                jsl = jsonlines.Writer(fo)

                count_encoded = 0
                for line_num, line in enumerate(fi):
                    example = {}

                    # Task
                    example["task_name"] = "rot-" + str(shift)

                    # Condition
                    example_type = fo_name.split("_")[1].split(".")[0]
                    example["example_type"] = example_type

                    word = line.strip().split("\t")[0]
                    sentence = word
                    # sentence1 = line.strip().split("\t")[0]
                    encoded = rot_encode(word, shift)

                    # Instruction
                    if task == "dec":
                        if shift == 1:
                            if prompt_type == "standard":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' position forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ' along with the original text that it was created from:\nRot-' + str(
                                    shift) + ' text: "' + rot_encode("Stay here!", shift) + '"\nOriginal text: "Stay here!"\n\nHere is another message in rot-' + str(shift) + '. Decode this message to produce the original text:\nRot-' + str(shift) + ' text: "%s"\nOriginal text:'
                            elif prompt_type == "text_cot":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' position forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("stay", shift) + '"\n\nTo decode this message, we shift each letter ' + str(
                                    shift) + ' position backward.' + create_chain(rot_encode("stay", shift), shift) + '\nTherefore, the original text is: "Stay"\n\nHere is another message in rot-' + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "math_cot":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' position forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("stay", shift) + '"\n\nTo decode this message, we need to shift each letter ' + str(
                                    shift) + ' position backward. ' + create_math_cot_chain(rot_encode("stay", shift), shift) + '\nTherefore, the original text is: "stay"\n\nHere is another message in rot-' + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "number_cot":
                                example["task_instruction"] = 'Shift-' + str(shift) + ' is a process in which each number is shifted ' + str(shift) + ' position forward until it reaches 26 and subsequently circles back to 1. For example, here is a sequence of numbers written in shift-' + str(shift) + ':\shift-' + str(shift) + ' sequence: "' + string_to_seq(rot_encode("stay", shift)) + '"\n\nTo decode this sequence, we need to shift each number ' + str(
                                    shift) + ' position backward. ' + create_number_cot_chain(rot_encode("stay", shift), shift) + '\nTherefore, the original sequence of numbers is: ' + f'"{string_to_seq("stay")}"' + '\n\nHere is another sequence of numbers in shift-' + str(shift) + '. Decode this sequence one number at a time. On the last line, write the words "Original sequence:" followed by the decoded sequence:\nshift-' + str(shift) + ' sequence: "%s"'
                        else:
                            if prompt_type == "standard":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' positions forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ' along with the original text that it was created from:\nRot-' + str(
                                    shift) + ' text: "' + rot_encode("Stay here!", shift) + '"\nOriginal text: "Stay here!"\n\nHere is another message in rot-' + str(shift) + '. Decode this message to produce the original text:\nRot-' + str(shift) + ' text: "%s"\nOriginal text:'
                            elif prompt_type == "text_cot":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' positions forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("stay", shift) + '"\n\nTo decode this message, we shift each letter ' + str(
                                    shift) + ' positions backward:\n' + create_chain(rot_encode("stay", shift), shift) + '\nTherefore, the original text is: "stay"\n\nHere is another message in rot-' + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "cot_hidden_1":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' positions forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("Stay here!", shift) + '"\n\nTo decode this message, we shift each letter ' + str(shift) + " positions backward; but instead of revealing what each letter becomes, we will replace it with a '*' until we write the final answer:\n" + create_corrupt_chain(
                                    rot_encode("Stay here!", shift), shift) + """\nIf we put together the letters that were hidden behind each '*', we get that the original text is: "Stay here!"\n\nHere is another message in rot-""" + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "math_cot":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' position forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("stay", shift) + '"\n\nTo decode this message, we need to shift each letter ' + str(
                                    shift) + ' positions backward. ' + create_math_cot_chain(rot_encode("stay", shift), shift) + '\nTherefore, the original text is: "stay"\n\nHere is another message in rot-' + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "number_cot":
                                example["task_instruction"] = 'Shift-' + str(shift) + ' is a process in which each number is shifted ' + str(shift) + ' positions forward until it reaches 26 and subsequently circles back to 1. For example, here is a sequence of numbers written in shift-' + str(shift) + ':\shift-' + str(shift) + ' sequence: "' + string_to_seq(rot_encode("stay", shift)) + '"\n\nTo decode this sequence, we need to shift each number ' + str(
                                    shift) + ' positions backward. ' + create_number_cot_chain(rot_encode("stay", shift), shift) + '\nTherefore, the original sequence of numbers is:' + f'"{string_to_seq("stay")}"' + '\n\nHere is another sequence of numbers in shift-' + str(shift) + '. Decode this sequence one number at a time. On the last line, write the words "Original sequence:" followed by the decoded sequence:\nshift-' + str(shift) + ' sequence: "%s"'
                            elif prompt_type == "one-step-fwd":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' positions forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("Stay here!", shift) + '"\n\nTo decode this message, we shift each letter ' + str(
                                    26-shift) + ' positions forward one step at a time:\n' + create_step_chain_forward(rot_encode("Stay here!", shift), shift) + '\nTherefore, the original text is: "Stay here!"\n\nHere is another message in rot-' + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "math_swap":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' positions forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("stay", shift+1) + '"\n\nTo decode this message, we shift each letter ' + str(
                                    shift) + ' positions backward:\n' + create_math_cot_chain(rot_encode("stay", shift+1), shift+1) + '\nTherefore, the original text is: "stay"\n\nHere is another message in rot-' + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'
                            elif prompt_type == "math_corrupt":
                                example["task_instruction"] = 'Rot-' + str(shift) + ' is a cipher in which each letter is shifted ' + str(shift) + ' positions forward in the alphabet. For example, here is a message written in rot-' + str(shift) + ':\nRot-' + str(shift) + ' text: "' + rot_encode("stay", shift) + '"\n\nTo decode this message, we shift each letter ' + str(shift) + " positions backward; but instead of revealing what each letter becomes, we will replace it with a '*' until we write the final answer:\n" + create_math_corrupt_chain(
                                    rot_encode("stay", shift), shift) + """\nIf we put together the letters that were hidden behind each '*', we get that the original text is: "stay"\n\nHere is another message in rot-""" + str(shift) + '. Decode this message one letter at a time. On the last line, write the words "Original text:" followed by the decoded message:\nRot-' + str(shift) + ' text: "%s"'

                    # Input and correct output
                    if task == "dec":
                        example["input"] = encoded
                        example["correct_output"] = sentence
                    else:
                        example["input"] = sentence
                        example["correct_output"] = encoded

                    # Combining the instruction and input (this is the string that should be given to the model)
                    example["instruction_plus_input"] = example["task_instruction"] % example["input"]

                    jsl.write(example)

                    count_encoded += 1
                    if count_encoded == 100:
                        break

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--prompt_type", type=str, help="Prompt type to use [standard, text_cot, math_cot, number_cot]", default="text_cot")
    args = args.parse_args()
    main(args)