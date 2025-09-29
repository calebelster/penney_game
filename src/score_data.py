import os
import numpy as np
from bitarray import bitarray
import numba as nb
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
from itertools import product


def read_deck_file(file_path: str) -> np.ndarray:
    ba = bitarray()
    with open(file_path, 'rb') as f:
        ba.fromfile(f)
    arr = np.frombuffer(ba.unpack(), dtype=np.uint8)  # 0/1 array
    n_decks = len(arr) // 52
    arr = arr[:n_decks * 52]
    decks = arr.reshape((n_decks, 52))
    return decks


@nb.njit
def score_deck_humble_jit(deck: np.ndarray, s1: np.ndarray, s2: np.ndarray):
    """
    Score one deck using Humble-Nishiyama rules.
    Ensures we don't match using already-awarded cards.
    """
    k = s1.size
    p1_cards = 0
    p2_cards = 0
    p1_tricks = 0
    p2_tricks = 0
    last_award_idx = 0

    for i in range(k - 1, deck.size):
        # only check windows that are fully in the current pile (i-k+1 .. i)
        if (i - k + 1) < last_award_idx:
            continue

        match1 = True
        match2 = True
        for j in range(k):
            v = deck[i - k + 1 + j]
            if v != s1[j]:
                match1 = False
            if v != s2[j]:
                match2 = False

        if match1:
            p1_cards += (i - last_award_idx + 1)
            p1_tricks += 1
            last_award_idx = i + 1
        elif match2:
            p2_cards += (i - last_award_idx + 1)
            p2_tricks += 1
            last_award_idx = i + 1

    return p1_cards, p2_cards, p1_tricks, p2_tricks


def _seq_to_array(seq: str) -> np.ndarray:
    return np.array([0 if c.lower() == 'r' else 1 for c in seq], dtype=np.uint8)


def all_sequences(k=3):
    return [''.join('r' if x == 0 else 'b' for x in seq)
            for seq in product([0, 1], repeat=k)]


def _winner(deck, s1, s2):
    """Return winners for cards and tricks separately."""
    c1, c2, t1, t2 = score_deck_humble_jit(deck, s1, s2)
    # cards winner
    if c1 > c2:
        w_cards = 1
    elif c2 > c1:
        w_cards = 2
    else:
        w_cards = 0
    # tricks winner
    if t1 > t2:
        w_tricks = 1
    elif t2 > t1:
        w_tricks = 2
    else:
        w_tricks = 0
    return w_cards, w_tricks


def _batch_score(decks_chunk, seqs, seq_arrays):
    """Top-level batch scorer so ProcessPoolExecutor can pickle it."""
    nseq = len(seqs)
    local_cards_p1 = np.zeros((nseq, nseq), dtype=np.int64)
    local_cards_p2 = np.zeros((nseq, nseq), dtype=np.int64)
    local_cards_tie = np.zeros((nseq, nseq), dtype=np.int64)

    local_tricks_p1 = np.zeros((nseq, nseq), dtype=np.int64)
    local_tricks_p2 = np.zeros((nseq, nseq), dtype=np.int64)
    local_tricks_tie = np.zeros((nseq, nseq), dtype=np.int64)

    for deck in decks_chunk:
        for i, s1 in enumerate(seqs):
            for j, s2 in enumerate(seqs):
                if i == j:
                    continue
                w_cards, w_tricks = _winner(deck, seq_arrays[s1], seq_arrays[s2])
                if w_cards == 1:
                    local_cards_p1[i, j] += 1
                elif w_cards == 2:
                    local_cards_p2[i, j] += 1
                else:
                    local_cards_tie[i, j] += 1

                if w_tricks == 1:
                    local_tricks_p1[i, j] += 1
                elif w_tricks == 2:
                    local_tricks_p2[i, j] += 1
                else:
                    local_tricks_tie[i, j] += 1

    return (local_cards_p1, local_cards_p2, local_cards_tie,
            local_tricks_p1, local_tricks_p2, local_tricks_tie)


def compute_winrate_table(file_path: str, k: int = 3,
                          workers: int = None, batch_size: int = 50_000):
    """
    Compute win/tie rates for every distinct pair of sequences of length k.

    Returns two DataFrames:
        cards_df: rates by cards
        tricks_df: rates by tricks

    Each cell = 'P1% (Tie%)'; P2% = 100 - P1% - Tie%.
    Rows = Player 1 patterns, Columns = Player 2 patterns.
    """
    decks = read_deck_file(file_path)
    n = decks.shape[0]

    seqs = all_sequences(k)
    nseq = len(seqs)

    seq_arrays = {s: _seq_to_array(s) for s in seqs}

    cards_p1 = np.zeros((nseq, nseq), dtype=np.int64)
    cards_p2 = np.zeros((nseq, nseq), dtype=np.int64)
    cards_tie = np.zeros((nseq, nseq), dtype=np.int64)

    tricks_p1 = np.zeros((nseq, nseq), dtype=np.int64)
    tricks_p2 = np.zeros((nseq, nseq), dtype=np.int64)
    tricks_tie = np.zeros((nseq, nseq), dtype=np.int64)

    if workers is None:
        workers = os.cpu_count()

    chunks = [decks[i:i + batch_size] for i in range(0, n, batch_size)]

    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_batch_score, chunk, seqs, seq_arrays) for chunk in chunks]
        for fut in futures:
            lc1, lc2, lct, lt1, lt2, ltt = fut.result()
            cards_p1 += lc1
            cards_p2 += lc2
            cards_tie += lct
            tricks_p1 += lt1
            tricks_p2 += lt2
            tricks_tie += ltt

    def _format_rates(p1, p2, tie):
        total = p1 + p2 + tie
        if total == 0:
            return np.nan
        p1_pct = round(p1 / total * 100, 2)
        tie_pct = round(tie / total * 100, 2)
        return f"{p1_pct:.2f}% ({tie_pct:.2f}%)"  # P2 = 100 - p1 - tie

    cards_table = pd.DataFrame(index=seqs, columns=seqs)
    tricks_table = pd.DataFrame(index=seqs, columns=seqs)

    for i, s1 in enumerate(seqs):  # row = Player 1
        for j, s2 in enumerate(seqs):  # col = Player 2
            if i == j:
                cards_table.loc[s1, s2] = np.nan
                tricks_table.loc[s1, s2] = np.nan
            else:
                cards_table.loc[s1, s2] = _format_rates(
                    cards_p1[i, j], cards_p2[i, j], cards_tie[i, j]
                )
                tricks_table.loc[s1, s2] = _format_rates(
                    tricks_p1[i, j], tricks_p2[i, j], tricks_tie[i, j]
                )

    return cards_table, tricks_table
