import os
import numpy as np
from model.lstm_model import build_lstm_model
from tensorflow.keras.callbacks import ModelCheckpoint

def load_data(file_path, seq_length=16):
    with open(file_path, 'r') as f:
        data = [list(map(int, line.strip().split(','))) for line in f]

    sequences = []
    labels = []

    for i in range(len(data) - seq_length):
        sequences.append(data[i:i + seq_length])
        labels.append(data[i + 1:i + seq_length + 1])  # Shifted sequence as label

    sequences = np.array(sequences)
    labels = np.array(labels)

    print(f"Loaded {file_path} with shapes -> sequences: {sequences.shape}, labels: {labels.shape}")

    return sequences, labels

if __name__ == '__main__':
    ai_format_folder = 'data/ai_format'
    model_save_path = 'models/best_model.h5'

    # Collect all data from files into a single dataset
    all_sequences = []
    all_labels = []

    for file_name in os.listdir(ai_format_folder):
        if file_name.endswith('_processed.txt'):
            file_path = os.path.join(ai_format_folder, file_name)
            seq_length = 16
            X, y = load_data(file_path, seq_length)
            all_sequences.append(X)
            all_labels.append(y)

    # Concatenate all sequences and labels from all files
    all_sequences = np.concatenate(all_sequences, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    print(f"Total shapes -> all_sequences: {all_sequences.shape}, all_labels: {all_labels.shape}")

    # Ensure labels are sequences of class indices
    try:
        # Flatten labels from (batch_size, seq_length, num_features) to (batch_size, seq_length)
        all_labels = np.argmax(all_labels, axis=-1)
        print(f"Shapes after flattening -> X: {all_sequences.shape}, y: {all_labels.shape}")
    except ValueError as e:
        print(f"Error during processing: {e}")
        # Additional debugging: Print the shape and content of labels
        print(f"Labels shape: {all_labels.shape}")
        print(f"First few labels: {all_labels[:5]}")

    # Build and train the model
    input_shape = (all_sequences.shape[1], all_sequences.shape[2])
    num_classes = np.max(all_labels) + 1  # Assuming labels are integers starting from 0

    model = build_lstm_model(input_shape, num_classes)
    checkpoint_callback = ModelCheckpoint(model_save_path, monitor='val_loss', save_best_only=True, mode='min')

    # Print model summary for debugging
    model.summary()

    model.fit(all_sequences, all_labels, epochs=50, batch_size=64, validation_split=0.2, shuffle=False, callbacks=[checkpoint_callback])

    # Evaluate the model
    loss, accuracy = model.evaluate(all_sequences, all_labels)
    print(f"Loss: {loss}, Accuracy: {accuracy}")

    # Save the model
    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")
