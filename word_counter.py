import sys
import string
import os

if len(sys.argv) < 3:
    print("Usage: python word_counter.py <filename> <N>")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.exists(filename):
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)

try:
    N = int(sys.argv[2])
except ValueError:
    print("Error: N must be a number.")
    sys.exit(1)

with open(filename, 'r', encoding='utf-8') as file:
    text = file.read().lower()
for char in string.punctuation:
    text = text.replace(char, '')

words = text.split()

word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

sorted_word_count = sorted(word_count.items(), key=lambda item: item[1], reverse=True)

if N > len(sorted_word_count):
    print("Error: N is larger than the number of unique words.")
    sys.exit(1)

for word, count in sorted_word_count[:N]:
    times = "time" if count == 1 else "times"
    print(f'The word "{word}" appears {count} {times}')