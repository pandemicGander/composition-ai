import os

from helpers import generate_row


class TestAiFormatToMidi:
    """Fast tests for ai_format_to_midi (no MIDI parsing, just file creation)."""

    def test_creates_midi_file(self, converter_module, num_features, tmp_path):
        data = [generate_row(num_features) for _ in range(20)]
        out = str(tmp_path / 'output.mid')
        converter_module.ai_format_to_midi(data, out)
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 0

    def test_all_silence(self, converter_module, num_features, tmp_path):
        """All-zeros input (silence) should still produce a valid MIDI file."""
        data = [[0] * num_features for _ in range(10)]
        out = str(tmp_path / 'silence.mid')
        converter_module.ai_format_to_midi(data, out)
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 0

    def test_single_note(self, converter_module, num_features, tmp_path):
        """A single C note should produce a valid MIDI file."""
        row = [0] * num_features
        row[0] = 1  # pitch class C
        if num_features == 20:
            row[12] = 1  # octave 1
        elif num_features == 108:
            row[12] = 1  # pitch class 0, octave 1
        data = [row] * 5
        out = str(tmp_path / 'single_note.mid')
        converter_module.ai_format_to_midi(data, out)
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 0

    def test_chord(self, converter_module, num_features, tmp_path):
        """C-major chord (C+E+G) should produce a valid MIDI file."""
        row = [0] * num_features
        row[0] = 1  # C
        row[4] = 1  # E
        row[7] = 1  # G
        if num_features == 20:
            row[15] = 1  # octave 4
        elif num_features == 108:
            row[12 + 0 * 8 + 3] = 1  # C in octave 4
            row[12 + 4 * 8 + 3] = 1  # E in octave 4
            row[12 + 7 * 8 + 3] = 1  # G in octave 4
        data = [row] * 5
        out = str(tmp_path / 'chord.mid')
        converter_module.ai_format_to_midi(data, out)
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 0
