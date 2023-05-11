import librosa
import numpy as np
from numpy.typing import NDArray
from scipy import ndimage
from settings import SPECTRUM_IMAGE_FILTER_SIZE, CONSTELLATION_SHAPE
from typing import List, Tuple
from io import BytesIO


def map_to_points(Cmap: NDArray) -> NDArray:
    
    points = []

    for i, row in enumerate(Cmap):
        for j, val in enumerate(row):
            if val:
                points.append((i, j))

    points = np.array(points)
    
    return points

def compute_spectrogram(
        fn_wav: BytesIO,
        Fs: int = 22050,
        bin_max: int = 128,
        frame_max: int = None) -> NDArray:
    
    """Adapted from: https://www.audiolabs-erlangen.de/resources/MIR/FMP/C7/C7S1_AudioIdentification.html

    No documentation.
    """

    x, Fs = librosa.load(fn_wav, sr=Fs)
    X = librosa.stft(x)
    if bin_max is None:
        bin_max = X.shape[0]
    if frame_max is None:
        frame_max = X.shape[0]
    Y = np.abs(X[:bin_max, :frame_max])
    return Y

def compute_constellation_map(Y: NDArray, thresh: float = 0.01) -> List[Tuple[int,int]]:
    """Compute constellation map (implementation using image processing)

    Adapted from: https://www.audiolabs-erlangen.de/resources/MIR/FMP/C7/C7S1_AudioIdentification.html

    Args:
        Y (np.ndarray): Spectrogram (magnitude)
        dist_freq (int): Neighborhood parameter for frequency direction (kappa) (Default value = 7)
        dist_time (int): Neighborhood parameter for time direction (tau) (Default value = 7)
        thresh (float): Threshold parameter for minimal peak magnitude (Default value = 0.01)

    Returns:
        Cmap (np.ndarray): Boolean mask for peak structure (same size as Y)
    """
    
    result = ndimage.maximum_filter(Y, size=SPECTRUM_IMAGE_FILTER_SIZE, mode='constant')
    Cmap = np.logical_and(Y == result, result > thresh)

    return map_to_points(Cmap)

def match_binary_matrices_tol(C_ref, C_est, tol_freq=0, tol_time=0):
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
    N = np.sum(C_ref)
    M = np.sum(C_est)
    # Expand C_est with 2D-max-filter using the tolerance parameters
    C_est_max = ndimage.maximum_filter(C_est, size=(2*tol_freq+1, 2*tol_time+1),
                                       mode='constant')
    C_AND = np.logical_and(C_est_max, C_ref)
    TP = np.sum(C_AND)
    FN = N - TP
    FP = M - TP
    return TP, FN, FP, C_AND

def points_to_matrix(points):
    Cmap = np.full(CONSTELLATION_SHAPE, False)

    for point in points:
        np.put(Cmap, point, True)
    
    return Cmap



def score_similarity(C_D, C_Q, tol_freq=1, tol_time=1):
    """
    Adapted from: https://www.audiolabs-erlangen.de/resources/MIR/FMP/C7/C7S1_AudioIdentification.html

    Computes matching function for constellation maps

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

    L = C_D.shape[1]
    N = C_Q.shape[1]
    M = L - N
    assert M >= 0, "Query must be shorter than document"
    max_matching_points = 0
    for m in range(M + 1):
        C_D_crop = C_D[:, m:m+N]
        TP, FN, FP, C_AND = match_binary_matrices_tol(C_D_crop, C_Q,
                                                      tol_freq=tol_freq, tol_time=tol_time)
        if max_matching_points < TP:
            max_matching_points = TP
    
    return int(max_matching_points)
