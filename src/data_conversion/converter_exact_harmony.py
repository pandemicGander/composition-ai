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

  # Iterate over all notes and rests in the MIDI file
  for midiData in transposed_stream.flat.notesAndRests:
    # Calculate the beats this note/chord/rest spans
    beat_start = int(midiData.offset * 4)  # 4 subdivisions per quarter
    beat_end = max(beat_start + 1, math.ceil((midiData.offset + midiData.duration.quarterLength) * 4))

    if beat_end > max_beat:
      max_beat = beat_end

    for beat in range(beat_start, beat_end):
      if beat not in result:
        # 12 bits for pitch classes, 96 bits for octaves = 108 total
        result[beat] = [0] * 108

      # Handle chords
      if isinstance(midiData, chord.Chord):
        for n in midiData.notes:
          pc = n.pitch.pitchClass  # 0–11
          octave = n.pitch.octave  # e.g., 4
          if octave is not None and 1 <= octave <= 8:
            # First set the pitch-class bit
            result[beat][pc] = 1
            # Then set the octave bit for this pitch class
            octave_index = 12 + pc * 8 + (octave - 1)
            result[beat][octave_index] = 1

      # Handle single notes
      elif isinstance(midiData, note.Note):
        pc = midiData.pitch.pitchClass
        octave = midiData.pitch.octave
        if octave is not None and 1 <= octave <= 8:
          # First set the pitch-class bit
          result[beat][pc] = 1
          # Then set the octave bit for this pitch class
          octave_index = 12 + pc * 8 + (octave - 1)
          result[beat][octave_index] = 1

  # Fill in any gaps (rests) with zero vectors
  for beat in range(max_beat):
    if beat not in result:
      result[beat] = [0] * 108

  # Create a list of time steps sorted by beat
  sequences = [result[beat] for beat in sorted(result.keys())]

  return sequences

def ai_format_to_midi(data, output_midi_path):
  # Create a new music21 stream
  s = stream.Stream()

  ks = key.KeySignature(0)  # 0 sharps/flats
  s.insert(0, ks)

  # Each time step is 108 bits:
  #  - first 12 bits = pitch classes
  #  - next 96 bits = 12 groups of 8 bits (one group per pitch class)
  for timestep in data:
    pitches = []

    # Check which pitch classes are active in the first 12 bits
    active_pcs = [pc for pc in range(12) if timestep[pc] == 1]

    # For each active pitch class, see which octaves are active
    for pc in active_pcs:
      octave_section_start = 12 + pc * 8
      octave_section_end = octave_section_start + 8  # 8 bits for octaves 1–8
      # Which octaves are active in [octave_section_start, octave_section_end)
      active_octaves = [
        (i - octave_section_start + 1)
        for i in range(octave_section_start, octave_section_end)
        if timestep[i] == 1
      ]
      # Build the pitches for each active octave
      for octv in active_octaves:
        p = pitch.Pitch()
        p.pitchClass = pc     # 0–11
        p.octave = octv       # 1–8
        pitches.append(p)

    # Now decide if it's a rest, single note, or chord
    if not pitches:
      # Rest
      r = note.Rest()
      r.duration.quarterLength = 0.25
      s.append(r)
    elif len(pitches) == 1:
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

  # Save as MIDI
  s.write('midi', fp=output_midi_path)
  print("MIDI file saved to:", output_midi_path)
