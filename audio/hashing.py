from hashlib import sha256
from typing import Tuple, List, Generator
from settings import TARGET_ZONE_HEIGHT, TARGET_ZONE_TIME_OFFSET, TARGET_ZONE_WIDTH

def hash_point_pair(
    anchor: Tuple[int, int],
    target: Tuple[int, int]) -> str:
    """
    Helper function to generate a hash from two time/frequency points.

    Args:
      anchor (`Tuple[int, int]`): Anchor point.
      target (`Tuple[int, int]`): Point from target zone.
    
    Returns:
      `str`: Hash.
    """
    
    data_str = str((anchor[0], target[0], target[1]-anchor[1])).encode('utf-8')
    sha256_hash = sha256(data_str)

    return sha256_hash.hexdigest()

def target_zone(
        anchor: Tuple[int, int],
        points: List[Tuple[int, int]],
        width: float,
        height: float,
        offset: float
        ) -> Generator[Tuple[int, int], None, None]:
    """
    Adapted from: https://github.com/notexactlyawe/abracadabra/blob/master/abracadabra/fingerprint.py

    Generates a target zone.

    Given an anchor point, yields all points within a box that starts `t` seconds after the point,
    and has width `width` and height `height`.

    Args:
      anchor (`Tuple[int, int]`): Anchor point.
      points (`List[Tuple[int, int]]`): List of constellation map points.
      width (`float`): Target zone width.
      height (`float`): Target zone height.
      offset (`float`): How many units in time after the anchor point the target zone should start.

    Returns:
      `Generator[Tuple[int, int], None, None]`: Generator of points inside target zone.
    """

    x_min = anchor[1] + offset
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
        points : List[Tuple[int, int]],
        song_id : int = None,
        tz_width : float = TARGET_ZONE_WIDTH,
        tz_height : float = TARGET_ZONE_HEIGHT,
        tz_offset : float = TARGET_ZONE_TIME_OFFSET
        ) -> List[Tuple[str, int, int]]:
    """
    Adapted from: https://github.com/notexactlyawe/abracadabra/blob/master/abracadabra/fingerprint.py

    Generates all hashes for a constellation map.

    Iterates through the peaks, generating a hash for each peak within that peak's target zone.

    Args:
      points (`List[Tuple[int, int]]`): List of constellation map points.
      song_id (`int`): ID to include in hashes list. Default to `None`.
      tz_width (`float`): Target zone width. Defaults to `DEFAULT_TARGET_ZONE_WIDTH`.
      tz_height (`float`): Target zone height. Defaults to `DEFAULT_TARGET_ZONE_HEIGHT`.
      tz_offset (`float`): Target zone time offset. Defaults to `DEFAULT_TARGET_ZONE_TIME_OFFSET`.

    Returns:
      `List[Tuple[str, int, int]]`: List of hashes in the form of `(hash, anchor_time_offset, song_id)`.
    """

    hashes = []

    for anchor in points:
        
        for target in target_zone(
            anchor, points, tz_width,
            tz_height, tz_offset
        ):
            
            hashes.append((
                hash_point_pair(anchor, target),
                anchor[1],
                song_id
            ))
    return hashes