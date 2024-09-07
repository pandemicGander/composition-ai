import numpy as np
from tensorflow.keras.models import load_model

def prepare_input_data(data, seq_length=16):
    sequences = []
    for i in range(len(data) - seq_length + 1):
        sequences.append(data[i:i + seq_length])
    sequences = np.array(sequences)
    print(f"Prepared input data with shape -> sequences: {sequences.shape}")
    return sequences

if __name__ == '__main__':
    model_path = 'models/best_model.h5'
    seq_length = 16

    # Define the input data
    input_data = [
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [2, 2, 2, 6, 6, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9],
        [1, 1, 4, 4, 4, 9, 9, 9]
    ]

    # Prepare the input data for the model
    input_data = np.array(input_data)
    input_sequences = prepare_input_data(input_data)

    # Load the trained model
    model = load_model(model_path)
    model.summary()

    # Make a prediction
    prediction = model.predict(input_sequences)
    print(f"Prediction raw output: {prediction}")

    # Decode the prediction
    predicted_sequence = np.argmax(prediction, axis=-1)
    print(f"Predicted sequence (decoded): {predicted_sequence}")

    # Print predicted probabilities for the first timestep
    print(f"Predicted probabilities for the first timestep:\n{prediction[0][0]}")

    # Optionally, map the predicted indices back to the original note values
    original_notes = input_data
    predicted_notes = [original_notes[i, pred] for i, pred in enumerate(predicted_sequence[0])]
    print(f"Predicted notes: {predicted_notes}")

    # Save the predicted sequence to a file for further analysis
    output_path = 'data/predictions/predicted_sequence.txt'
    with open(output_path, 'w') as f:
        f.write(','.join(map(str, predicted_notes)) + '\n')
    print(f"Predicted sequence saved to {output_path}")
