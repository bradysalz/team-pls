import sys
import csv
import time

from riothelpers import check_recent_matches


def fetch():
    """Helper function to fetch matches. Used as cron job.
    Takes the first argument on as a CSV list of summoners, in the format:
    [ Real Name, Summoner Name, Summoner ID ]
    ex: [ Brady, dahtguy, 111111 ]
    """
    file_name = sys.argv[1]

    lookup = []
    with open(file_name, 'rb') as f:
        file_read = csv.reader(f)
        for row in file_read:
            lookup.append(row[2])

    print 'Cron ran at {0}'.format(strftime("%a, %d %b %Y %H:%M:%S +0000"))
    for id in lookup:
        check_recent_matches(id)

if __name__ == '__main__':
    fetch()
