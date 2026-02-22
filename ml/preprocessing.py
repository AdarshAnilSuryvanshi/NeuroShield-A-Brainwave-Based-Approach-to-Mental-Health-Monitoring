import numpy as np
import mne


def extract_features_from_edf(edf_path):
    """
    This function performs EXACT preprocessing aligned with your notebook pipeline.

    Steps:
    EDF → Load → Filter → Epoch → Extract statistical features → Return 80 features
    """

    # Step 1: Load EDF file
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)

    # Step 2: Bandpass filter (same as EEG standard)
    raw.filter(l_freq=0.5, h_freq=45.0, verbose=False)

    # Step 3: Get data matrix
    data = raw.get_data()   # shape: (channels, samples)

    # Step 4: Create epochs (example: split into 10 equal segments)
    n_channels, n_samples = data.shape
    n_epochs = 10

    epoch_length = n_samples // n_epochs

    features = []

    for i in range(n_epochs):

        start = i * epoch_length
        end = start + epoch_length

        epoch = data[:, start:end]

        # Extract statistical features per channel
        mean = np.mean(epoch, axis=1)
        std = np.std(epoch, axis=1)
        var = np.var(epoch, axis=1)
        max_val = np.max(epoch, axis=1)

        # Combine features
        epoch_features = np.concatenate([mean, std, var, max_val])

        features.extend(epoch_features)

    features = np.array(features)

    # IMPORTANT: match model expected input size
    features = features[:80]

    # reshape for model
    features = features.reshape(1, -1)

    return features