### Score created data files by tricks and cards won for each player in each game, there are only ever two players and they never choose the same color order
### Sorting by tricks involves 1 point for each set of three card colors matching a players choice of three card colors
### Sorting by cards won involves a point for each card before the winning three card colors matching a players choice of three card colors including the three cards
### ensure the tricks counting does not go out of range
import os
import numpy as np
from typing import Tuple
from bitarray import bitarray

def _score_bitarray_deck(deck: bitarray) -> Tuple[int, int]:
    player1_tricks = 0
    player2_tricks = 0
    player1_cards = 0
    player2_cards = 0

    # Scoring by tricks (sets of three)
    for i in range(0, 52, 3):
        if i + 3 > 52:
            break
        triplet = deck[i:i + 3]
        if triplet.count(1) > triplet.count(0):
            player2_tricks += 1
        elif triplet.count(0) > triplet.count(1):
            player1_tricks += 1

    # Scoring by cards won (including the winning triplet)
    for i in range(52):
        if deck[i] == 1:
            player2_cards += 1
        else:
            player1_cards += 1

    return (player1_tricks, player2_tricks), (player1_cards, player2_cards)

def score_deck_data_bitarray(input_name='decks_bitarray.bin', output_name='scores_bitarray.npy'):
    input_dir = 'data'
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(input_dir, input_name)
    output_path = os.path.join(output_dir, output_name)

    scores = []

    with open(input_path, 'rb') as f:
        deck_size = 52
        byte_size = (deck_size + 7) // 8
        while True:
            deck_bytes = f.read(byte_size)
            if not deck_bytes:
                break
            deck = bitarray()
            deck.frombytes(deck_bytes)
            deck = deck[:deck_size]  # Ensure we only take the first 52 bits
            score_tricks, score_cards = _score_bitarray_deck(deck)
            scores.append(score_tricks + score_cards)

    scores_array = np.array(scores, dtype=np.uint8)
    np.save(output_path, scores_array)

