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
        result[beat] = [0] * 20  # Initialize vector for 12 pitch classes + 8 octaves

      # Handle chords
      if isinstance(midiData, chord.Chord):
        for n in midiData.notes:
          pc = n.pitch.pitchClass        # Pitch class (0-11)
          octave = n.pitch.octave        # Octave (integer)
          if octave is not None and 1 <= octave <= 8:
            result[beat][pc] = 1       # Set pitch class
            result[beat][12 + (octave - 1)] = 1  # Set octave
      # Handle single notes
      elif isinstance(midiData, note.Note):
        pc = midiData.pitch.pitchClass
        octave = midiData.pitch.octave
        if octave is not None and 1 <= octave <= 8:
          result[beat][pc] = 1
          result[beat][12 + (octave - 1)] = 1
      # Handle rests (no action needed for rests in this representation)

  # Create a list of time steps sorted by beat
  sequences = [result[beat] for beat in sorted(result.keys())]

  return sequences

def ai_format_to_midi(data, output_midi_path):
  # Create a new music21 stream
  s = stream.Stream()

  # Iterate through each time step in the data
  for timestep in data:
    pitches = []
    pitch_classes = [i for i, val in enumerate(timestep[:12]) if val == 1]
    octaves = [i + 1 for i, val in enumerate(timestep[12:]) if val == 1]  # Octaves 1-8

    if pitch_classes and octaves:
      for pc in pitch_classes:
        for octave in octaves:
          p = pitch.Pitch()
          p.pitchClass = pc
          p.octave = octave
          pitches.append(p)

      if len(pitches) == 1:
        # Single note
        n = note.Note()
        n.pitch = pitches[0]
        n.duration.quarterLength = 0.25
        s.append(n)
      else:
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
