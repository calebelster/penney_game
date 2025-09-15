import unittest
import time
import tracemalloc
import os
import statistics
from bitarray import bitarray
from src.create_data import create_deck_data_only_bits, create_deck_data_bitarray

class TestDeckCreation(unittest.TestCase):
    NUM_DECKS = 100_000
    BATCH_SIZE = 1_000
    NUM_RUNS = 5

    def check_deck_validity_bits(self, filename):
        with open(filename, 'rb') as f:
            data = f.read(7)
            bits = []
            for i in range(52):
                byte_index = i // 8
                bit_index = 7 - (i % 8)
                bit = (data[byte_index] >> bit_index) & 1
                bits.append(bit)
            self.assertEqual(bits.count(1), 26)
            self.assertEqual(bits.count(0), 26)

    def check_deck_validity_bitarray(self, filename):
        with open(filename, 'rb') as f:
            ba = bitarray()
            ba.fromfile(f, 7)
            deck = ba[:52]
            self.assertEqual(deck.count(1), 26)
            self.assertEqual(deck.count(0), 26)

    def measure_performance(self, func, filename):
        times = []
        peaks = []
        for _ in range(self.NUM_RUNS):
            if os.path.exists(filename):
                os.remove(filename)
            tracemalloc.start()
            start = time.perf_counter()
            func(num_decks=self.NUM_DECKS, batch_size=self.BATCH_SIZE)
            elapsed = time.perf_counter() - start
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            times.append(elapsed)
            peaks.append(peak)
            if os.path.exists(filename):
                os.remove(filename)
        return times, peaks

    def test_bits_creation(self):
        filename = 'data/decks_bits.bin'
        self.addCleanup(lambda: os.path.exists(filename) and os.remove(filename))
        times, peaks = self.measure_performance(create_deck_data_only_bits, filename)
        print(f"Bits: time (s) avg={statistics.mean(times):.4f}, median={statistics.median(times):.4f}, min={min(times):.4f}, max={max(times):.4f}")
        print(f"Bits: peak mem (KiB) avg={statistics.mean(peaks)/1024:.2f}, median={statistics.median(peaks)/1024:.2f}, min={min(peaks)/1024:.2f}, max={max(peaks)/1024:.2f}")
        # Run once more for validity check
        create_deck_data_only_bits(num_decks=self.NUM_DECKS, batch_size=self.BATCH_SIZE)
        self.assertTrue(os.path.exists(filename))
        self.check_deck_validity_bits(filename)
        os.remove(filename)

    def test_bitarray_creation(self):
        filename = 'data/decks_bitarray.bin'
        self.addCleanup(lambda: os.path.exists(filename) and os.remove(filename))
        times, peaks = self.measure_performance(create_deck_data_bitarray, filename)
        print(f"Bitarray: time (s) avg={statistics.mean(times):.4f}, median={statistics.median(times):.4f}, min={min(times):.4f}, max={max(times):.4f}")
        print(f"Bitarray: peak mem (KiB) avg={statistics.mean(peaks)/1024:.2f}, median={statistics.median(peaks)/1024:.2f}, min={min(peaks)/1024:.2f}, max={max(peaks)/1024:.2f}")
        # Run once more for validity check
        create_deck_data_bitarray(num_decks=self.NUM_DECKS, batch_size=self.BATCH_SIZE)
        self.assertTrue(os.path.exists(filename))
        self.check_deck_validity_bitarray(filename)
        os.remove(filename)


if __name__ == '__main__':
    unittest.main()