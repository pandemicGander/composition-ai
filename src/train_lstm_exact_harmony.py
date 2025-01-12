import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split

def load_data(file_path, seq_length=100):
    with open(file_path, 'r') as f:
        data = [list(map(int, line.strip().split(','))) for line in f]

    sequences = []
    next_sequences = []

    # Ensure that we have enough data to create at least one sequence
    if len(data) <= seq_length:
        return sequences, next_sequences

    for i in range(len(data) - seq_length):
        sequences.append(data[i:i + seq_length])
        next_sequences.append(data[i + seq_length])

    return sequences, next_sequences

def build_lstm_model(input_shape):
    model = Sequential([
        LSTM(128, input_shape=input_shape, return_sequences=True),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dense(96, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy')
    return model

def train_model(X, y, model_save_path):
    # Shuffle the dataset before splitting
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

    input_shape = (X_train.shape[1], X_train.shape[2])

    model = build_lstm_model(input_shape)

    checkpoint_callback = ModelCheckpoint(model_save_path, save_best_only=True, monitor='val_loss')

    model.fit(X_train, y_train,
              epochs=50,
              batch_size=32,
              validation_data=(X_val, y_val),
              callbacks=[checkpoint_callback],
              shuffle=False)

    return model

def predict_next_sequence(model, input_sequence):
    input_sequence = np.expand_dims(input_sequence, axis=0)
    prediction = model.predict(input_sequence)[0]
    return (prediction > 0.5).astype(int)

if __name__ == '__main__':
    ai_format_folder = 'data/ai_format'
    model_save_path = 'models/lstm_exact_harmony_model.h5'

    all_sequences = []
    all_next_sequences = []

    for file_name in os.listdir(ai_format_folder):
        if file_name.endswith('_processed.txt'):
            file_path = os.path.join(ai_format_folder, file_name)
            sequences, next_sequences = load_data(file_path, seq_length=100)
            all_sequences.extend(sequences)
            all_next_sequences.extend(next_sequences)

    # Convert lists to numpy arrays
    X = np.array(all_sequences)
    y = np.array(all_next_sequences)

    model = train_model(X, y, model_save_path)

    # Example prediction
    example_sequence = X[-1]  # Use the last sequence as an example
    predicted_next_sequence = predict_next_sequence(model, example_sequence)

    print("Example sequence:")
    for seq in example_sequence:
        print(','.join(map(str, seq)))

    print("\nPredicted next sequence:")
    print(','.join(map(str, predicted_next_sequence)))
