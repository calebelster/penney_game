from src.create_data import *
from src.score_data import *
from bitarray import bitarray


def main():
    ### create data if not already created and then score it and print the results

    data_file = 'decks_bitarray.bin'
    score_file = 'scores_bitarray.npy'
    if not os.path.exists(os.path.join('data', data_file)):
        print("Creating deck data...")
        create_deck_data_bitarray(num_decks=2_000_000, output_name=data_file, batch_size=10000)
        print("Deck data created.")
    else:
        print("Deck data already exists. Skipping creation.")
    

    print("Scoring deck data...")
    score_deck_data_bitarray(input_name=data_file, output_name=score_file)
    print("Deck data scored.")

if __name__ == "__main__":
    main()
