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
