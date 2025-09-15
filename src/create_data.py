import os
import numpy as np
from src.classes import Debugger
from bitarray import bitarray
import concurrent.futures
from typing import List


def _create_bit_batch(num_decks: int) -> List[bytes]:
    deck_size = 52
    batch_bytes = []
    for _ in range(num_decks):
        deck = np.array([0] * 26 + [1] * 26, dtype=np.uint8)
        np.random.shuffle(deck)
        deck_bytes = []
        for i in range(0, deck_size, 8):
            byte = 0
            for bit in deck[i:i + 8]:
                byte = (byte << 1) | bit
            if i + 8 > deck_size:
                byte <<= (i + 8 - deck_size)
            deck_bytes.append(byte)
        batch_bytes.extend(deck_bytes)
    return batch_bytes


def _create_bitarray_batch(size: int) -> bitarray:
    batch = bitarray()
    for _ in range(size):
        deck = np.array([0] * 26 + [1] * 26, dtype=np.uint8)
        np.random.shuffle(deck)
        batch.extend(deck)
    return batch


@Debugger.debug
def create_deck_data_only_bits(num_decks=1_000_000, output_name='decks_bits.bin', batch_size=10000):
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_name)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        batches = [batch_size] * (num_decks // batch_size)
        if num_decks % batch_size:
            batches.append(num_decks % batch_size)

        futures = [executor.submit(_create_bit_batch, batch) for batch in batches]

        with open(output_path, 'wb') as f:
            for future in concurrent.futures.as_completed(futures):
                f.write(bytes(future.result()))

    print(f"Created {num_decks} shuffled decks in '{output_path}'")


@Debugger.debug
def create_deck_data_bitarray(num_decks=1_000_000, output_name='decks_bitarray.bin', batch_size=10000):
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_name)


    with concurrent.futures.ThreadPoolExecutor() as executor:
        batches = [batch_size] * (num_decks // batch_size)
        if num_decks % batch_size:
            batches.append(num_decks % batch_size)

        futures = [executor.submit(_create_bitarray_batch, batch) for batch in batches]

        with open(output_path, 'wb') as f:
            for future in concurrent.futures.as_completed(futures):
                future.result().tofile(f)

    print(f"Created {num_decks} shuffled decks in '{output_path}'")

