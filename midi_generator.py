from music21 import stream, note, chord, midi

# Create a simple MIDI stream
simple_midi = stream.Stream()

# Add the first note 'C4'
simple_midi.append(note.Note('C4', quarterLength=1))

# Create and add a chord to play on the second quaver
chord_notes = ['E4', 'G4']  # Notes to be played together
chord_duration = 1  # Duration of the chord in quarter notes
chord_to_play = chord.Chord(chord_notes, quarterLength=chord_duration)
chord_to_play.offset = 0.5  # Start half a beat after the first note
simple_midi.append(chord_to_play)

# Add a rest before the last chord
rest = note.Rest(quarterLength=1)
simple_midi.append(rest)

# Create and add the last chord with three notes
last_chord_notes = ['C5', 'E5', 'G5']  # Define the notes for the last chord
last_chord_duration = 1  # Duration of the last chord in quarter notes
last_chord = chord.Chord(last_chord_notes, quarterLength=last_chord_duration)
last_chord.offset = 2.5  # Start time after the rest
simple_midi.append(last_chord)

# Write to a MIDI file
simple_midi.write('midi', fp='generated.mid')
