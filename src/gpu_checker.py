import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("Available Physical GPUs:", tf.config.list_physical_devices('GPU'))
