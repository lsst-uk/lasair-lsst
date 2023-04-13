### Building watchlist files
`watchlist_test.py`

This test uses a small watchlist to build a MOC file. Several mock alerts are run against 
the MOC file, and the number of hits asserted. The watchlist and the mock alerts are
in the same csv file, which also includes a program that generates such a csv file.
It uses the following auxiliary files and directories:
* watchlist_sample.csv
* watchlist_cache

