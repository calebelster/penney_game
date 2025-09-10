import os
import numpy as np

num_decks = 1_000_000
deck_size = 52
output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'decks.bin')

with open(output_path, 'wb') as f:
    for _ in range(num_decks):
        deck = np.array([0]*26 + [1]*26, dtype=np.uint8)
        np.random.shuffle(deck)
        for i in range(0, deck_size, 8):
            byte = 0
            for bit in deck[i:i+8]:
                byte = (byte << 1) | bit
            if i + 8 > deck_size:
                byte <<= (i + 8 - deck_size)
            f.write(bytes([byte]))
print(f"Created {num_decks} shuffled decks in '{output_path}'")
# Each deck is represented as 52 bits (0 for red, 1 for black), packed into 7 bytes.