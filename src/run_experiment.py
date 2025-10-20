import os
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from matplotlib.patches import Rectangle
from bitarray import bitarray
from src.create_data import create_deck_data_bitarray, _create_bitarray_batch
from src.score_data import compute_winrate_table_incremental

DECKS_DIR = "data/decks"
TARGET_DECKS = 5_000_000
BATCH_SIZE = 50_000

os.makedirs("data", exist_ok=True)
os.makedirs("data/tables", exist_ok=True)
os.makedirs("data/plots", exist_ok=True)
os.makedirs(DECKS_DIR, exist_ok=True)

def find_deck_file():
    """
    Find the deck file with highest deck count in DECKS_DIR, following naming pattern.
    Returns tuple: (path, count)
    """
    files = [f for f in os.listdir(DECKS_DIR) if re.match(r"decks_\d+\.bin", f)]
    if not files:
        return None, 0
    counts = [(f, int(re.search(r"decks_(\d+)\.bin", f).group(1))) for f in files]
    best = max(counts, key=lambda x: x[1])
    return os.path.join(DECKS_DIR, best[0]), best[1]

def rename_deck_file(old_path, new_count):
    """
    Rename deck file to reflect new deck count.
    """
    new_name = f"decks_{new_count}.bin"
    new_path = os.path.join(DECKS_DIR, new_name)
    if old_path != new_path:
        os.rename(old_path, new_path)
    return new_path

def file_deck_count(file_path: str) -> int:
    """
    Return the number of decks in a given file by total bits divided by 52.
    """
    if not os.path.exists(file_path):
        return 0
    ba = bitarray()
    with open(file_path, "rb") as f:
        ba.fromfile(f)
    return len(ba) // 52

def append_decks(file_path: str, num_to_add: int, batch_size: int = 10_000):
    """
    Append new randomly-generated decks to an existing deck file.
    """
    with open(file_path, "ab") as f:
        batches = [batch_size] * (num_to_add // batch_size)
        if num_to_add % batch_size:
            batches.append(num_to_add % batch_size)
        for b in batches:
            ba = _create_bitarray_batch(b)
            ba.tofile(f)


def plot_heatmap(p1_pct_matrix, tie_pct_matrix, seqs, title, outpath, highlight_best=True):
    """
    Create a heatmap showing win/draw probabilities, coloring by win likelihood.
    Highlight row-best (highest win probability) cell with black box.
    """
    arr = np.nan_to_num(p1_pct_matrix, nan=0).astype(int).T
    tie_arr = np.nan_to_num(tie_pct_matrix, nan=0).astype(int).T
    n = arr.shape[0]
    mask = np.eye(n, dtype=bool)
    plt.figure(figsize=(9, 7))
    cmap = plt.get_cmap("Blues")
    annot_labels = np.empty_like(arr, dtype=object)
    for i in range(n):
        for j in range(n):
            if mask[i, j] or np.isnan(p1_pct_matrix[j, i]):
                annot_labels[i, j] = ""
            else:
                annot_labels[i, j] = f"{arr[i, j]} ({tie_arr[i, j]})"
    ax = sns.heatmap(
        arr,
        cmap=cmap,
        vmin=0,
        vmax=100,
        mask=mask,
        linewidths=0.5,
        cbar_kws={"label": "Player 1 win %"},
        xticklabels=seqs,
        yticklabels=seqs,
        annot=annot_labels,
        fmt="",
        annot_kws={"size": 8, "color": "black"},
    )
    ax.set_title(title)
    ax.set_xlabel("Player 1 pattern")
    ax.set_ylabel("Opponent (Player 2) pattern")
    if highlight_best:
        for i in range(n):
            row = arr[i, :].astype(float).copy()
            row[i] = np.nan
            if np.all(np.isnan(row)):
                continue
            best_j = int(np.nanargmax(row))
            ax.add_patch(Rectangle((best_j, i), 1, 1, fill=False, edgecolor='black', lw=2))
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def run_scoring_and_plots(deck_file, limit_to_target=True, decks_to_use=None):
    """
    Run scoring and plot heatmaps for both scoring methods (cards, tricks).
    Save results as CSVs and plots in expected locations.
    """
    total_decks = file_deck_count(deck_file)
    if decks_to_use is None:
        decks_to_use = min(total_decks, TARGET_DECKS) if limit_to_target else total_decks
    print(f"\nScoring using n = {decks_to_use:,} decks...")
    deck_file_path, _ = find_deck_file()
    cards_df, tricks_df, cards_pct_p1, cards_pct_tie, tricks_pct_p1, tricks_pct_tie, seqs = compute_winrate_table_incremental(
        deck_file_path,
        k=3,
        counts_cards_file="data/tracking_decks/counts_cards.npy",
        counts_tricks_file="data/tracking_decks/counts_tricks.npy",
        last_n_file="data/tracking_decks/last_n.txt"
    )

    csv_cards = f"data/tables/winrates_cards_n{decks_to_use}.csv"
    csv_tricks = f"data/tables/winrates_tricks_n{decks_to_use}.csv"
    cards_df.to_csv(csv_cards)
    tricks_df.to_csv(csv_tricks)
    print(f"Saved CSVs: {csv_cards}, {csv_tricks}")
    plot_heatmap(cards_pct_p1, cards_pct_tie, seqs,
                 f"Player 1 Win % by Cards (n={decks_to_use:,})",
                 f"data/plots/heatmap_cards_n{decks_to_use}.png")
    plot_heatmap(tricks_pct_p1, tricks_pct_tie, seqs,
                 f"Player 1 Win % by Tricks (n={decks_to_use:,})",
                 f"data/plots/heatmap_tricks_n{decks_to_use}.png")
    print("Saved updated heatmaps.")


def delete_old_outputs(decks_to_use):
    """
    Delete old CSVs and plots not matching the current decks_to_use value.
    Ensures only current outputs remain.
    """
    for f in glob.glob("data/tables/winrates_cards_n*.csv"):
        if f != f"data/tables/winrates_cards_n{decks_to_use}.csv":
            os.remove(f)
    for f in glob.glob("data/tables/winrates_tricks_n*.csv"):
        if f != f"data/tables/winrates_tricks_n{decks_to_use}.csv":
            os.remove(f)
    for f in glob.glob("data/plots/heatmap_cards_n*.png"):
        if f != f"data/plots/heatmap_cards_n{decks_to_use}.png":
            os.remove(f)
    for f in glob.glob("data/plots/heatmap_tricks_n*.png"):
        if f != f"data/plots/heatmap_tricks_n{decks_to_use}.png":
            os.remove(f)


def augment_or_rescore(n: int, prev_decks_to_use: int):
    """
    Add n new decks, renaming file when finished, and rescore using updated deck count.
    """
    deck_file, cur_count = find_deck_file()
    decks_to_use = prev_decks_to_use + n
    if cur_count < decks_to_use:
        print(f"\nAppending {decks_to_use - cur_count:,} new decks to {deck_file}...")
        append_decks(deck_file, decks_to_use - cur_count)
        deck_file = rename_deck_file(deck_file, decks_to_use)
        print(f"New total decks: {decks_to_use:,}")
    else:
        print(f"\nDeck file has {cur_count:,} decks; scoring only the first {decks_to_use:,}.")
    delete_old_outputs(decks_to_use)
    run_scoring_and_plots(deck_file, limit_to_target=False, decks_to_use=decks_to_use)


def augment_data(n: int):
    """
    Create n new decks and update scores/figures accordingly.
    """
    deck_file, cur_count = find_deck_file()
    augment_or_rescore(n, cur_count)


def main():
    """
    Main experiment driver. Creates decks (if missing), then scores and plots results.
    Prompts to augment further decks.
    """
    deck_file, cur_count = find_deck_file()
    prev_decks_to_use = TARGET_DECKS
    if not deck_file:
        print(f"No deck file found. Creating {TARGET_DECKS:,} decks...")
        deck_file = os.path.join(DECKS_DIR, f"decks_{TARGET_DECKS}.bin")
        create_deck_data_bitarray(num_decks=TARGET_DECKS,
                                  output_name=os.path.basename(deck_file),
                                  batch_size=BATCH_SIZE)
        print("Deck creation finished.")
    elif cur_count < TARGET_DECKS:
        need = TARGET_DECKS - cur_count
        print(f"Deck file has {cur_count:,} decks; creating {need:,} more to reach {TARGET_DECKS:,}.")
        append_decks(deck_file, need)
        deck_file = rename_deck_file(deck_file, TARGET_DECKS)
    elif cur_count > TARGET_DECKS:
        print(f"Deck file has {cur_count:,} decks; scoring only the first {TARGET_DECKS:,}.")
    delete_old_outputs(TARGET_DECKS)
    run_scoring_and_plots(deck_file, limit_to_target=True)
    while True:
        resp = input("\nAppend more decks and rerun? [y/N]: ").strip().lower()
        if resp not in ("y", "yes"):
            print("Done.")
            break
        try:
            add_n = int(input("How many additional decks to create? (e.g. 1000000): ").strip())
            if add_n <= 0:
                print("No decks added.")
                continue
        except Exception:
            print("Invalid number.")
            continue
        augment_or_rescore(add_n, prev_decks_to_use)
        prev_decks_to_use += add_n


if __name__ == "__main__":
    main()