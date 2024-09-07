import numpy as np
from tensorflow.keras.models import load_model
from train_lstm import load_data, predict_next_sequence

def prepare_input_data(data, seq_length=16):
    sequences = []
    for i in range(len(data) - seq_length + 1):
        sequences.append(data[i:i + seq_length])
    sequences = np.array(sequences)
    print(f"Prepared input data with shape -> sequences: {sequences.shape}")
    return sequences

if __name__ == '__main__':
    model_path = 'models/lstm_model.h5'  # Updated to match train_lstm.py
    seq_length = 16
    num_features = 8  # Number of features per timestep

    # Load the input data using the load_data function from train_lstm.py
    input_file = 'data/example_input/example_1.txt'  # You'll need to create this file
    input_sequences, _ = load_data(input_file, seq_length)

    # Load the trained model
    model = load_model(model_path)
    model.summary()

    # Make a prediction using the predict_next_sequence function from train_lstm.py
    example_sequence = input_sequences[-1]  # Use the last sequence as an example
    predicted_sequence = predict_next_sequence(model, example_sequence)
    print(f"Predicted sequence: {predicted_sequence}")

    # Generate a full sequence prediction
    full_sequence = []
    current_input = input_sequences[-1].copy()

    for _ in range(16):  # Predict the next 16 timesteps
        next_step = predict_next_sequence(model, current_input)
        full_sequence.append(next_step)
        current_input = np.vstack((current_input[1:], next_step))

    # Save the original input and full sequence prediction to a single file
    combined_output_path = 'data/predictions/input_and_prediction.txt'
    with open(combined_output_path, 'w') as f:
        # Write original input
        for sequence in input_sequences:
            for timestep in sequence:
                f.write(','.join(map(str, timestep)) + '\n')

        # Write prediction
        for step in full_sequence:
            f.write(','.join(map(str, step.flatten())) + '\n')

    print(f"Original input and full sequence prediction saved to {combined_output_path}")

    # Remove individual prediction file saves
