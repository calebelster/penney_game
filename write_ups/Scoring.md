## Data Scoring Methods

### 1. Scoring Logic
Each deck is stored as a numpy array of 0's and 1's. The chosen sequence of 3 black or red cards is compared against the generated numpy array of cards. When a chosen sequence matches the sequence in the numpy array, the winning player takes all the cards since the last win.


### 2. Optimizations
Using parallel processing, we can use each CPU core to score a subset of decks, greatly decreasing the total runtime. We also used a JIT compiler called Numba, which turns Python functions into much faster machine code at runtime.