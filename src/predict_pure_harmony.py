import numpy as np
from tensorflow.keras.models import load_model
from train_lstm_pure_harmony import predict_next_sequence

def load_data(file_path):
  with open(file_path, 'r') as f:
    data = [list(map(int, line.strip().split(','))) for line in f]
  return np.array(data)

if __name__ == '__main__':
  model_path = 'models/lstm_pure_harmony_model.h5'

  # Load the trained model
  model = load_model(model_path)
  model.summary()

  # Load the input data
  input_file = 'data/example_input/example_1.txt'
  input_data = load_data(input_file)

  # Generate a sequence prediction
  full_sequence = input_data.copy()
  num_predictions = 16

  for i in range(num_predictions):
    # Get the last seq_length timesteps
    seq_length = model.input_shape[1]
    if len(full_sequence) < seq_length:
      current_input = np.pad(full_sequence, ((seq_length - len(full_sequence), 0), (0, 0)), mode='constant')
    else:
      current_input = full_sequence[-seq_length:]

    # Predict the next step
    predicted_next = predict_next_sequence(model, current_input)
    # Append the next step to the full sequence
    full_sequence = np.vstack((full_sequence, predicted_next))

  # Save the full sequence to a file
  output_path = 'data/predictions/predicted_sequence.txt'
  with open(output_path, 'w') as f:
    for vector in full_sequence:
      f.write(','.join(map(str, vector)) + '\n')

  print(f"Full sequence prediction saved to {output_path}")
