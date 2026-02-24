import numpy as np


SEQ_LENGTH = 10  # tiny for fast tests


class TestLoadDataFromFile:
    """Tests for load_data_from_file from each train_lstm_*.py module."""

    def test_correct_number_of_sequences(self, train_module, synthetic_data_file):
        seqs, nexts = train_module.load_data_from_file(synthetic_data_file, seq_length=SEQ_LENGTH)
        # 30 rows - 10 seq_length = 20 sequences
        assert len(seqs) == 20
        assert len(nexts) == 20

    def test_sequence_shape(self, train_module, synthetic_data_file, num_features):
        seqs, nexts = train_module.load_data_from_file(synthetic_data_file, seq_length=SEQ_LENGTH)
        seq = np.array(seqs[0])
        nxt = np.array(nexts[0])
        assert seq.shape == (SEQ_LENGTH, num_features)
        assert nxt.shape == (num_features,)

    def test_values_are_binary(self, train_module, synthetic_data_file):
        seqs, nexts = train_module.load_data_from_file(synthetic_data_file, seq_length=SEQ_LENGTH)
        all_vals = np.array(seqs).flatten().tolist() + np.array(nexts).flatten().tolist()
        assert set(all_vals) <= {0, 1}

    def test_empty_when_too_few_rows(self, train_module, tmp_path, num_features):
        """File with exactly seq_length rows should produce no sequences."""
        from helpers import generate_row
        p = tmp_path / 'short.txt'
        with open(str(p), 'w') as f:
            for _ in range(SEQ_LENGTH):
                f.write(','.join(str(b) for b in generate_row(num_features)) + '\n')
        seqs, nexts = train_module.load_data_from_file(str(p), seq_length=SEQ_LENGTH)
        assert seqs == []
        assert nexts == []

    def test_sliding_window_correctness(self, train_module, synthetic_data_file):
        """Sequence N should start at row N in the file."""
        seqs, _ = train_module.load_data_from_file(synthetic_data_file, seq_length=SEQ_LENGTH)
        # Read raw data for comparison
        with open(synthetic_data_file) as f:
            raw = [list(map(int, line.strip().split(','))) for line in f]
        for i in range(min(5, len(seqs))):
            assert seqs[i] == raw[i : i + SEQ_LENGTH]


class TestCountTotalSequences:
    """Tests for count_total_sequences."""

    def test_single_file(self, train_module, synthetic_data_file):
        count = train_module.count_total_sequences([synthetic_data_file], seq_length=SEQ_LENGTH)
        assert count == 20  # 30 - 10

    def test_multiple_files(self, train_module, synthetic_data_files):
        count = train_module.count_total_sequences(synthetic_data_files, seq_length=SEQ_LENGTH)
        assert count == 60  # 3 files * 20 sequences each

    def test_short_file_contributes_zero(self, train_module, tmp_path, num_features):
        from helpers import generate_row
        p = tmp_path / 'tiny.txt'
        with open(str(p), 'w') as f:
            for _ in range(5):
                f.write(','.join(str(b) for b in generate_row(num_features)) + '\n')
        count = train_module.count_total_sequences([str(p)], seq_length=SEQ_LENGTH)
        assert count == 0


class TestDataGenerator:
    """Tests for the infinite data_generator."""

    def test_batch_shapes(self, train_module, synthetic_data_files, num_features):
        gen = train_module.data_generator(synthetic_data_files, seq_length=SEQ_LENGTH, batch_size=4)
        X, y = next(gen)
        assert X.shape == (4, SEQ_LENGTH, num_features)
        assert y.shape == (4, num_features)

    def test_generator_loops_across_epochs(self, train_module, synthetic_data_files):
        """Generator should yield indefinitely (we pull more batches than one epoch)."""
        gen = train_module.data_generator(synthetic_data_files, seq_length=SEQ_LENGTH, batch_size=4)
        total_seqs = 60  # 3 files * 20 sequences
        batches_per_epoch = total_seqs // 4 + (1 if total_seqs % 4 else 0)
        # Pull 2x as many batches as one epoch to prove looping works
        for _ in range(batches_per_epoch * 2):
            X, y = next(gen)
            assert X.shape[0] <= 4

    def test_last_batch_may_be_smaller(self, train_module, synthetic_data_file):
        """With 20 sequences and batch_size=6, last batch should have 2 items."""
        gen = train_module.data_generator([synthetic_data_file], seq_length=SEQ_LENGTH, batch_size=6)
        sizes = []
        # One file produces 20 sequences = ceil(20/6)=4 batches: 6,6,6,2
        for _ in range(4):
            X, _ = next(gen)
            sizes.append(X.shape[0])
        assert min(sizes) < 6  # at least one batch is smaller
