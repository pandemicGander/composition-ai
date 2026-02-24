# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Music composition AI that uses LSTM neural networks (TensorFlow/Keras) to learn harmonic patterns from MIDI files and generate new musical sequences. Python 3.10.16.

## Commands

```bash
pip install -r requirements.txt          # Install dependencies
pytest tests/                            # Run all tests
pytest tests/test_converter.py           # Run a single test file
python src/gpu_checker.py                # Check GPU availability
```

## Pipeline Workflow

The project is a four-stage pipeline. All scripts use `__file__`-relative paths, so they can be run from any working directory:

1. **Convert MIDI → AI format**: `python src/convert_<variant>.py` (reads `src/data/raw_midi/`, writes `src/data/ai_format/<variant>/`)
2. **Train LSTM**: `python src/train_lstm_<variant>.py` (reads `src/data/ai_format/<variant>/`, saves model to `models/`)
3. **Predict/Generate**: `python src/predict_<variant>.py` (loads model, reads `src/data/example_input/example_<variant>.txt`, writes `src/data/predictions/<variant>/`)
4. **Reconstruct MIDI**: Run the same convert script again to convert predictions back to MIDI (writes `src/data/reconstructed_midi/`)

Replace `<variant>` with one of: `pure_harmony`, `octave_range_harmony`, `exact_harmony`.

Each variant uses its own subdirectories for ai_format and predictions to prevent cross-variant data contamination.

## Architecture

### Three Encoding Variants

Each variant has its own converter, training script, prediction script, and example input:

| Variant | Bits per timestep | What it encodes |
|---|---|---|
| `pure_harmony` | 12 | Pitch classes only (C, C#, ..., B) |
| `octave_range_harmony` | 20 | 12 pitch classes + 8 octave bits |
| `exact_harmony` | 108 | 12 pitch classes × 9 (1 class bit + 8 octave bits per class) |

### Data Conversion (`src/data_conversion/`)

Each converter exposes `midi_to_ai_format()` and `ai_format_to_midi()`. During conversion, MIDI files are transposed to C major or A minor and quantized to 4 subdivisions per quarter note. Output is CSV-like text with binary vectors (one line per timestep).

### LSTM Model

All three training scripts share the same architecture:
- Input: sequences of 100 timesteps
- Layers: LSTM(128) → Dropout(0.2) → LSTM(64) → Dropout(0.2) → LSTM(32) → Dense(sigmoid)
- Loss: binary crossentropy
- Training uses a generator that streams from files with 80/20 file-level train/val split (batch size 32, 50 epochs)

### Prediction

Loads a trained model, takes an input sequence, and iteratively predicts the next timestep 200 times, thresholding at 0.5 to produce binary vectors.

## Key Dependencies

- **music21**: MIDI parsing, key detection, transposition
- **TensorFlow**: LSTM model training and inference
- **scikit-learn**: Train/validation splitting
