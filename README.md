# Music Generation Scripts

This repository contains various scripts for music generation and manipulation.

## AI Chord Progression Generator (`chord_progression_generator.py`)

### Description

The `chord_progression_generator.py` script generates musical chord progressions based on user preferences for mood, key, and genre. It utilizes the OpenAI API to get chord suggestions and then creates a MIDI file for the generated progression.

### Setup Instructions

1.  **Install Dependencies:**
    Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
    Ensure that `requirements.txt` is present and includes `openai` and `midiutil`.

2.  **API Key:**
    You will need an OpenAI API key to use this script. The script will prompt you to enter your API key directly when you run it. If you leave the prompt blank, the script will use placeholder data for testing, and will not make a real call to the OpenAI API.

### How to Run

1.  Run the script from your terminal:
    ```bash
    python chord_progression_generator.py
    ```
2.  The script will then prompt you to enter:
    *   The desired mood (e.g., happy, melancholic).
    *   The desired musical key (e.g., C Major, A minor).
    *   The desired genre (e.g., Pop, Jazz, Cinematic).
    *   Your OpenAI API Key.
    *   The desired output filename for the MIDI file (e.g., `my_progression.mid`).

### Output

The script will generate a MIDI file (e.g., `chord_progression.mid`, or your custom filename) in the same directory. This MIDI file contains the AI-suggested chord progression, where each chord is played as a simple triad for a fixed duration. If there were issues parsing any specific chords suggested by the AI, those chords might be skipped in the final MIDI output.

---

*More scripts and documentation may be added here in the future.*
