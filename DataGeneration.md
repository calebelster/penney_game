## Data Generation Methods

### 1. Bits Only Binary File

This method generates a binary file containing only bits (0s and 1s). It is useful for space efficiency but takes time to run and is prone to errors or bugs.

It is created in batches of 10,000 52 bit decks that are all appended to one binary file. When reading these files need to be

### 2. Bitarray Binary File

This method uses the `bitarray` library to create a binary file. It is faster than the bits-only method and less prone to errors, but it requires the `bitarray` library to be installed.

#### Important Notes:

Both methods make use of parallel processing to speed up the data generation process. However, the bits-only method is significantly slower and more error-prone compared to the bitarray method.
