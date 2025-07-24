import sys
import string

with open('generic_text.txt', 'r') as file:
    text = file.read().lower()

for char in string.punctuation:
    text = text.replace(char, '')

words = text.split()

word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

sorted_word_count = sorted(word_count.items(), key=lambda item: item[1], reverse=True)

try:
    N = int(sys.argv[1])
except (IndexError, ValueError):
    print("Error: Please provide a valid number N as a command-line argument.")
    sys.exit(1)

if N > len(sorted_word_count):
    print("Error: N exceeds the number of unique words in the file.")
    sys.exit(1)

for word, count in sorted_word_count[:N]:
    print(f'The word "{word}" appears {count} times')
