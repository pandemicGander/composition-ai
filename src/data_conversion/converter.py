from music21 import converter, note, stream, midi, chord
from itertools import zip_longest

from src.utils.helpers import does_element_exist, append_to_nth_element


def midi_to_custom_format(midi_file_path, harmonyValue=6):
  # Load the MIDI file
  midi_stream = converter.parse(midi_file_path)
  expectedOffset = 0
  futureNotesToMerge = []
  notes = []

  for midiData in midi_stream.flat.notesAndRests:

    if isinstance(midiData, chord.Chord):
      for n in midiData:
        # correct the offset - seems like a bug in music21
        n.offset = midiData.offset
        process(expectedOffset, futureNotesToMerge, n, notes)

    if isinstance(midiData, note.Note):
      process(expectedOffset, futureNotesToMerge, midiData, notes)

  merged_notes = [a + b for a, b in
                  zip_longest(futureNotesToMerge, notes, fillvalue=[])]
  sorted_data = [sorted(sublist, key=lambda x: x['pitch']) for sublist in
                 merged_notes]

  to_append_template = {'pitch': 0, 'velocity': 0}  # Template without offset

  result = []

  for idx, sublist in enumerate(sorted_data):
    # Check if the sublist is longer than the harmonyValue
    if len(sublist) > harmonyValue:
      # If so, truncate the sublist to harmonyValue length
      trimmed_sublist = sublist[:harmonyValue]
      result.append(trimmed_sublist)
    elif len(sublist) < harmonyValue:
      # If the sublist is shorter than the harmonyValue
      # Calculate how many items need to be appended
      append_count = harmonyValue - len(sublist)
      # Create the items to be appended
      items_to_append = [{'offset': idx, **to_append_template} for _ in
                         range(append_count)]
      # Append the items to the sublist
      extended_sublist = sublist + items_to_append
      result.append(extended_sublist)
    else:
      # If the sublist is exactly harmonyValue length, add it as is
      result.append(sublist)


  return result

def extractPitchesForAIFormat(data):
  return [[note['pitch'] for note in sublist] for sublist in data]

def process(expectedOffset, futureNotesToMerge, n, notes):
  while (getIndexFromOffset(n.offset) != expectedOffset):
    if (does_element_exist(notes, expectedOffset)):
      expectedOffset += 1
    else:
      append_to_nth_element(expectedOffset, notes, None)
      expectedOffset += 1
  for i in range(0, getIndexFromOffset(n.duration.quarterLength)):
    if (i > 0):
      append_to_nth_element(expectedOffset + i, futureNotesToMerge,
                            {"name": n.pitch.fullName, "pitch": n.pitch.midi,
                             "velocity": n.volume.velocity,
                             "offset:": expectedOffset + i})
    else:
      append_to_nth_element(expectedOffset + i, notes,
                            {"name": n.pitch.fullName, "pitch": n.pitch.midi,
                             "velocity": n.volume.velocity,
                             "offset:": expectedOffset + i})

def getIndexFromOffset(offset):
  return int(offset * 4)

from music21 import stream, note, midi, chord

def array_to_midi(pitch_arrays, instruments=6, output_midi_path='output_midi.mid'):
  # Create a new music21 stream
  s = stream.Stream()

  # Iterate over each array (each representing a 16th note)
  for i, pitches in enumerate(pitch_arrays):
    # Create a chord for the current beat with the non-zero pitches
    notes = [note.Note(p) for p in pitches if p > 0]

    # If there are no notes, create a rest
    if not notes:
      n = note.Rest()
    else:
      # If there's only one note, don't create a chord
      n = notes[0] if len(notes) == 1 else chord.Chord(notes)

    # Set the duration of the note or chord to a 16th note
    n.duration.type = '16th'

    # Append the note or chord to the stream at the correct offset
    s.insert(i * 0.25, n)  # 0.25 because each array represents a 16th note (there are 4 in a quarter note)

  # Write the stream to a MIDI file
  mf = midi.translate.streamToMidiFile(s)
  mf.open(output_midi_path, 'wb')
  mf.write()
  mf.close()

  return output_midi_path


def ai_to_midi_reconstructed():
  return None

# # Example usage with the provided input data
# pitch_arrays = [[50, 50, 50, 54, 57, 0], [50, 50, 50, 54, 57, 0], [50, 50, 54, 57, 57, 0], [50, 50, 54, 57, 57, 0], [50, 62, 0, 0, 0, 0], [49, 59, 0, 0, 0, 0], [47, 64, 0, 0, 0, 0], [48, 63, 0, 0, 0, 0], [45, 47, 45, 50, 56, 12], [46, 44, 47, 49, 53, 10], [47, 45, 50, 54, 55, 18], [48, 44, 51, 56, 53, 0], [48, 58, 0, 0, 0, 0], [47, 55, 0, 0, 0, 0], [46, 57, 0, 0, 0, 0], [48, 61, 0, 0, 0, 0], [48, 50, 51, 54, 61, 0], [49, 49, 51, 52, 60, 0], [50, 48, 57, 60, 64, 0], [51, 50, 56, 53, 51, 0], [49, 70, 0, 0, 0, 0], [53, 69, 0, 0, 0, 0], [52, 79, 0, 0, 22, 0], [56, 74, 0, 0, 0, 0], [52, 64, 41, 41, 67, 0], [48, 51, 38, 37, 49, 0], [49, 52, 36, 42, 43, 0], [46, 73, 0, 0, 0, 0], [45, 73, 0, 0, 10, 14], [53, 72, 0, 18, 15, 0], [53, 75, 0, 12, 11, 0], [54, 69, 31, 32, 62, 0], [46, 51, 28, 28, 38, 0], [45, 88, 0, 0, 0, 0], [43, 85, 0, 0, 0, 15], [41, 81, 0, 0, 0, 0], [49, 89, 0, 0, 26, 0], [54, 100, 0, 0, 0, 0], [45, 74, 0, 0, 0, 43], [33, 71, 0, 0, 0, 0], [31, 63, 0, 0, 0, 0], [19, 106, 0, 0, 0, 0], [34, 54, 0, 0, 0, 0], [30, 30, 0, 24, 0, 0], [25, 31, 11, 50, 93, 26], [35, 37, 0, 22, 86, 0], [25, 20, 0, 17, 30, 12], [31, 21, 20, 65, 63, 12], [27, 37, 20, 25, 12, 0], [22, 41, 32, 45, 37, 24], [25, 38, 23, 45, 0, 11], [22, 33, 27, 39, 27, 25], [21, 34, 36, 59, 0, 0], [27, 41, 34, 51, 40, 12], [26, 45, 40, 49, 10, 0], [28, 49, 45, 55, 49, 29], [30, 51, 52, 58, 24, 13], [35, 51, 52, 57, 41, 23], [37, 56, 55, 62, 17, 19], [43, 54, 50, 56, 36, 26], [45, 58, 55, 59, 13, 20], [48, 61, 54, 56, 21, 20], [51, 64, 57, 61, 10, 17], [54, 68, 61, 66, 32, 0], [57, 68, 63, 72, 29, 15], [64, 69, 63, 80, 67, 18], [68, 73, 70, 87, 69, 10], [69, 78, 77, 96, 85, 0], [69, 80, 68, 88, 85, 0], [64, 77, 63, 76, 81, 0], [60, 74, 53, 67, 52, 21], [58, 64, 42, 70, 59, 50], [59, 58, 56, 76, 48, 58], [57, 56, 61, 76, 41, 56], [59, 59, 63, 74, 38, 58], [59, 70, 74, 76, 53, 53], [58, 72, 76, 79, 57, 53], [58, 73, 78, 83, 65, 53], [56, 71, 74, 89, 73, 49], [53, 55, 52, 88, 70, 41], [53, 55, 53, 88, 70, 38], [54, 58, 62, 87, 64, 25], [56, 68, 71, 87, 63, 23], [60, 78, 79, 89, 58, 19], [62, 82, 83, 86, 52, 45], [62, 83, 89, 89, 54, 59], [61, 76, 84, 90, 57, 72], [60, 73, 81, 90, 64, 81], [59, 71, 77, 87, 70, 81], [57, 66, 64, 81, 69, 72], [58, 65, 63, 81, 68, 69], [56, 57, 58, 75, 65, 72], [56, 58, 61, 74, 65, 66], [56, 63, 67, 78, 62, 50], [57, 65, 71, 82, 56, 42], [58, 70, 75, 88, 53, 40], [57, 69, 74, 91, 48, 42], [56, 67, 71, 91, 47, 52], [57, 70, 75, 90, 51, 65], [58, 69, 76, 90, 59, 73], [60, 72, 78, 89, 67, 69], [60, 71, 73, 88, 69, 70], [58, 63, 61, 85, 68, 73], [56, 58, 55, 80, 68, 71], [54, 56, 59, 79, 66, 67]]
#
#
# output_midi_path = 'output_midi3.mid'
#
# # Convert the arrays to a MIDI file
# array_to_midi(pitch_arrays, instruments=6, output_midi_path=output_midi_path)
#
#
#
# # Usage
# midi_file_path = 'tester2.mid'
# formatted_data = midi_to_custom_format(midi_file_path)
# print(extractPitchesForAIFormat(formatted_data))
