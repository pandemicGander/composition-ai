# MIDI to Custom Format Conversion Script

## Overview

This Python script is designed to convert MIDI files into a specific time series data format. The primary purpose of this conversion is to prepare the data for feeding into an LSTM (Long Short-Term Memory) AI model for music composition prediction. The script uses the `music21` library to parse MIDI files and transforms the musical information into a structured format that represents each note and chord along with their attributes such as pitch, velocity, and offset.

## Features

- **MIDI Parsing**: Reads MIDI files and extracts musical elements (notes and chords).
- **Custom Data Structuring**: Converts musical elements into a time series data structure.
- **Harmony Normalization**: Ensures each time step in the series has a consistent number of elements, defined by `harmonyValue`.
- **Time Series Output**: The output is a list of time steps, each containing a list of note dictionaries.

## Usage

### Installation

Ensure you have `music21` installed in your Python environment.

```bash
pip install music21
```

### Running the Script

The main function `midi_to_custom_format` takes a MIDI file path and an optional `harmonyValue` (default is 6) as inputs.

```python
midi_file_path = 'path_to_your_midi_file.mid'
formatted_data = midi_to_custom_format(midi_file_path, harmonyValue=6)
print(formatted_data)
```

## Functionality

- `midi_to_custom_format`: Main function to convert MIDI to custom format.
  - **Parameters**:
    - `midi_file_path` (str): Path to the MIDI file.
    - `harmonyValue` (int, optional): Maximum number of elements per time step.
  - **Returns**: A list of time steps, each a list of note/chord elements.
- `process`: Helper function to process each note/chord.
- `does_element_exist`: Checks if an element exists at a specific index in a list.
- `append_to_nth_element`: Appends a value to the nth element of a list.
- `getIndexFromOffset`: Converts an offset value to an index.

## Example Output

The output is a list of time steps (indexed), where each time step is a list of dictionaries representing notes. Each dictionary contains keys such as 'name', 'pitch', 'velocity', and 'offset'. For example:

```python
00 = [{'name': 'C4', 'offset': 0, 'pitch': 60, 'velocity': 80}, ...]
01 = [{'name': 'C4', 'offset': 1, 'pitch': 60, 'velocity': 80}, ...]
...
```

Each time step has a consistent number of elements, determined by `harmonyValue`.

## Note

This script is specifically designed for preparing MIDI data for LSTM-based music composition models. The format may need adjustments based on the specific requirements of your AI model.