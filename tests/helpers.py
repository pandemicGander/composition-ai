"""Shared test helpers that can be imported by test modules."""
import random


def generate_row(num_features):
    """Generate a musically-plausible binary vector.

    For all variants the first 12 bits are pitch classes.
    We set a C-major chord (C=0, E=4, G=7) with some randomness.
    For octave_range_harmony (20) we also set one octave bit (bits 12-19).
    For exact_harmony (108) we set per-pitch-class octave bits.
    """
    row = [0] * num_features

    # Randomly choose between silence and a chord
    if random.random() < 0.15:
        return row  # rest

    # Set some pitch classes (C-major chord with occasional extras)
    active_pcs = [0, 4, 7]  # C, E, G
    if random.random() < 0.3:
        active_pcs.append(random.choice([2, 5, 9, 11]))  # add D, F, A, or B
    for pc in active_pcs:
        row[pc] = 1

    if num_features == 20:
        # octave_range_harmony: shared octave bits at indices 12-19
        octave = random.randint(0, 7)  # octaves 1-8 mapped to bits 12-19
        row[12 + octave] = 1
    elif num_features == 108:
        # exact_harmony: per-pitch-class octave bits
        for pc in active_pcs:
            octave = random.randint(0, 7)
            row[12 + pc * 8 + octave] = 1

    return row
