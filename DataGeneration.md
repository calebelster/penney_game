## Data Generation Methods

### 1. Bits Only Binary File

This method generates a binary file containing only bits (0s and 1s). It is useful for space efficiency but takes time to run and is prone to errors or bugs.

It is created in batches of 10,000 52 bit decks that are all appended to one binary file. When reading these files the bits need to be calculated which is time consuming and error prone.

### 2. Bitarray Binary File

This method uses the `bitarray` library to create a binary file. It is faster than the bits-only method and less prone to errors, but it requires the `bitarray` library to be installed.

This method allows for indexing the same way a typical array works. This results in more efficient access time and less error-prone code.

#### Important Notes:

Both methods make use of parallel processing to speed up the data generation process. However, the bits-only method is significantly slower and more error-prone compared to the bitarray method.


### BitArray Method (1 million decks | 5 runs)
| Statistic | Runtime | Peak Memory Usage (KiB)| File Size (bytes) |
| ---- | ---------- | ---------- | ---------- |
| Avg | 93.4653 | 7138.15 | 6500000.00 |
| Median | 93.1439 | 6972.70 | 6500000.00 |
| Min | 74.9839 | 6968.96 | 6500000 |
| Max | 111.1638 | 7804.29 | 6500000 |
| Std Dev | 16.7273 | 372.39 | 0.00 |

### Bits Method (1 million decks | 5 runs)
| Statistic | Runtime | Peak Memory Usage (KiB)| File Size (bytes) |
| ---- |----------|----------|----------|
| Avg | 297.6125 | 220111.21 | 7000000.00 |
| Median | 298.6667 | 220110.11  | 7000000.00 |
| Min | 283.7084 | 20109.99 | 7000000 |
| Max | 311.9737 | 220114.04 | 7000000 |
| Std Dev | 11.1171 | 1.78 | 0.00 |

### Conclusion
The BitArray method is significantly faster and uses less memory compared to the Bits Only method. Additionally, the file size for the BitArray method is smaller, making it a more efficient choice for data generation.