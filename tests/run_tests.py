import unittest
import time
import tracemalloc
import os
import statistics
from bitarray import bitarray
from src.create_data import create_deck_data_only_bits, create_deck_data_bitarray


class TestDeckCreation(unittest.TestCase):
    NUM_DECKS = 1_000_000
    BATCH_SIZE = 10_000
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
        sizes = []
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
                sizes.append(os.path.getsize(filename))
                os.remove(filename)
        return times, peaks, sizes

    def print_stats(self, label, times, peaks, sizes):
        print(
            f"{label}: time (s) avg={statistics.mean(times):.4f}, std={statistics.stdev(times):.4f}, "
            f"median={statistics.median(times):.4f}, min={min(times):.4f}, max={max(times):.4f}"
        )
        print(
            f"{label}: peak mem (KiB) avg={statistics.mean(peaks)/1024:.2f}, std={statistics.stdev(peaks)/1024:.2f}, "
            f"median={statistics.median(peaks)/1024:.2f}, min={min(peaks)/1024:.2f}, max={max(peaks)/1024:.2f}"
        )
        print(
            f"{label}: file size (bytes) avg={statistics.mean(sizes):.2f}, std={statistics.stdev(sizes):.2f}, "
            f"median={statistics.median(sizes):.2f}, min={min(sizes)}, max={max(sizes)}"
        )

    def test_bits_creation(self):
        filename = 'data/decks_bits.bin'
        self.addCleanup(lambda: os.path.exists(filename) and os.remove(filename))
        times, peaks, sizes = self.measure_performance(create_deck_data_only_bits, filename)
        self.print_stats("Bits", times, peaks, sizes)
        # Run once more for validity check
        create_deck_data_only_bits(num_decks=self.NUM_DECKS, batch_size=self.BATCH_SIZE)
        self.assertTrue(os.path.exists(filename))
        self.check_deck_validity_bits(filename)
        os.remove(filename)

    def test_bitarray_creation(self):
        filename = 'data/decks_bitarray.bin'
        self.addCleanup(lambda: os.path.exists(filename) and os.remove(filename))
        times, peaks, sizes = self.measure_performance(create_deck_data_bitarray, filename)
        self.print_stats("Bitarray", times, peaks, sizes)
        # Run once more for validity check
        create_deck_data_bitarray(num_decks=self.NUM_DECKS, batch_size=self.BATCH_SIZE)
        self.assertTrue(os.path.exists(filename))
        self.check_deck_validity_bitarray(filename)
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()