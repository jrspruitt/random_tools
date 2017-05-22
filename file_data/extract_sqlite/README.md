## Extract SQLite DB

This script attempts to extract sqlite databases from data files. It searches for all sqlite magic string "SQLite format3\x00'" then reads the headers.

From the header the page_size and db_size is used to calculate the size of each database. From here it reads that much data from the input file, and saves them to the output_dir.

Not all sqlite databases can be counted on for this method.

**Usage:**

    ./extract_sqlite.py <file.bin> <output_dir>


