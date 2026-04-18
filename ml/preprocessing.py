import numpy as np
import mne


def extract_features_from_edf(edf_path):
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
    raw.filter(l_freq=0.5, h_freq=45.0, verbose=False)

    data = raw.get_data()

    n_channels, n_samples = data.shape
    n_epochs = 10
    epoch_length = n_samples // n_epochs

    features = []

    for i in range(n_epochs):
        start = i * epoch_length
        end = start + epoch_length
        epoch = data[:, start:end]

        mean = np.mean(epoch, axis=1)
        std = np.std(epoch, axis=1)
        var = np.var(epoch, axis=1)
        max_val = np.max(epoch, axis=1)

        epoch_features = np.concatenate([mean, std, var, max_val])
        features.extend(epoch_features)

    features = np.array(features)
    features = features[:80]
    features = features.reshape(1, -1)

    return features


def summarize_features(features):
    arr = np.asarray(features).reshape(-1)

    return {
        "feature_count": int(arr.shape[0]),
        "feature_mean": float(np.mean(arr)),
        "feature_std": float(np.std(arr)),
        "feature_min": float(np.min(arr)),
        "feature_max": float(np.max(arr)),
        "first_10_features": [float(x) for x in arr[:10]],
    }