import librosa
import numpy as np
from numpy.typing import NDArray
from scipy import ndimage
from settings import SPECTRUM_IMAGE_FILTER_SIZE, CONSTELLATION_SHAPE
from typing import List, Tuple
from io import BytesIO
from os import PathLike


def map_to_points(
    Cmap: NDArray
    ) -> List[Tuple[int, int]]:
    """
    Helper function to convert matrix constellation map to points list. Saves
    the `(x, y)` coordinates for every `True` entry.

    Args:
      Cmap (`NDArray`): Constellation map matrix.
    
    Returns:
      `List[Tuple[int, int]]`: List of consellation map points.
    """

    points = []

    for i, row in enumerate(Cmap):
        for j, val in enumerate(row):
            if val:
                points.append((i, j))

    points = np.array(points)
    
    return points

def get_spectrogram(
        wav: BytesIO | PathLike,
        Fs: int = 44100,
        bin_max: int = 128,
        duration: int = None,
        offset : int = None) -> NDArray:
    
    """
    Computes the spectrogram for an audio signal.

    Args:
      wav (`BytesIO` | `PathLike`): File (or filename) to be processed.
      Fs (`int`): Frequency sample of the audio in hertz (hz). Defaults to `44100`.
      bin_max (`int`): Number of maximum frequency bins to return. Defaults to `128`.
      duration (`int`): Optional maximum duration to be processed. If `None`, the whole
      audio will be processed. Defaults to `None`.
      offset (`int`): Optional offset to start the audio processing. If `None` the signal
      will be processed from the beggining. Defaults to `None`.
    
    Returns:
      `NDArray`: Audio spectrogram as matrix.
    """

    x, Fs = librosa.load(wav, sr=Fs,  duration=duration, offset=offset)
    
    X = librosa.stft(x, n_fft=4096, hop_length=1024)

    if bin_max is None:
        bin_max = X.shape[0]

    return np.abs(X[:bin_max, :])

def compute_constellation_map(
    spectrogram: NDArray,
    thresh: float = 0.01,
    size: int = SPECTRUM_IMAGE_FILTER_SIZE
    ) -> List[Tuple[int, int]]:
    """Computes constellation map (implementation using image processing)

    Adapted from: https://www.audiolabs-erlangen.de/resources/MIR/FMP/C7/C7S1_AudioIdentification.html

    Args:
        spectrogram (`NDArray`): Audio spectrogram matrix.
        thresh (`float`): Threshold parameter for minimal peak magnitude. Defaults to `0.01`.
        size (`int`): Spectrogram image filter size. Defaults to `DEFAULT_SPECTROGRAM_IMAGE_FILTER_SIZE`.

    Returns:
        `List[Tuple[int, int]]`: List of constellation map `True` points.
    """

    result = ndimage.maximum_filter(spectrogram, size=size, mode='constant')
    Cmap = np.logical_and(spectrogram == result, result > thresh)

    return map_to_points(Cmap)

def points_to_matrix(points: List[Tuple[int, int]]):
    """Helper function to convert points list to matrix constellation map.

    Args:
        points (``List[Tuple[int, int]]``): Points list.

    Returns:
        ``NDArray``: Constellation map matrix.
    """

    Cmap = np.full((CONSTELLATION_SHAPE[0]+1, np.max(points, axis=(0,1))+1), False)

    for point in points:
        Cmap[point[0], point[1]] = True
    
    return Cmap

def match_binary_matrices(matrix1: NDArray, matrix2: NDArray, tol_freq: int = 0, tol_time: int = 100):
    """
    Computes the number of matches between two binary matrices.

    Args:
        matrix1 (`NDArray`): First binary matrix.\n
        matrix2 (`NDArray`): Second binary matrix.\n

    Returns:
        ``int``: Matches between the two matrices.
    """

    matrix2_max = ndimage.maximum_filter(matrix2, size=(2*tol_freq+1, 2*tol_time+1),
                                       mode='constant')
    C_AND = np.logical_and(matrix1, matrix2_max)
    return np.sum(C_AND) / np.sum(np.logical_or(matrix1, matrix2))

def get_max_matches(
        db_cmap: List[Tuple[int, int]],
        query_cmap: List[Tuple[int, int]],
        offsets: List[int]):
    
    """
    Compares two constellation maps at different offsets and returns
    the maximum number of matches.

    Args:
        db_cmap (`List[Tuple[int, int]]`): Constellation map of the database audio. \n
        query_cmap (`List[Tuple[int, int]]`): Constellation map of the query audio. \n
        offsets (`List[int]`): List of offsets to be tested. \n

    Returns:
        ``int``: Maximum number of matches between the two constellation maps.
    """

    C_D = points_to_matrix(db_cmap)
    C_Q = points_to_matrix(query_cmap)

    N = C_Q.shape[1]

    max_matches = 0
    
    for m in offsets:
        C_D_crop = C_D[:, m:m+N]
        if C_D_crop.shape == C_Q.shape:
            TP = match_binary_matrices(C_D_crop, C_Q)
        else:
            sd = C_D_crop.shape[1] - C_Q.shape[1]
            TP = match_binary_matrices(C_D_crop, C_Q[:,:sd])
        if TP > max_matches:
            max_matches = TP
    
    return max_matches