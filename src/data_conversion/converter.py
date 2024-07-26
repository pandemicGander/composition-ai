from music21 import stream, pitch, midi, converter, note, chord
import json

def midi_to_ai_format(midi_file_path):
  # Load the MIDI file
  midi_stream = converter.parse(midi_file_path)

  # Dictionary to store results
  result = {}

  # Iterate over all notes and chords in the MIDI file
  for midiData in midi_stream.flat.notesAndRests:
    # Calculate the beats this note or chord should cover
    beat_start = int(midiData.offset * 4)  # Assuming we want 4 beats per quarter note
    beat_end = int((midiData.offset + midiData.duration.quarterLength) * 4)

    # Handle chords
    if isinstance(midiData, chord.Chord):
      notes_list = [n.pitch.pitchClass for n in midiData.notes]
      for beat in range(beat_start, beat_end):
        if beat in result:
          result[beat].extend(notes_list)  # Append new notes to existing beat
        else:
          result[beat] = notes_list.copy()  # Initialize beat

    # Handle single notes
    elif isinstance(midiData, note.Note):
      note_dict = midiData.pitch.pitchClass
      for beat in range(beat_start, beat_end):
        if beat in result:
          result[beat].append(note_dict)  # Append the note to existing beat
        else:
          result[beat] = [note_dict]  # Initialize beat


  return prepare_sequences(result)


def ai_format_to_midi(data, output_midi_path):
  # Create a new music21 stream
  s = stream.Stream()

  # Iterate through each sequence in the data
  for sequence in data:
    unique_notes = set(sequence)
    if len(unique_notes) == 1:
      # If all elements are the same, create a single note extended over the whole sequence
      n = note.Note()
      n.pitch = pitch.Pitch(pitchClass=sequence[0])
      n.duration.quarterLength = 0.25  # Multiply duration by number of beats in the sequence
      s.append(n)
    else:
      # Create a chord for sequences with multiple unique notes
      pitches = [pitch.Pitch(pitchClass=pc) for pc in sequence]
      c = chord.Chord(pitches)
      c.duration.quarterLength = 0.25  # Set duration for the whole sequence
      s.append(c)

  # Save the stream as a MIDI file
  mf = midi.translate.streamToMidiFile(s)
  mf.open(output_midi_path, 'wb')
  mf.write()
  mf.close()
  print("MIDI file saved to:", output_midi_path)

# Function to process and prepare sequences
def prepare_sequences(data, seq_length=8):
  sequences = []
  for key in data.items():
    # Extract pitch classes
    sequence = list(set(key[1]))

    if len(sequence) > seq_length:
      # Truncate sequence if longer than seq_length
      sequence = sequence[:seq_length]
    elif len(sequence) < seq_length:
      # Extend sequence by repeating and slicing to seq_length
      repeat_times = (seq_length // len(sequence)) + 1  # Compute required repetitions
      sequence = (sequence * repeat_times)[:seq_length]

    sequences.append(sequence)  # Append prepared sequence

  sorted_list = [sorted(sublist) for sublist in sequences]
  return sorted_list
