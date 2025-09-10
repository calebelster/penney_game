from src.create_data import *

def main():
    #create_deck_data()
    # Replace 'your_file.bin' with the actual path to your .bin file
    # Python
    # Python
    with open('data/decks.bin', 'rb') as f:
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


if __name__ == "__main__":
    main()
