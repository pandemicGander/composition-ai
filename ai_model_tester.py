import numpy as np
from tensorflow.keras.models import load_model

# Load the model
model = load_model('my_lstm_model.h5')
def generate_sequence(start, increment, length=30):
  return [start + i * increment for i in range(length)]


test_inc = 1.5
test_start = 3
test_array = generate_sequence(test_start, test_inc, 5)
# split the array into two, take the last element out into its own variable
test_array, test_array_last = test_array[:-1], test_array[-1]
print("Test sequence:", test_array)
print("Expected next:", test_array_last)
# Predicting a new sequence
test_sequence = np.array(test_array).reshape((1, 4, 1)) / 10.0
prediction = model.predict(test_sequence) * 10
print("Predicted sequence:", prediction)

