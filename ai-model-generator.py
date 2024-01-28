import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Function to generate sequences
def generate_sequence(start, increment, length=30):
  return [start + i * increment for i in range(length)]

# Generate sequences
sequences = [generate_sequence(1, i) for i in range(1, 50)]

# Preparing the data
X = []
y = []
for seq in sequences:
  for i in range(len(seq) - 4):  # Adjust the range to avoid 'index out of range'
    X.append(seq[i:i+4])  # Input sequences of length 4
    y.append(seq[i+4])    # Next number in the sequence

# Normalizing and reshaping the data
X = np.array(X) / 10.0
y = np.array(y) / 10.0
X = X.reshape((len(X), 4, 1))  # Reshaping to (samples, time steps, features)

# Building the LSTM model
model = Sequential([
  LSTM(50, activation='relu', input_shape=(4, 1)),  # 4 time steps
  Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# Training the model
model.fit(X, y, epochs=10000, verbose=0)
model.save('my_lstm_model.h5')  # Saves the model
