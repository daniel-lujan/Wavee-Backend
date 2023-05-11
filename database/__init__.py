from typing import List, Tuple, Dict
import numpy as np
from settings import SCORING_BIN_WIDTH
from database import static

HASH_TABLE = static.HASH_TABLE
SONGS_DB = static.SONGS

def score_match(offsets: List[int]) -> int:
    """
    Adapted from: https://github.com/notexactlyawe/abracadabra/blob/master/abracadabra/recognise.py

    Score a matched song.

    Calculates a histogram of the deltas between the time offsets of the hashes from the
    recorded sample and the time offsets of the hashes matched in the database for a song.
    The function then returns the size of the largest bin in this histogram as a score.

    :param offsets: List of offset pairs for matching hashes
    :returns: The highest peak in a histogram of time deltas
    :rtype: int
    """
    # Use bins spaced 0.5 seconds apart
    binwidth = SCORING_BIN_WIDTH
    hist, _ = np.histogram(offsets,
                           bins=np.arange(int(min(offsets)),
                                          int(max(offsets)) + binwidth + 1,
                                          binwidth))
    return int(np.max(hist))

def get_matches(hashes: List[Tuple[str, int, int]]) -> Dict[str, int]:
    
    matches = set()

    for h in hashes:
        try:
            for match in HASH_TABLE[h[0]]:
                matches.add(match[1])
        except KeyError:
            continue
    
    return matches

    # matches = {}

    # for h in hashes:
    #     try:
    #         for match in HASH_TABLE[h[0]]:
    #             try:
    #                 matches[match[1]].append(match[0] - h[1])
    #             except KeyError:
    #                 matches[match[1]] = [match[0] - h[1]]
    #     except KeyError:
    #         continue
    
    # for m in matches:
    #     matches[m] = score_match(matches[m])
    
    return matches
    