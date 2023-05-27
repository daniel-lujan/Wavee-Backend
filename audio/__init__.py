from io import BytesIO
from audio import processing
from audio import hashing
from typing import List, Tuple, Dict
import database

def get_fingerprint(audio: BytesIO) -> List[Tuple[int, int]]:
    
    Y = processing.get_spectrogram(audio)

    return processing.compute_constellation_map(Y)

def score_matches(matches: Dict, query_fingerprint):

    scored_matches = {}

    for match_song_id, offsets in matches.items():
        scored_matches[match_song_id] = processing.get_max_matches(
            database.SONGS_DB[match_song_id], query_fingerprint, offsets)
    
    return scored_matches


def query_song(audio: BytesIO) -> Dict[str, int]:
    
    fp = get_fingerprint(audio)

    hashes = hashing.hash_points(fp)

    matches = database.get_matches(hashes)

    return score_matches(matches, fp)
