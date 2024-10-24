from music21 import stream, pitch, midi, converter, note, chord

def midi_to_ai_format(midi_file_path):
  # Load the MIDI file
  midi_stream = converter.parse(midi_file_path)

  # Dictionary to store results
  result = {}

  # Iterate over all notes and chords in the MIDI file
  for midiData in midi_stream.flat.notesAndRests:
    # Calculate the beats this note or chord should cover
    beat_start = int(midiData.offset * 4)  # Assuming 4 beats per quarter note
    beat_end = int((midiData.offset + midiData.duration.quarterLength) * 4)

    for beat in range(beat_start, beat_end):
      if beat not in result:
        result[beat] = [0] * 12  # Initialize vector for 12 pitch classes

      # Handle chords
      if isinstance(midiData, chord.Chord):
        for n in midiData.notes:
          pc = n.pitch.pitchClass
          result[beat][pc] = 1  # Set the pitch class to 1

      # Handle single notes
      elif isinstance(midiData, note.Note):
        pc = midiData.pitch.pitchClass
        result[beat][pc] = 1  # Set the pitch class to 1

  # Create a list of time steps sorted by beat
  sequences = [result[beat] for beat in sorted(result.keys())]

  return sequences

def ai_format_to_midi(data, output_midi_path):
  # Create a new music21 stream
  s = stream.Stream()

  # Iterate through each time step in the data
  for timestep in data:
    pitches = []
    for pc, is_present in enumerate(timestep):
      if is_present:
        pitches.append(pitch.Pitch(pitchClass=pc))

    if len(pitches) == 1:
      # Single note
      n = note.Note()
      n.pitch = pitches[0]
      n.duration.quarterLength = 0.25
      s.append(n)
    elif len(pitches) > 1:
      # Chord
      c = chord.Chord(pitches)
      c.duration.quarterLength = 0.25
      s.append(c)
    else:
      # Rest
      r = note.Rest()
      r.duration.quarterLength = 0.25
      s.append(r)

  # Save the stream as a MIDI file
  s.write('midi', fp=output_midi_path)
  print("MIDI file saved to:", output_midi_path)
