from music21 import converter, note, stream, midi, chord
from itertools import zip_longest


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


def does_element_exist(lst, index):
  return index < len(lst)


def append_to_nth_element(n, notes, value):
  if value is None:
    notes.append([])
    return
  # Ensure that there are enough elements in notes
  while len(notes) <= n:
    notes.append([])  # Append an empty list if the index does not exist

  # Now that we're sure notes[n] exists, append the value to it
  notes[n].append(value)


def getIndexFromOffset(offset):
  return int(offset * 4)


# Usage
midi_file_path = 'simple_midi.mid'
formatted_data = midi_to_custom_format(midi_file_path)
print(extractPitchesForAIFormat(formatted_data))
