# run_experiment.py
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from bitarray import bitarray

from src.create_data import create_deck_data_bitarray, _create_bitarray_batch
from src.score_data import compute_winrate_table

# === Global paths & parameters ===
DECK_FILE = "data/decks/decks_bitarray.bin"
TARGET_DECKS = 5_000_000
BATCH_SIZE = 10_000

os.makedirs("data", exist_ok=True)
os.makedirs("data/tables", exist_ok=True)
os.makedirs("data/plots", exist_ok=True)


# === Utility functions ===
def file_deck_count(file_path: str) -> int:
    """Return number of full 52-card decks in file."""
    if not os.path.exists(file_path):
        return 0
    ba = bitarray()
    with open(file_path, "rb") as f:
        ba.fromfile(f)
    return len(ba) // 52


def append_decks(file_path: str, num_to_add: int, batch_size: int = 10_000):
    """Append num_to_add decks to existing bitarray file."""
    with open(file_path, "ab") as f:
        batches = [batch_size] * (num_to_add // batch_size)
        if num_to_add % batch_size:
            batches.append(num_to_add % batch_size)
        for b in batches:
            ba = _create_bitarray_batch(b)
            ba.tofile(f)


def plot_heatmap(p1_pct_matrix, tie_pct_matrix, seqs, title, outpath, highlight_best=True):
    """
    Plot a heatmap of P1 win % and tie %.
    Each cell: 'P1% (Tie%)'
    White = 0%, Blue = 100% (P1 win odds).
    """
    arr = np.array(p1_pct_matrix, dtype=float)
    tie_arr = np.array(tie_pct_matrix, dtype=float)
    n = arr.shape[0]
    mask = np.eye(n, dtype=bool)

    plt.figure(figsize=(9, 7))
    cmap = plt.get_cmap("Blues")

    annot_labels = np.empty_like(arr, dtype=object)
    for i in range(n):
        for j in range(n):
            if mask[i, j] or np.isnan(arr[i, j]):
                annot_labels[i, j] = ""
            else:
                annot_labels[i, j] = f"{arr[i, j]:.1f} ({tie_arr[i, j]:.1f})"

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
    ax.set_xlabel("Opponent (Player 2) pattern")
    ax.set_ylabel("Player 1 pattern")

    if highlight_best:
        for i in range(n):
            row = arr[i, :].copy()
            row[i] = np.nan
            if np.all(np.isnan(row)):
                continue
            best_j = int(np.nanargmax(row))
            ax.add_patch(Rectangle((best_j, i), 1, 1, fill=False, edgecolor='black', lw=2))

    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


# === Scoring and plotting orchestration ===
def run_scoring_and_plots(limit_to_target=True):
    """Compute winrate tables and produce updated CSVs + plots."""
    total_decks = file_deck_count(DECK_FILE)
    decks_to_use = min(total_decks, TARGET_DECKS) if limit_to_target else total_decks

    print(f"\nScoring using n = {decks_to_use:,} decks...")

    cards_df, tricks_df, cards_pct_p1, cards_pct_tie, tricks_pct_p1, tricks_pct_tie, seqs = \
        compute_winrate_table(
            DECK_FILE, k=3, workers=None, batch_size=50_000,
            max_decks=decks_to_use, seq_order_binary=True
        )

    # === Save CSVs ===
    csv_cards = f"data/tables/winrates_cards_n{decks_to_use}.csv"
    csv_tricks = f"data/tables/winrates_tricks_n{decks_to_use}.csv"
    cards_df.to_csv(csv_cards)
    tricks_df.to_csv(csv_tricks)
    print(f"Saved CSVs: {csv_cards}, {csv_tricks}")

    # === Plot Heatmaps ===
    plot_heatmap(cards_pct_p1, cards_pct_tie, seqs,
                 f"Player 1 Win % by Cards (n={decks_to_use:,})",
                 f"data/plots/heatmap_cards_n{decks_to_use}.png")
    plot_heatmap(tricks_pct_p1, tricks_pct_tie, seqs,
                 f"Player 1 Win % by Tricks (n={decks_to_use:,})",
                 f"data/plots/heatmap_tricks_n{decks_to_use}.png")
    print("Saved updated heatmaps.")


def augment_data(n: int):
    """
    Append n new decks, update scores, and regenerate figures.
    Example:
        >>> from run_experiment import augment_data
        >>> augment_data(1000000)
    """
    print(f"\nAppending {n:,} new decks to {DECK_FILE}...")
    append_decks(DECK_FILE, n)
    total = file_deck_count(DECK_FILE)
    print(f"New total decks: {total:,}")
    run_scoring_and_plots(limit_to_target=True)


# === Main entrypoint ===
def main():
    cur = file_deck_count(DECK_FILE)
    if cur == 0:
        print(f"No deck file found. Creating {TARGET_DECKS:,} decks...")
        create_deck_data_bitarray(num_decks=TARGET_DECKS,
                                  output_name=os.path.basename(DECK_FILE),
                                  batch_size=BATCH_SIZE)
        print("Deck creation finished.")
    elif cur < TARGET_DECKS:
        need = TARGET_DECKS - cur
        print(f"Deck file has {cur:,} decks; creating {need:,} more to reach {TARGET_DECKS:,}.")
        append_decks(DECK_FILE, need)
    elif cur > TARGET_DECKS:
        print(f"Deck file has {cur:,} decks; scoring only the first {TARGET_DECKS:,}.")

    run_scoring_and_plots(limit_to_target=True)

    # Ask user if they want to append more decks after initial run
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
        augment_data(add_n)


if __name__ == "__main__":
    main()
