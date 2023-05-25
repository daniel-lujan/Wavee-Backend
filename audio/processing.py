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

def match_binary_matrices_tol(C_ref, C_est, tol_freq=4, tol_time=0):
    """| Compare binary matrices with tolerance
    | Note: The tolerance parameters should be smaller than the minimum distance of
      peaks (1-entries in C_ref ad C_est) to obtain meaningful TP, FN, FP values

    Notebook: C7/C7S1_AudioIdentification.ipynb

    Args:
        C_ref (np.ndarray): Binary matrix used as reference
        C_est (np.ndarray): Binary matrix used as estimation
        tol_freq (int): Tolerance in frequency direction (vertical) (Default value = 0)
        tol_time (int): Tolerance in time direction (horizontal) (Default value = 0)

    Returns:
        TP (int): True positives
        FN (int): False negatives
        FP (int): False positives
        C_AND (np.ndarray): Boolean mask of AND of C_ref and C_est (with tolerance)
    """
    assert C_ref.shape == C_est.shape, "Dimensions need to agree"
    # Expand C_est with 2D-max-filter using the tolerance parameters
    C_est_max = ndimage.maximum_filter(C_est, size=SPECTRUM_IMAGE_FILTER_SIZE,
                                       mode='constant')
    C_AND = np.logical_and(C_est_max, C_ref)
    TP = np.sum(C_AND)
    return TP

def points_to_matrix(points):
    Cmap = np.full((CONSTELLATION_SHAPE[0]+1, np.max(points, axis=(0,1))+1), False)

    for point in points:
        Cmap[point[0], point[1]] = True
    
    return Cmap

def compute_matching_function(C_D, C_Q, offsets):
    """Computes matching function for constellation maps

    Notebook: C7/C7S1_AudioIdentification.ipynb

    Args:
        C_D (np.ndarray): Binary matrix used as dababase document
        C_Q (np.ndarray): Binary matrix used as query document
        tol_freq (int): Tolerance in frequency direction (vertical) (Default value = 1)
        tol_time (int): Tolerance in time direction (horizontal) (Default value = 1)

    Returns:
        Delta (np.ndarray): Matching function
        shift_max (int): Optimal shift position maximizing Delta
    """

    C_D = points_to_matrix(C_D)
    C_Q = points_to_matrix(C_Q)

    N = C_Q.shape[1]

    max_matches = 0
    
    for m in offsets:
        C_D_crop = C_D[:, m:m+N]
        TP = match_binary_matrices_tol(C_D_crop, C_Q)
        if TP > max_matches:
            max_matches = TP
    
    return int(max_matches)