import numpy as np
from tensorflow.keras.models import load_model

# Load the model
model = load_model('my_lstm_model_midi.h5')

# Define the maximum pitch value for normalization and denormalization
max_pitch = 127

# Initial sequence
initial_sequence = np.array([[50, 50, 50, 54, 57, 0], [50, 50, 50, 54, 57, 0], [50, 50, 54, 57, 57, 0], [50, 50, 54, 57, 57, 0], [50, 62, 0, 0, 0, 0], [50, 62, 0, 0, 0, 0], [50, 66, 0, 0, 0, 0], [50, 66, 0, 0, 0, 0]])

# Normalize the sequence
initial_sequence_normalized = initial_sequence / max_pitch

# Reshape the sequence for the model
initial_sequence_normalized = initial_sequence_normalized.reshape((1, 8, 6))

# Number of times to predict the next sequence
num_predictions = 100  # Set the number of predictions

# List to accumulate predictions, starting with each sequence in the initial sequence
all_predictions = [seq.tolist() for seq in initial_sequence]

filter_low_notes_under = 15  # Set the minimum note value to filter out
filter_high_notes_over = 127  # Set the maximum note value to filter out

# Predict the next sequence multiple times
for _ in range(num_predictions):
  # Predict the next sequence
  predicted_sequence_normalized = model.predict(initial_sequence_normalized)

  # Denormalize the predicted sequence
  predicted_sequence = predicted_sequence_normalized * max_pitch

  # Round to the nearest integer
  predicted_sequence = np.rint(predicted_sequence).astype(int)

  # Filter both low and high notes
  predicted_sequence = np.where(
      (predicted_sequence < filter_low_notes_under) | (predicted_sequence > filter_high_notes_over),
      0,
      predicted_sequence
  )

  # Add the predicted sequence to the list of all predictions
  all_predictions.append(predicted_sequence[0].tolist())

  # Use the predicted sequence as the input for the next prediction
  # Shift the sequence by one time step and insert the new prediction
  initial_sequence_normalized = np.roll(initial_sequence_normalized, -1, axis=1)
  initial_sequence_normalized[0, -1, :] = predicted_sequence_normalized[0, :]

# Print all the predictions along with the initial sequence as a nested array
print("All Sequences (Initial + Predicted):", all_predictions)
