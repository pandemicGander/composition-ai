Place the midi file into raw midi

Run  [convert_octave_range_harmony.py](../src/convert_octave_range_harmony.py) or [convert_pure_harmony.py](../src/convert_pure_harmony.py) 

Then run [train_lstm_octave_range_harmony.py](../src/train_lstm_octave_range_harmony.py) or [train_lstm_pure_harmony.py](../src/train_lstm_pure_harmony.py)

Then run [predict_octave_range_harmony.py](../src/predict_octave_range_harmony.py) or [predict_pure_harmony.py](../src/predict_pure_harmony.py)

Then run convert again: [convert_octave_range_harmony.py](../src/convert_octave_range_harmony.py) or [convert_pure_harmony.py](../src/convert_pure_harmony.py) 

Use something like musescore to play the midi file found in [predicted_sequence_predicted.mid](../src/data/reconstructed_midi/predicted_sequence_predicted.mid)
