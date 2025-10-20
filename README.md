# Penney Game Simulation

This repository simulates and analyzes several pattern-matching card games, including Penney's Game, the Humble-Nishiyama Game, and a new variant that scores by the total number of cards won. No prior knowledge of these games is assumed, and the experiments reveal how rule changes affect optimal strategies for players.

## Project Overview

- **Penney's Game** is a probability puzzle where two players each select a sequence of three Red (R) or Black (B) cards. A shuffled deck is revealed, and the first player whose pattern appears is the winner.
- **Humble-Nishiyama Game** is a related variation that allows pattern overlaps and uses different criteria for winning.
- **Total Cards Won Variant:** This new variant scores players by the total number of cards won across all pattern occurrences, not just the first. Simulations show that the best strategy for player 2 differs markedly here compared to the classic Penney's Game and Humble-Nishiyama Game. These differences are visualized in heatmaps and summarized in output tables.

The core experiment creates millions of shuffled decks, scores outcomes under different variants, and produces CSVs and heatmaps to illustrate win rates and reveal strategic insights.

## Quickstart Guide

1. **Dependencies:**  
   This project uses Python 3.8+ and dependencies managed via **UV**. If you are unfamiliar with UV, see the [UV documentation](https://github.com/astral-sh/uv).

2. **Setup and Running:**  
   - Clone the repository and ensure your shell is in the root directory of the project.  
   - Run  
     ```
     uv sync
     ```  
     to synchronize and install all necessary dependencies specified in the project configuration.  
   - Then run the experiment with:  
     ```
     uv run main.py
     ```  
     This will generate decks, score all variants, produce CSV data files, and create heatmaps in the `data/plots` directory.

3. **Outputs:**  
   - Results include detailed win-rate tables and heatmaps showing probabilities of winning by first appearance and by total cards won, illuminating how scoring rules affect optimal play.

Following these steps will allow users to reproduce the core findings that player 2’s optimal strategy shifts depending on the scoring variant used in these pattern-based card games.