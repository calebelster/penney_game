from typing import List, Tuple

# --- scoring function for one deck ---
def score_single_deck(deck: List[int],
                      pattern1: Tuple[int, int, int],
                      pattern2: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
    """
    Score a single deck for both cards and tricks.

    Returns:
      (p1_cards, p2_cards, p1_tricks, p2_tricks)
    """
    window = []
    cards_since_last_win = 0
    p1_cards = p2_cards = 0
    p1_tricks = p2_tricks = 0

    for idx, card in enumerate(deck):
        window.append(card)
        if len(window) > 3:
            window.pop(0)

        cards_since_last_win += 1

        # Check for pattern match
        if len(window) == 3:
            if tuple(window) == pattern1:
                # Player 1 wins the cards since last win
                p1_cards += cards_since_last_win
                p1_tricks += 1
                print(f"Flip {idx+1}: P1 pattern matched. "
                      f"Won {cards_since_last_win} cards. "
                      f"Total cards={p1_cards}, tricks={p1_tricks}")
                cards_since_last_win = 0
            elif tuple(window) == pattern2:
                p2_cards += cards_since_last_win
                p2_tricks += 1
                print(f"Flip {idx+1}: P2 pattern matched. "
                      f"Won {cards_since_last_win} cards. "
                      f"Total cards={p2_cards}, tricks={p2_tricks}")
                cards_since_last_win = 0

    print("\nEnd of deck.")
    print(f"Player 1: {p1_cards} cards, {p1_tricks} tricks")
    print(f"Player 2: {p2_cards} cards, {p2_tricks} tricks")
    return p1_cards, p2_cards, p1_tricks, p2_tricks


if __name__ == "__main__":
    # 0 = Red, 1 = Black
    # Make a very small deck: 12 cards
    test_deck = [0,0,0,1,1,0, 1,0,1,0,1,1]
    # Player 1 looks for Red-Red-Red
    p1_pattern = (0,0,0)
    # Player 2 looks for Black-Red-Black
    p2_pattern = (1,0,1)

    print("Deck:", test_deck)
    print("P1 pattern:", p1_pattern, "P2 pattern:", p2_pattern)
    print("\nStep-by-step scoring:\n")
    score_single_deck(test_deck, p1_pattern, p2_pattern)
