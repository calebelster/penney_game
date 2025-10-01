## Data Scoring Methods

### 1. Scoring Logic
Each deck is stored as a numpy array of 0’s and 1’s, where 0 = red and 1 = black. Each player chooses a sequence of 3 cards (ex. BBR, RBR, etc), and we slide that sequence across the deck. When the chosen sequence matches with the actual deck, the winning player takes all the cards from the last win earns a "trick".

For example, if a sample deck is "r r b b r b" and the chosen sequences are "r r b" for player 1, and "b r b" for player 2, the first three cards match player 1, who collects 3 cards and 1 trick. Then brb matches for player 2, who collects the next 3 cards and 1 trick. In this instance, it would result in a tie.

### 2. Optimizations
Using parallel processing, we can divide the scoring of the decks across CPU cores so that each core scores only a subset of total decks, greatly reducing runtime. However, even with this optimization our code was taking too long. On 30 samples of 1,000 decks, it took on average 4.07 seconds to run each iteration. Linearly, this would equate to over 67 minutes to run 1 million decks, which is not sensible. We then discovered Numba, a just-in-time (JIT) compiler that translates Python functions into fast machine code at runtime. Using this, we were hoping to speed up the inner scoring loop. It was successful, reducing our runtimes by 22.77% on average.

| Method | Avg (s) | Min (s) | Max (s) |
|--------|---------|---------|---------|
| Python | 5.27    | 4.29    | 7.42    |
| Numba  | 4.07    | 3.40    | 5.63    |


 Although Numba did cause a noticeable increase, it was not exceptionally faster. This was until we realized that Numba was much more powerful when analyzing larger subsets of decks. In 5 samples of 100,000 decks, we found Numba to be 95.1% faster on average, over 4 times faster than comparing to subsets of 1,000. 

| Method | Avg (s)  | Min (s) | Max (s)  |
|--------|----------|---------|----------|
| Python | 132.918  | 87.08   | 191.27   |
| Numba  | 6.51     | 6.17    | 6.98     |

We concluded that using Numba would be dramatically more practical, especially with deck sizes in the millions. We were able to run a sample of 5 scoring simulations using all 2 million decks, with an average runtime of 49.1 seconds.


