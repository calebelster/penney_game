import os
import numpy as np
from bitarray import bitarray
import numba as nb
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def read_deck_file(file_path: str) -> np.ndarray:
    ba = bitarray()
    with open(file_path, 'rb') as f:
        ba.fromfile(f)
    arr = np.frombuffer(ba.unpack(), dtype=np.uint8)
    n_decks = len(arr) // 52
    arr = arr[:n_decks * 52]
    return arr.reshape((n_decks, 52))

@nb.njit
def score_deck_humble_jit(deck: np.ndarray, s1: np.ndarray, s2: np.ndarray):
    k = s1.size
    p1_cards = p2_cards = p1_tricks = p2_tricks = 0
    last_award_idx = 0
    i = k - 1
    while i < deck.size:
        match1 = True
        match2 = True
        # Only check if window starts at or after last_award_idx
        start_idx = i - k + 1
        if start_idx < last_award_idx:
            i += 1
            continue
        for j in range(k):
            if deck[start_idx + j] != s1[j]:
                match1 = False
            if deck[start_idx + j] != s2[j]:
                match2 = False
        if match1:
            p1_cards += (i - last_award_idx + 1)
            p1_tricks += 1
            last_award_idx = i + 1
            i = last_award_idx + k - 1  # Jump to next possible window after reset
        elif match2:
            p2_cards += (i - last_award_idx + 1)
            p2_tricks += 1
            last_award_idx = i + 1
            i = last_award_idx + k - 1
        else:
            i += 1

    return p1_cards, p2_cards, p1_tricks, p2_tricks

def _seq_to_array(seq: str) -> np.ndarray:
    return np.array([1 if c == 'r' else 0 for c in seq.lower()], dtype=np.uint8)

def _batch_score(decks_chunk, seqs, seq_arrays):
    nseq = len(seqs)
    lc1 = np.zeros((nseq, nseq), dtype=np.int64)
    lc2 = np.zeros((nseq, nseq), dtype=np.int64)
    lct = np.zeros((nseq, nseq), dtype=np.int64)
    lt1 = np.zeros((nseq, nseq), dtype=np.int64)
    lt2 = np.zeros((nseq, nseq), dtype=np.int64)
    ltt = np.zeros((nseq, nseq), dtype=np.int64)
    for deck in decks_chunk:
        for i, s1 in enumerate(seqs):
            for j, s2 in enumerate(seqs):
                if i == j:
                    continue
                c1, c2, t1, t2 = score_deck_humble_jit(deck, seq_arrays[s1], seq_arrays[s2])
                # cards
                if c1 > c2:
                    lc1[i, j] += 1
                elif c2 > c1:
                    lc2[i, j] += 1
                else:
                    lct[i, j] += 1
                # tricks
                if t1 > t2:
                    lt1[i, j] += 1
                elif t2 > t1:
                    lt2[i, j] += 1
                else:
                    ltt[i, j] += 1
    return lc1, lc2, lct, lt1, lt2, ltt

def all_sequences_binary_order(k=3):
    seqs = []
    for num in range(2 ** k):
        bits = [(num >> (k - 1 - i)) & 1 for i in range(k)]
        seq = ''.join('r' if bit else 'b' for bit in bits)
        seqs.append(seq)
    return seqs

def compute_winrate_table_incremental(
    file_path: str,
    k: int = 3,
    workers: int = None,
    batch_size: int = 50_000,
    max_decks: int = None,
    seq_order_binary: bool = True,
    counts_cards_file: str = "counts_cards.npy",
    counts_tricks_file: str = "counts_tricks.npy",
    last_n_file: str = "last_n.txt"
):
    """Incremental update: only score decks after the last processed index."""
    decks = read_deck_file(file_path)
    if max_decks is not None:
        decks = decks[:max_decks]
    n = decks.shape[0]
    seqs = all_sequences_binary_order(k) if seq_order_binary else all_sequences(k)
    nseq = len(seqs)
    seq_arrays = {s: _seq_to_array(s) for s in seqs}

    # Load or initialize counts
    if os.path.exists(counts_cards_file) and os.path.exists(counts_tricks_file) and os.path.exists(last_n_file):
        cards_p1, cards_p2, cards_tie = np.load(counts_cards_file)
        tricks_p1, tricks_p2, tricks_tie = np.load(counts_tricks_file)
        with open(last_n_file, "r") as f:
            last_n = int(f.read().strip())
    else:
        cards_p1 = np.zeros((nseq, nseq), dtype=np.int64)
        cards_p2 = np.zeros((nseq, nseq), dtype=np.int64)
        cards_tie = np.zeros((nseq, nseq), dtype=np.int64)
        tricks_p1 = np.zeros((nseq, nseq), dtype=np.int64)
        tricks_p2 = np.zeros((nseq, nseq), dtype=np.int64)
        tricks_tie = np.zeros((nseq, nseq), dtype=np.int64)
        last_n = 0

    if n > last_n:
        new_decks = decks[last_n:]
        chunks = [new_decks[i:i + batch_size] for i in range(0, len(new_decks), batch_size)]
        if workers is None:
            workers = os.cpu_count()
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
        # Save updated counts and index
        np.save(counts_cards_file, [cards_p1, cards_p2, cards_tie])
        np.save(counts_tricks_file, [tricks_p1, tricks_p2, tricks_tie])
        with open(last_n_file, "w") as f:
            f.write(str(n))

    def _pct_matrices(p1, p2, tie):
        total = p1 + p2 + tie
        p1_pct = np.divide(p1, total, out=np.full_like(p1, np.nan, dtype=np.float64), where=total > 0) * 100
        tie_pct = np.divide(tie, total, out=np.full_like(tie, np.nan, dtype=np.float64), where=total > 0) * 100
        return np.round(p1_pct, 4), np.round(tie_pct, 4)

    cards_pct_p1, cards_pct_tie = _pct_matrices(cards_p1, cards_p2, cards_tie)
    tricks_pct_p1, tricks_pct_tie = _pct_matrices(tricks_p1, tricks_p2, tricks_tie)

    def _format_str_matrix(p1_pct, tie_pct):
        n = p1_pct.shape[0]
        mat = np.empty((n, n), dtype=object)
        for i in range(n):
            for j in range(n):
                if i == j or np.isnan(p1_pct[i, j]):
                    mat[i, j] = ""
                else:
                    mat[i, j] = f"{p1_pct[i,j]:.2f}% ({tie_pct[i,j]:.2f}%)"
        df = pd.DataFrame(mat, index=seqs, columns=seqs)
        df.index.name = "Player 1 pattern"
        df.columns.name = "Player 2 pattern"
        return df

    cards_df = _format_str_matrix(cards_pct_p1, cards_pct_tie)
    tricks_df = _format_str_matrix(tricks_pct_p1, tricks_pct_tie)
    return cards_df, tricks_df, cards_pct_p1, cards_pct_tie, tricks_pct_p1, tricks_pct_tie, seqs