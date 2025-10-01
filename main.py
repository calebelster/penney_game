import time
from src.create_data import *
from src.score_data import *
from bitarray import bitarray
from src.score_data import compute_winrate_table

def main():
    file_path = 'data/decks/decks_bitarray.bin'
    start = time.time()

    cards_df, tricks_df = compute_winrate_table(file_path)

    end = time.time()

    print("Win rates by cards:")
    print(cards_df)

    print("Win rates by tricks:")
    print(tricks_df)
    
    print(f"Elapsed time: {end - start:.2f} seconds")

    cards_df.to_csv('data/tables/winrates_cards.csv')
    tricks_df.to_csv('data/tables/winrates_tricks.csv')

if __name__ == "__main__":
    main()
