import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split
import tensorflow as tf

# Optional: Set memory growth so TF doesn't grab all GPU memory at once.
# This helps avoid fragmentation issues.
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("Enabled GPU memory growth")
    except RuntimeError as e:
        print(e)

def load_data_from_file(file_path, seq_length=100):
    """
    Loads sequences and corresponding 'next' steps from a single file.
    Returns two lists: (sequences, next_sequences).
    Each entry in 'sequences' is shape [seq_length, features],
    and each entry in 'next_sequences' is shape [features].
    """
    with open(file_path, 'r') as f:
        data = [list(map(int, line.strip().split(','))) for line in f]

    # If there aren't enough steps to form a single sequence, return empty
    if len(data) <= seq_length:
        return [], []

    sequences = []
    next_sequences = []

    for i in range(len(data) - seq_length):
        sequences.append(data[i:i + seq_length])
        next_sequences.append(data[i + seq_length])

    return sequences, next_sequences


def data_generator(file_paths, seq_length=100, batch_size=32):
    """
    A generator that streams data from multiple files (songs).
    Yields (X_batch, y_batch) tuples indefinitely.
    """
    while True:  # Loop forever so Keras can train for multiple epochs
        for file_path in file_paths:
            seqs, next_seqs = load_data_from_file(file_path, seq_length)

            # If the file doesn't have enough data, skip
            if not seqs:
                continue

            # Slice into batches
            for i in range(0, len(seqs), batch_size):
                X_batch = seqs[i : i + batch_size]
                y_batch = next_seqs[i : i + batch_size]

                # Convert to numpy arrays
                X_batch = np.array(X_batch)
                y_batch = np.array(y_batch)

                yield (X_batch, y_batch)


def count_total_sequences(file_paths, seq_length=100):
    """
    Counts the total number of sequences across all files,
    so we can compute steps_per_epoch for model.fit.
    """
    total = 0
    for fp in file_paths:
        with open(fp, 'r') as f:
            data = f.readlines()
        # Each valid sequence has length seq_length, so we can form (len(data) - seq_length) sequences
        file_seq_count = max(0, len(data) - seq_length)
        total += file_seq_count
    return total


def build_lstm_model(input_shape):
    """
    Builds and compiles the LSTM model.
    :param input_shape: tuple, e.g. (seq_length, num_features)
    """
    model = Sequential([
        LSTM(128, input_shape=input_shape, return_sequences=True),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dense(20, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy')
    return model


def predict_next_sequence(model, input_sequence):
    """
    Given a single sequence (shape [seq_length, features]),
    predict the next step (shape [features]).
    """
    input_sequence = np.expand_dims(input_sequence, axis=0)  # shape becomes (1, seq_length, features)
    prediction = model.predict(input_sequence)[0]           # shape becomes (features,)
    return (prediction > 0.5).astype(int)


if __name__ == '__main__':

    seq_length = 100
    batch_size = 32
    epochs = 50

    ai_format_folder = 'data/ai_format'
    model_save_path = 'models/lstm_octave_range_harmony_model.keras'

    # 1. Gather all file paths
    all_file_paths = [
        os.path.join(ai_format_folder, fn)
        for fn in os.listdir(ai_format_folder)
        if fn.endswith('_processed.txt')
    ]

    # 2. Split file paths into train/val
    train_files, val_files = train_test_split(all_file_paths, test_size=0.2, shuffle=True)

    # 3. Count total sequences in each set
    total_train_sequences = count_total_sequences(train_files, seq_length)
    total_val_sequences = count_total_sequences(val_files, seq_length)

    # 4. Calculate steps
    steps_per_epoch = max(1, total_train_sequences // batch_size)
    validation_steps = max(1, total_val_sequences // batch_size)

    # 5. Create data generators
    train_gen = data_generator(train_files, seq_length=seq_length, batch_size=batch_size)
    val_gen = data_generator(val_files, seq_length=seq_length, batch_size=batch_size)

    # 6. Build model
    #   We need an input shape: (seq_length, num_features).
    #   We can guess num_features=20 if that's what's in your data (based on the final Dense(20)).
    #   Alternatively, we might dynamically find the # of features by reading the first file.
    #   For simplicity, we assume 20 features per step.
    model = build_lstm_model((seq_length, 20))

    # 7. Set up checkpoints
    checkpoint_callback = ModelCheckpoint(model_save_path, save_best_only=True, monitor='val_loss')

    # 8. Train
    model.fit(
        train_gen,
        steps_per_epoch=steps_per_epoch,
        validation_data=val_gen,
        validation_steps=validation_steps,
        epochs=epochs,
        callbacks=[checkpoint_callback]
    )

    # 9. Example: Load one file from validation set in memory to do a quick example prediction
    if val_files:
        example_file = val_files[-1]
        sequences, next_sequences = load_data_from_file(example_file, seq_length=seq_length)
        if sequences:
            example_sequence = sequences[-1]  # The last sequence from this file
            predicted_next_sequence = predict_next_sequence(model, example_sequence)

            print("Example input sequence (last one from validation file):")
            for seq_step in example_sequence:
                print(','.join(map(str, seq_step)))

            print("\nPredicted next sequence:")
            print(','.join(map(str, predicted_next_sequence)))
        else:
            print("No sequences found in the example validation file.")
    else:
        print("No validation files to demonstrate a prediction.")
