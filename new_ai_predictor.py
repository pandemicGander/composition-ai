import numpy as np
import json
from tensorflow.keras.models import load_model

# Load the model
model = load_model('my_lstm_model.h5')

# Function to make predictions based on input sequences
def make_predictions(input_sequences):
  predictions = model.predict(input_sequences)
  # Scale back the predictions (since we normalized the pitch classes by dividing by 11)
  predictions = np.round(predictions * 11).astype(int)
  return predictions

# Load input data for predictions (e.g., from previously prepared sequences)
with open('pitch_classes.json', 'r') as file:
  input_data = json.load(file)

# Normalize and reshape input data for prediction
input_sequences = np.array(input_data)
input_sequences = input_sequences[:, :-1] / 11.0  # Normalize
input_sequences = input_sequences.reshape((input_sequences.shape[0], input_sequences.shape[1], 1))

# Predict new pitch classes
predicted_pitch_classes = make_predictions(input_sequences)
print("Predicted pitch classes:", predicted_pitch_classes)
