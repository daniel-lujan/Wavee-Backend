from io import BytesIO
from audio import processing
from audio import hashing
from typing import List, Tuple, Dict
import database

def get_fingerprint(audio: BytesIO) -> List[Tuple[int, int]]:
    
    Y = processing.compute_spectrogram(audio)

    return processing.compute_constellation_map(Y)

def score_matches(matches, query_fingerprint):

    scored_matches = {}

    for m in matches:
        scored_matches[m] = processing.score_similarity(database.SONGS_DB[m], query_fingerprint)
    
    return scored_matches


def query_song(audio: BytesIO) -> Dict[str, int]:
    
    fp = get_fingerprint(audio)

    hashes = hashing.hash_points(fp)

    matches = database.get_matches(hashes)

    return score_matches(matches, fp)
