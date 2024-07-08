import json
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from tensorflow.keras.models import load_model


# Load data from JSON file
with open('pitch_classes.json', 'r') as file:
  data = json.load(file)

# Convert to numpy array
sequences = np.array(data)

# Configuration
seq_length = 16  # Number of arrays in each sequence
n_features = 8   # Number of features in each array

# Prepare the dataset
X = []
y = []

for i in range(len(sequences) - seq_length):
  X.append(sequences[i:i + seq_length])
  y.append(sequences[i + seq_length])

X = np.array(X)
y = np.array(y)

# Normalize data
X = X / 11.0  # Normalizing pitch classes assuming they range from 0 to 11
y = y / 11.0  # Normalize output

# Reshape X for LSTM (samples, time steps, features)
X = X.reshape((X.shape[0], seq_length, n_features))

# Splitting data into training and validation sets
split_idx = int(0.8 * len(X))  # 80% for training, 20% for validation
X_train, X_val = X[:split_idx], X[split_idx:]
y_train, y_val = y[:split_idx], y[split_idx:]

# Build the LSTM model
model = Sequential([
    LSTM(100, return_sequences=True, activation='relu', input_shape=(seq_length, n_features),
         kernel_regularizer=l2(0.01)),  # L2 regularization
    Dropout(0.3),  # Increased dropout rate for better regularization
    LSTM(100, return_sequences=True, activation='relu'),
    Dropout(0.3),  # Consistent dropout after each LSTM layer
    LSTM(50, activation='relu'),
    Dense(n_features)  # Output layer should match the number of features
])

def train():
    model.compile(optimizer='adam', loss='mse')
    early_stopping = EarlyStopping(monitor='val_loss', patience=10)

    # Train the model
    model.fit(X_train, y_train, epochs=200, verbose=1, validation_data=(X_val, y_val), callbacks=[early_stopping])

    # Save the model
    model.save('my_lstm_model.h5')
    print("Model trained and saved.")


# Prediction Function
def predict_next_array(model, input_sequence):
    # Ensure the input is normalized and reshaped correctly
    input_sequence = np.array(input_sequence) / 11.0
    input_sequence = input_sequence.reshape((1, seq_length, n_features))

    # Predict the next array
    predicted_array = model.predict(input_sequence)
    predicted_array = predicted_array * 11.0  # De-normalize the output
    return predicted_array.round().astype(int)  # Return as integers


def predict():
    # Example usage with a custom input sequence
    custom_sequence = [
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


    model = load_model('my_lstm_model.h5')
    # Predict the next array
    next_array = predict_next_array(model, custom_sequence)
    print("Predicted next array:", next_array)

train()
predict()
