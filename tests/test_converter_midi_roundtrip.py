import os
import importlib

import pytest


@pytest.mark.slow
class TestPureHarmonyRoundTrip:
    """Round-trip: ai_format_to_midi -> file -> midi_to_ai_format for pure_harmony."""

    def test_roundtrip_preserves_pitch_classes(self, tmp_path):
        mod = importlib.import_module('data_conversion.converter_pure_harmony')
        # Build a short sequence with C-major chord
        data = []
        for _ in range(8):
            row = [0] * 12
            row[0] = 1  # C
            row[4] = 1  # E
            row[7] = 1  # G
            data.append(row)

        midi_path = str(tmp_path / 'roundtrip.mid')
        mod.ai_format_to_midi(data, midi_path)
        assert os.path.isfile(midi_path)

        recovered = mod.midi_to_ai_format(midi_path)
        assert len(recovered) > 0
        # Each recovered row should have 12 features
        assert len(recovered[0]) == 12
        # Check that C, E, G are present in at least one row
        has_c = any(row[0] == 1 for row in recovered)
        has_e = any(row[4] == 1 for row in recovered)
        has_g = any(row[7] == 1 for row in recovered)
        assert has_c and has_e and has_g


@pytest.mark.slow
class TestOctaveRangeHarmonyRoundTrip:
    """Round-trip for octave_range_harmony."""

    def test_roundtrip_preserves_pitch_classes(self, tmp_path):
        mod = importlib.import_module('data_conversion.converter_octave_range_harmony')
        data = []
        for _ in range(8):
            row = [0] * 20
            row[0] = 1  # C
            row[4] = 1  # E
            row[7] = 1  # G
            row[15] = 1  # octave 4
            data.append(row)

        midi_path = str(tmp_path / 'roundtrip.mid')
        mod.ai_format_to_midi(data, midi_path)
        assert os.path.isfile(midi_path)

        recovered = mod.midi_to_ai_format(midi_path)
        assert len(recovered) > 0
        assert len(recovered[0]) == 20
        has_c = any(row[0] == 1 for row in recovered)
        has_e = any(row[4] == 1 for row in recovered)
        has_g = any(row[7] == 1 for row in recovered)
        assert has_c and has_e and has_g


@pytest.mark.slow
class TestExactHarmonyRoundTrip:
    """Round-trip for exact_harmony."""

    def test_roundtrip_preserves_pitch_classes(self, tmp_path):
        mod = importlib.import_module('data_conversion.converter_exact_harmony')
        data = []
        for _ in range(8):
            row = [0] * 108
            row[0] = 1  # C
            row[4] = 1  # E
            row[7] = 1  # G
            # Per-PC octave bits: octave 4 (index 3) for each PC
            row[12 + 0 * 8 + 3] = 1  # C octave 4
            row[12 + 4 * 8 + 3] = 1  # E octave 4
            row[12 + 7 * 8 + 3] = 1  # G octave 4
            data.append(row)

        midi_path = str(tmp_path / 'roundtrip.mid')
        mod.ai_format_to_midi(data, midi_path)
        assert os.path.isfile(midi_path)

        recovered = mod.midi_to_ai_format(midi_path)
        assert len(recovered) > 0
        assert len(recovered[0]) == 108
        has_c = any(row[0] == 1 for row in recovered)
        has_e = any(row[4] == 1 for row in recovered)
        has_g = any(row[7] == 1 for row in recovered)
        assert has_c and has_e and has_g
