from hashlib import sha256
from typing import Tuple, List, Generator
from settings import TARGET_ZONE_HEIGHT, TARGET_ZONE_TIME_OFFSET, TARGET_ZONE_WIDTH

def hash_point_pair(p1: Tuple[int, int], p2: Tuple[int, int]) -> str:
    """Helper function to generate a hash from two time/frequency points."""
    
    data_str = str((p1[0], p2[0], p2[1]-p1[1])).encode('utf-8')
    sha256_hash = sha256(data_str)
    return sha256_hash.hexdigest()

def target_zone(
        anchor: Tuple[int, int],
        points: List[Tuple[int, int]],
        width: float,
        height: float,
        t: float) -> Generator[Tuple[int, int], None, None]:
    """
    Adapted from: https://github.com/notexactlyawe/abracadabra/blob/master/abracadabra/fingerprint.py

    Generates a target zone as described in `the Shazam paper
    <https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf>`_.

    Given an anchor point, yields all points within a box that starts `t` seconds after the point,
    and has width `width` and height `height`.

    :param anchor: The anchor point
    :param points: The list of points to search
    :param width: The width of the target zone
    :param height: The height of the target zone
    :param t: How many seconds after the anchor point the target zone should start
    :returns: Yields all points within the target zone.
    """

    x_min = anchor[1] + t
    x_max = x_min + width
    y_min = anchor[0] - (height*0.5)
    y_max = y_min + height
    for point in points:
        if point[0] < y_min or point[0] > y_max:
            continue
        if point[1] < x_min or point[1] > x_max:
            continue
        yield point


def hash_points(
        points: List[Tuple[int, int]],
        song_id: int = None) -> List[Tuple[str, int, int]]:
    """
    Adapted from: https://github.com/notexactlyawe/abracadabra/blob/master/abracadabra/fingerprint.py

    Generates all hashes for a list of peaks.

    Iterates through the peaks, generating a hash for each peak within that peak's target zone.

    :param points: The list of peaks.
    :param filename: The filename of the song, used for generating song_id.
    :returns: A list of tuples of the form (hash, time offset, song_id).
    """
    hashes = []
    for anchor in points:
        
        for target in target_zone(
            anchor, points, TARGET_ZONE_WIDTH,
            TARGET_ZONE_HEIGHT, TARGET_ZONE_TIME_OFFSET
        ):
            
            hashes.append((
                # hash
                hash_point_pair(anchor, target),
                # time offset
                anchor[1],
                # filename
                song_id
            ))
    return hashes
