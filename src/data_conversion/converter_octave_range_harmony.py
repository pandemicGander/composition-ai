import math
from music21 import stream, pitch, key, converter, note, chord, interval

def midi_to_ai_format(midi_file_path):
  # Load the MIDI file
  midi_stream = converter.parse(midi_file_path)

  # Analyze the key of the MIDI file
  key_signature = midi_stream.analyze('key')
  print(f"Original Key: {key_signature.tonic.name} {key_signature.mode}")

  # Determine the interval needed to transpose to C major or A minor
  if key_signature.mode == 'major':
    target = pitch.Pitch('C')
  elif key_signature.mode == 'minor':
    target = pitch.Pitch('A')
  else:
    target = pitch.Pitch('C')

  # Compute semitone difference and normalize to ascending (0..11)
  semitones = (target.pitchClass - key_signature.tonic.pitchClass) % 12
  transposition_interval = interval.Interval(semitones)

  # Transpose the MIDI stream to C major or A minor
  transposed_stream = midi_stream.transpose(transposition_interval)
  print(f"Transposed by interval: {transposition_interval}")

  # Dictionary to store results
  result = {}

  # Find the total number of beats to fill gaps from rests
  max_beat = 0

  # Iterate over all notes and chords in the MIDI file
  for midiData in transposed_stream.flat.notesAndRests:
    # Calculate the beats this note or chord should cover
    beat_start = int(midiData.offset * 4)  # 4 subdivisions per quarter note
    beat_end = max(beat_start + 1, math.ceil((midiData.offset + midiData.duration.quarterLength) * 4))

    if beat_end > max_beat:
      max_beat = beat_end

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

  # Fill in any gaps (rests) with zero vectors
  for beat in range(max_beat):
    if beat not in result:
      result[beat] = [0] * 20

  # Create a list of time steps sorted by beat
  sequences = [result[beat] for beat in sorted(result.keys())]

  return sequences

def ai_format_to_midi(data, output_midi_path):
  # Create a new music21 stream
  s = stream.Stream()

  ks = key.KeySignature(0)  # 0 sharps/flats
  s.insert(0, ks)

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
