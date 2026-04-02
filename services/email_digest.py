"""
For each filter with email output, checks the associated Kafka topic for new alerts,
builds a digest email and sends it. Intended to be run as a daily cronjob.
Usage:
    email_digest.py

Options:
    --help     Show usage information
"""

from docopt import docopt
from src import db_connect


def main():
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = f"SELECT * FROM myqueries WHERE active>0"
    cursor.execute(query)
    for row in cursor:
        print(row)


if __name__ == '__main__':
    args = docopt(__doc__)
    main()
