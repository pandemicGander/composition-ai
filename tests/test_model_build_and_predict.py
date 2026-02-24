import numpy as np


SEQ_LENGTH = 10  # tiny for fast tests


class TestBuildModel:
    """Tests for build_lstm_model."""

    def test_model_creates_successfully(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        assert model is not None

    def test_input_output_shapes(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        assert model.input_shape == (None, SEQ_LENGTH, num_features)
        assert model.output_shape == (None, num_features)

    def test_layer_count(self, train_module, num_features):
        """Model should have 6 layers: LSTM, Dropout, LSTM, Dropout, LSTM, Dense."""
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        assert len(model.layers) == 6

    def test_layer_types(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        layer_types = [type(l).__name__ for l in model.layers]
        assert layer_types == ['LSTM', 'Dropout', 'LSTM', 'Dropout', 'LSTM', 'Dense']

    def test_sigmoid_activation(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        dense_layer = model.layers[-1]
        assert dense_layer.get_config()['activation'] == 'sigmoid'

    def test_binary_crossentropy_loss(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        assert 'binary_crossentropy' in str(model.loss)


class TestPredictNextSequence:
    """Tests for predict_next_sequence."""

    def test_returns_correct_shape(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        input_seq = np.zeros((SEQ_LENGTH, num_features))
        result = train_module.predict_next_sequence(model, input_seq)
        assert result.shape == (num_features,)

    def test_returns_binary_values(self, train_module, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        input_seq = np.random.rand(SEQ_LENGTH, num_features)
        result = train_module.predict_next_sequence(model, input_seq)
        assert set(result.flatten().tolist()) <= {0, 1}

    def test_predict_module_matches_train_module(self, train_module, predict_module, num_features):
        """predict_*.py and train_lstm_*.py both define predict_next_sequence; verify they agree."""
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        input_seq = np.zeros((SEQ_LENGTH, num_features))
        result_train = train_module.predict_next_sequence(model, input_seq)
        result_predict = predict_module.predict_next_sequence(model, input_seq)
        np.testing.assert_array_equal(result_train, result_predict)


class TestMinimalTraining:
    """Verify that a tiny training run completes without errors."""

    def test_training_completes(self, train_module, synthetic_data_files, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        gen = train_module.data_generator(synthetic_data_files, seq_length=SEQ_LENGTH, batch_size=4)
        total_seqs = train_module.count_total_sequences(synthetic_data_files, seq_length=SEQ_LENGTH)
        steps = max(1, total_seqs // 4)
        history = model.fit(gen, steps_per_epoch=steps, epochs=2, verbose=0)
        assert history is not None

    def test_training_loss_is_finite(self, train_module, synthetic_data_files, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        gen = train_module.data_generator(synthetic_data_files, seq_length=SEQ_LENGTH, batch_size=4)
        total_seqs = train_module.count_total_sequences(synthetic_data_files, seq_length=SEQ_LENGTH)
        steps = max(1, total_seqs // 4)
        history = model.fit(gen, steps_per_epoch=steps, epochs=2, verbose=0)
        for loss_val in history.history['loss']:
            assert np.isfinite(loss_val)

    def test_prediction_after_training(self, train_module, synthetic_data_files, num_features):
        model = train_module.build_lstm_model((SEQ_LENGTH, num_features))
        gen = train_module.data_generator(synthetic_data_files, seq_length=SEQ_LENGTH, batch_size=4)
        model.fit(gen, steps_per_epoch=5, epochs=2, verbose=0)
        input_seq = np.random.rand(SEQ_LENGTH, num_features)
        result = train_module.predict_next_sequence(model, input_seq)
        assert result.shape == (num_features,)
        assert set(result.flatten().tolist()) <= {0, 1}
