import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import json

# Path to your file
file_path = 'sequences.txt'

# Read and parse the file
with open(file_path, 'r') as file:
  data = file.read()
  sequences = json.loads(data)

# Define the maximum pitch value for normalization
max_pitch = 127

# Convert 0s to -127 in sequences
sequences = [[-127 if pitch == 0 else pitch for pitch in sequence] for sequence in sequences]

# Preparing the data
X = []
y = []
sequence_length = 8  # Number of time steps in each input sequence

# Normalize the sequences and prepare input (X) and output (y)
for i in range(len(sequences) - sequence_length):
  X.append(sequences[i:i + sequence_length])  # Input: sequence of time steps
  y.append(sequences[i + sequence_length])    # Output: next time step

# Convert to numpy arrays and normalize
X = np.array(X) / max_pitch
y = np.array(y) / max_pitch

# Reshape X for LSTM: [samples, time steps, features]
X = X.reshape((len(X), sequence_length, 6))  # 6 features per time step

# Building the LSTM model
model = Sequential([
  LSTM(50, activation='relu', input_shape=(sequence_length, 6)),
  Dense(6)  # Outputting 6 features
])
model.compile(optimizer='adam', loss='mse')

# Training the model
model.fit(X, y, epochs=100, verbose=1)

# Saving the model
model.save('my_lstm_model_midi.h5')
