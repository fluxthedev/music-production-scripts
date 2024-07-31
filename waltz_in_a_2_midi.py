from midiutil import MIDIFile

# Set up MIDI file parameters
tempo = 88  # typical waltz tempo
time_signature = (3, 4)  # 3/4 time signature

# Create a new MIDI file for each track
melody_midi_file = MIDIFile(1)  # 1 track
harmony_midi_file = MIDIFile(1)  # 1 track
bass_midi_file = MIDIFile(1)  # 1 track

# Set tempo and time signature for each track
melody_midi_file.addTempo(0, 0, tempo)
melody_midi_file.addTimeSignature(0, 0, time_signature[0], time_signature[1], 24)

harmony_midi_file.addTempo(0, 0, tempo)
harmony_midi_file.addTimeSignature(0, 0, time_signature[0], time_signature[1], 24)

bass_midi_file.addTempo(0, 0, tempo)
bass_midi_file.addTimeSignature(0, 0, time_signature[0], time_signature[1], 24)

# Melody track
melody_track = 0
melody_channel = 0

# Harmony track
harmony_track = 0
harmony_channel = 0

# Bass track
bass_track = 0
bass_channel = 0

# Add melody notes
melody_notes = [
    # Bar 1-4: [Introduction, no melody]
    # Bar 5
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    {'pitch': 62, 'duration': 1},  # D (quarter)
    {'pitch': 64, 'duration': 1},  # E (quarter)
    # Bar 6
    {'pitch': 66, 'duration': 2},  # F# (half)
    {'pitch': 64, 'duration': 1},  # E (quarter)
    # Bar 7
    {'pitch': 62, 'duration': 2},  # D (half)
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    # Bar 8
    {'pitch': 59, 'duration': 4},  # B (whole note tied to next bar)
    # Bar 9
    {'pitch': 59, 'duration': 0},  # B (continued from previous bar)
    # Bar 10-11: [Similar pattern to bars 5-6]
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    {'pitch': 62, 'duration': 1},  # D (quarter)
    {'pitch': 64, 'duration': 1},  # E (quarter)
    {'pitch': 66, 'duration': 2},  # F# (half)
    {'pitch': 64, 'duration': 1},  # E (quarter)
    # Bar 12-13: [Similar pattern to bars 7-8]
    {'pitch': 62, 'duration': 2},  # D (half)
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    {'pitch': 59, 'duration': 4},  # B (whole note tied to next bar)
    {'pitch': 59, 'duration': 0},  # B (continued from previous bar)
    # Bar 14-15: Repeated notes pattern (exact pitches unclear from image)
    # Assuming a repeated pattern of C#-D-E
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    {'pitch': 62, 'duration': 1},  # D (quarter)
    {'pitch': 64, 'duration': 1},  # E (quarter)
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    {'pitch': 62, 'duration': 1},  # D (quarter)
    {'pitch': 64, 'duration': 1},  # E (quarter)
    # Bar 16-19: [Ending section, melody not clearly visible]
    # Assuming a simple ending pattern of B-C#-D-E
    {'pitch': 59, 'duration': 1},  # B (quarter)
    {'pitch': 60, 'duration': 1},  # C# (quarter)
    {'pitch': 62, 'duration': 1},  # D (quarter)
    {'pitch': 64, 'duration': 1},  # E (quarter)
]

for i, note in enumerate(melody_notes):
    melody_midi_file.addNote(melody_track, melody_channel, note['pitch'], i, note['duration'], 100)

# Add harmony (chord progression)
harmony_chords = [
    # Bar 1
    {'root': 54, 'quality': '7'},  # F#7
    # Bar 2
    {'root': 52, 'quality': '7'},  # E7
    # Bar 3
    {'root': 59, 'quality': 'maj'},  # B F#7
    # Bar 4
    {'root': 59, 'quality': 'maj'},  # B
    # ... add more harmony chords here ...
]

for i, chord in enumerate(harmony_chords):
    if chord['quality'] == '7':
        harmony_midi_file.addNote(harmony_track, harmony_channel, chord['root'], i, 1, 100)
        harmony_midi_file.addNote(harmony_track, harmony_channel, chord['root'] + 4, i, 1, 100)
        harmony_midi_file.addNote(harmony_track, harmony_channel, chord['root'] + 7, i, 1, 100)
    elif chord['quality'] == 'maj':
        harmony_midi_file.addNote(harmony_track, harmony_channel, chord['root'], i, 1, 100)
        harmony_midi_file.addNote(harmony_track, harmony_channel, chord['root'] + 4, i, 1, 100)
        harmony_midi_file.addNote(harmony_track, harmony_channel, chord['root'] + 7, i, 1, 100)

# Add bass line
bass_notes = [
    # Bar 1
    {'pitch': 36, 'duration': 1},  # F# (quarter)
    # Bar 2
    {'pitch': 34, 'duration': 1},  # E (quarter)
    # Bar 3
    {'pitch': 41, 'duration': 1},  # B (quarter)
    # Bar 4
    {'pitch': 41, 'duration': 1},  # B (quarter)
    # ... add more bass notes here ...
]

for i, note in enumerate(bass_notes):
    bass_midi_file.addNote(bass_track, bass_channel, note['pitch'], i, note['duration'], 100)

# Save MIDI files
with open('melody.mid', 'wb') as output_file:
    melody_midi_file.writeFile(output_file)

with open('harmony.mid', 'wb') as output_file:
    harmony_midi_file.writeFile(output_file)

with open('bass.mid', 'wb') as output_file:
    bass_midi_file.writeFile(output_file)