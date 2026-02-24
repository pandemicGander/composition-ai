import os

import numpy as np
import pytest

from helpers import generate_row


SEQ_LENGTH = 10


@pytest.mark.slow
class TestEndToEndPipeline:
    """Full pipeline: build model -> train -> predict -> convert to MIDI."""

    def test_full_pipeline(self, train_module, converter_module, synthetic_data_files,
                           num_features, tmp_path):
        # 1. Build model
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))

        # 2. Train for 2 epochs
        gen = train_module.data_generator(
            synthetic_data_files, seq_length=SEQ_LENGTH, batch_size=4,
        )
        total_seqs = train_module.count_total_sequences(
            synthetic_data_files, seq_length=SEQ_LENGTH,
        )
        steps = max(1, total_seqs // 4)
        model.fit(gen, steps_per_epoch=steps, epochs=2, verbose=0)

        # 3. Predict 10 steps iteratively
        seed = np.array([generate_row(num_features) for _ in range(SEQ_LENGTH)])
        full_sequence = seed.copy()

        for _ in range(10):
            input_seq = full_sequence[-SEQ_LENGTH:]
            predicted = train_module.predict_next_sequence(model, input_seq)
            full_sequence = np.vstack([full_sequence, predicted])

        assert full_sequence.shape == (SEQ_LENGTH + 10, num_features)

        # 4. Convert predicted output to MIDI
        midi_path = str(tmp_path / 'pipeline_output.mid')
        converter_module.ai_format_to_midi(full_sequence.tolist(), midi_path)
        assert os.path.isfile(midi_path)
        assert os.path.getsize(midi_path) > 0
