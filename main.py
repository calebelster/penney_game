from src.create_data import *
from bitarray import bitarray

def main():
    print("Only bits method:")
    create_deck_data_only_bits()
    with open('data/decks_bits.bin', 'rb') as f:
        data = f.read(7)  # 7 bytes = 56 bits
        ones = zeros = 0
        for i in range(52):
            byte_index = i // 8
            bit_index = 7 - (i % 8)
            bit = (data[byte_index] >> bit_index) & 1
            if bit:
                ones += 1
            else:
                zeros += 1
            print(f'Bit {i + 1}: {bit}')
        print(f'Number of 1s: {ones}')
        print(f'Number of 0s: {zeros}')

    print("\nBitarray method:")
    create_deck_data_bitarray()
    with open('data/decks_bitarray.bin', 'rb') as f:
        ba = bitarray()
        ba.fromfile(f, 52)  # Read exactly 52 bits (one deck)
        ones = zeros = 0
        for i, bit in enumerate(ba[:52]):
            print(f'Bit {i + 1}: {1 if bit else 0}')
            if bit:
                ones += 1
            else:
                zeros += 1
        print(f'Number of 1s: {ones}')
        print(f'Number of 0s: {zeros}')

if __name__ == "__main__":
    main()
