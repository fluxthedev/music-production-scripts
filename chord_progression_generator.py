"""
Chord Progression Generator.

This script generates musical chord progressions based on user preferences
for mood, key, and genre. It utilizes the OpenAI API to get chord suggestions
and then creates a MIDI file for the generated progression using the `midiutil`
library.

Features:
- Prompts the user for musical preferences (mood, key, genre).
- Queries the OpenAI GPT-3.5-turbo model for chord progression suggestions.
- Parses the AI's response to extract a list of chords.
- Converts chord names (e.g., "Am", "C#maj7", "G/B") into MIDI notes.
- Generates a MIDI file (.mid) representing the chord progression.
- Includes error handling for API calls, response parsing, and MIDI creation.
- Allows using a placeholder API key for testing without actual OpenAI calls,
  in which case it uses sample chord data.

Dependencies:
- openai: For interacting with the OpenAI API.
- midiutil: For creating MIDI files.
  (These should be installed via pip: `pip install openai midiutil`)
"""
import openai
import ast
import re # For chord parsing
from midiutil.MidiFile import MIDIFile # For MIDI creation

# Attempt to import specific OpenAI error types for more granular error handling.
# If these specific error classes are not found (e.g., in an older version of the
# openai library), define dummy classes to prevent `except` blocks from crashing.
try:
    from openai import APIConnectionError, AuthenticationError, RateLimitError, APIError
except ImportError:
    # Define dummy exception classes if specific ones are not available.
    # This ensures that the `except` blocks referencing these names still function.
    class APIConnectionError(Exception): pass
    class AuthenticationError(Exception): pass
    class RateLimitError(Exception): pass
    class APIError(Exception): pass


def get_user_preferences() -> dict[str, str]:
    """
    Prompts the user to input their desired mood, key, and genre for the
    chord progression.

    The function will loop for each preference until a non-empty string is provided.

    Returns:
        dict[str, str]: A dictionary containing the user's preferences,
                        with keys 'mood', 'key', and 'genre'.
    """
    print("[INFO] Getting user preferences...")
    preferences = {} # Initialize an empty dictionary to store preferences.

    # Loop until a valid mood is entered.
    while True:
        mood = input("Enter the desired mood (e.g., happy, melancholic, energetic): ").strip()
        if mood: # Check if the input is not empty.
            preferences['mood'] = mood
            break
        else:
            print("[WARNING] Mood input cannot be empty. Please enter a mood.")

    # Loop until a valid key is entered.
    while True:
        key = input("Enter the desired key (e.g., C Major, A minor, G# Dorian): ").strip()
        if key: # Check if the input is not empty.
            preferences['key'] = key
            break
        else:
            print("[WARNING] Key input cannot be empty. Please enter a key.")

    # Loop until a valid genre is entered.
    while True:
        genre = input("Enter the desired genre (e.g., Pop, Jazz, Cinematic, Lo-fi): ").strip()
        if genre: # Check if the input is not empty.
            preferences['genre'] = genre
            break
        else:
            print("[WARNING] Genre input cannot be empty. Please enter a genre.")
    
    return preferences

def get_chord_suggestions(mood: str, key: str, genre: str, api_key: str) -> str:
    """
    Generates chord progression suggestions by calling the OpenAI API.

    If a placeholder API key ("YOUR_OPENAI_API_KEY") or an empty key is provided,
    it returns a sample chord progression string for testing purposes. Otherwise,
    it constructs a detailed prompt and queries the `gpt-3.5-turbo` model.

    Args:
        mood (str): The desired mood for the chord progression.
        key (str): The desired musical key.
        genre (str): The desired musical genre.
        api_key (str): The user's OpenAI API key.

    Returns:
        str: The raw string response from the LLM, which is expected to be a
             Python list of chord strings (e.g., "['C', 'G', 'Am', 'F']").
             Returns an error message string starting with "[ERROR]" or a
             sample string if using a placeholder key.
    
    Handled Exceptions:
        Catches and returns string error messages for:
        - `openai.AuthenticationError`: If API key is invalid.
        - `openai.APIConnectionError`: If connection to OpenAI fails.
        - `openai.RateLimitError`: If API rate limit is exceeded.
        - `openai.APIError`: For other OpenAI specific API errors.
        - `Exception`: For any other unexpected errors during the API call.
    """
    print("[INFO] Contacting AI for chord suggestions...")

    # Handle placeholder or empty API key for testing or if user doesn't provide one.
    if api_key == "YOUR_OPENAI_API_KEY" or not api_key:
        print("[WARNING] Using a placeholder or empty API key.")
        print("[INFO] To get actual suggestions, please provide a valid OpenAI API key when prompted.")
        # Return a sample response to allow testing of parsing and MIDI generation.
        return "['Cmaj', 'Gmaj', 'Amin', 'Fmaj']" # Sample chord progression

    try:
        # Initialize the OpenAI client with the provided API key.
        client = openai.OpenAI(api_key=api_key)

        # Construct the prompt for the LLM.
        # The prompt is designed to be specific about the desired output format (a Python list of strings)
        # and the musical context (mood, key, genre).
        prompt = (
            f"Generate a chord progression with 4 or 8 chords for a '{genre}' track "
            f"in '{key}' with a '{mood}' mood. "
            "The output should be ONLY a Python list of strings, where each string is a chord name. "
            "For example: ['C', 'G/B', 'Am', 'Fmaj7'] or ['Cmaj7', 'F#m7b5', 'A7sus4', 'Dm9']. "
            "Do not include any introductory text or explanations, just the list itself."
        )
        
        # Make the API call to OpenAI's chat completions endpoint.
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # Specify the model to use.
            messages=[
                # System message sets the context for the AI assistant.
                {"role": "system", "content": "You are a helpful music assistant. Respond ONLY with a Python list of chord strings."},
                # User message provides the specific request (the prompt).
                {"role": "user", "content": prompt}
            ]
        )
        # Extract and return the content of the AI's response.
        return completion.choices[0].message.content
    except AuthenticationError:
        return "[ERROR] OpenAI API Authentication Failed: Please check your API key. Ensure it is correct and has not expired."
    except APIConnectionError:
        return "[ERROR] OpenAI API Connection Error: Could not connect to OpenAI. Please check your internet connection."
    except RateLimitError:
        return "[ERROR] OpenAI API Rate Limit Exceeded: You have exceeded your current quota. Please check your OpenAI plan and billing details."
    except APIError as e: # Catch other OpenAI specific errors.
        return f"[ERROR] OpenAI API Error: {e}"
    except Exception as e: # Catch any other non-OpenAI errors during the API call.
        return f"[ERROR] An unexpected error occurred while trying to contact OpenAI API: {e}"

def parse_llm_response(response_text: str) -> list[str]:
    """
    Parses the LLM's string response to safely extract a list of chord strings.

    The function expects the response to contain a string representation of a
    Python list (e.g., "['C', 'G', 'Am', 'F']"). It uses regular expressions
    to find the list structure and `ast.literal_eval()` for safe parsing.

    Args:
        response_text (str): The raw string response from the LLM.

    Returns:
        list[str]: A list of chord strings if parsing is successful.
                   Returns an empty list if parsing fails, if the response
                   is an error message, or if the response is empty.
    
    Handled Scenarios:
        - Empty or whitespace-only `response_text`.
        - `response_text` that is an error message (starts with "[ERROR]").
        - `response_text` that does not contain a recognizable list structure.
        - Parsed structure is not a list or contains non-string elements.
        - `ast.literal_eval()` raises `ValueError` or `SyntaxError`.
    """
    print("[INFO] Parsing AI response...")

    # Basic check for empty or invalid input.
    if not response_text or not response_text.strip():
        print("[ERROR] LLM response is empty. Cannot parse chords.")
        return []
        
    # If the response_text is already an error message from a previous step, propagate it.
    if response_text.startswith("[ERROR]"):
        print(response_text) # Print the specific error message.
        return []

    try:
        # Parsing strategy:
        # 1. Use regex to find a string that looks like a Python list of strings.
        #    This is more robust than simple find('\[') and rfind('\]') as it
        #    tries to match the content pattern of a list of strings.
        #    It looks for `[` followed by optional whitespace, then quoted strings,
        #    and finally `]`. `re.DOTALL` allows `.` to match newlines.
        list_match = re.search(r"\[\s*('|\").*?('|\")\s*\]", response_text, re.DOTALL)
        
        if not list_match:
            print(f"[ERROR] Could not find a valid list structure in the AI response: {response_text}")
            print("[INFO] The AI should return a list of chords like ['C', 'G', 'Am', 'F'].")
            return []
            
        list_str = list_match.group(0) # Extract the matched list string.
        
        # 2. Use ast.literal_eval for safe parsing of the string into a Python object.
        #    It only parses basic Python literals (strings, numbers, tuples, lists, dicts, booleans, None).
        parsed_response = ast.literal_eval(list_str)
        
        # 3. Validate the parsed structure.
        if not isinstance(parsed_response, list):
            print(f"[ERROR] AI response was parsed, but it's not a list: {parsed_response}")
            return []
        
        if not all(isinstance(item, str) for item in parsed_response):
            print(f"[ERROR] AI response is a list, but not all items are chord strings: {parsed_response}")
            return []
            
        if not parsed_response: # Check for an empty list.
            print("[WARNING] AI response was an empty list. No chords to process.")
            return [] # Return empty list, not an error, as it's valid but contains no data.

        print("[INFO] AI response parsed successfully.")
        return parsed_response
        
    except (ValueError, SyntaxError) as e:
        # These errors occur if ast.literal_eval fails to parse the string.
        print(f"[ERROR] Could not understand the chord progression format from the AI: {e}.")
        print(f"[DEBUG] Raw response was: {response_text}") # Show the problematic response for debugging.
        return []
    except Exception as e: # Catch any other unexpected errors during parsing.
        print(f"[ERROR] An unexpected error occurred during AI response parsing: {e}. Response was: {response_text}")
        return []

# Global constants for MIDI conversion.
# Maps note names to their base MIDI pitch value (relative to octave 0).
NOTE_TO_MIDI_BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
DEFAULT_OCTAVE = 4 # Default MIDI octave (C4 is middle C, MIDI note 60).

def chord_to_midi_pitches(chord_name: str) -> tuple[list[int] | None, str | None]:
    """
    Parses a chord name string (e.g., "Am", "C#", "Fmaj7", "Gbm3") and returns
    a list of MIDI pitch numbers for its triad (root, third, fifth).

    The function handles:
    - Root notes (A-G).
    - Accidentals (#, b, ♭, ♯).
    - Basic chord qualities (major, minor via "m" or "min"). Assumes major if unspecified.
    - Optional octave numbers (e.g., "C4", "Am3"). Defaults to DEFAULT_OCTAVE if not specified.
    - It currently ignores complex chord extensions (e.g., 7th, 9th, sus) and slash chords beyond the root.

    Args:
        chord_name (str): The chord name string to parse.

    Returns:
        tuple[list[int] | None, str | None]: A tuple containing:
            - A list of three MIDI pitch numbers (root, third, fifth) if parsing is successful.
            - `None` if the chord name cannot be parsed or results in invalid MIDI pitches.
            The second element is:
            - `None` if successful.
            - A string error message if parsing or validation fails.
    """
    if not chord_name:
        return None, "Chord name is empty."

    # Regex to parse chord names:
    # - Group 1 ([A-G]): Root note.
    # - Group 2 ([#b♭♯]*): Accidentals (zero or more sharps or flats).
    # - Group 3 (maj|min|m|M)?: Optional quality (major/minor). 'M' for major is also accepted.
    # - Group 4 (\d)?: Optional octave number.
    # - (?:/[A-G#b♭♯]*)?: Optional slash chord part (e.g., "/B"), currently ignored.
    match = re.match(
        r"([A-G])([#b♭♯]*)?(maj|min|m|M)?(\d)?(?:/[A-G#b♭♯]*)?", 
        chord_name.strip(), 
        re.IGNORECASE # Case-insensitive matching.
    )

    if not match:
        return None, f"Could not parse chord structure: '{chord_name}'"

    root_str, accidental_str, quality_str, octave_str = match.groups()
    
    # Determine base MIDI pitch from the root note string.
    base_pitch = NOTE_TO_MIDI_BASE.get(root_str.upper())
    if base_pitch is None: # Should not happen due to regex, but as a safeguard.
        return None, f"Invalid root note: '{root_str}' in '{chord_name}'"

    # Adjust base_pitch for accidentals.
    if accidental_str:
        for acc_char in accidental_str:
            if acc_char in ['#', '♯']: base_pitch += 1
            elif acc_char in ['b', '♭']: base_pitch -= 1
    base_pitch %= 12 # Normalize pitch (e.g., B# becomes C).

    # Determine the octave.
    octave = DEFAULT_OCTAVE
    if octave_str:
        try:
            octave = int(octave_str)
            # Validate octave range (0-9 is a common practical range for MIDI).
            if not (0 <= octave <= 9):
                return None, f"Octave '{octave_str}' out of typical range (0-9) for chord '{chord_name}'."
        except ValueError: # Should not happen if regex matches \d, but good for safety.
            return None, f"Invalid octave '{octave_str}' for chord '{chord_name}'."
    
    # Calculate the MIDI note number for the root.
    root_midi_note = base_pitch + (octave * 12)
    if not (0 <= root_midi_note <= 127): # Validate MIDI pitch range.
         return None, f"Root note MIDI value '{root_midi_note}' for chord '{chord_name}' is out of MIDI range (0-127)."

    # Determine chord quality (major or minor).
    # Assumes major if 'min' or 'm' is not present. 'maj' or 'M' explicitly means major.
    is_minor = quality_str and quality_str.lower() in ["min", "m"]
    
    # Construct the triad (root, third, fifth).
    pitches = [root_midi_note]
    pitches.append(root_midi_note + (3 if is_minor else 4)) # Minor third (root+3) or Major third (root+4).
    pitches.append(root_midi_note + 7) # Perfect fifth (root+7).
    
    # Validate that all generated pitches are within the MIDI range (0-127).
    valid_pitches = [p for p in pitches if 0 <= p <= 127]
    if len(valid_pitches) != 3: # Ensure all three notes of the triad are valid.
        return None, f"Generated pitches for '{chord_name}' (values: {pitches}) are out of MIDI range (0-127)."

    return valid_pitches, None # Return the list of pitches and no error message.

def create_midi_file(chord_progression: list[str], output_filename: str = "chord_progression.mid", tempo: int = 120):
    """
    Creates a MIDI file from a given chord progression.

    Each chord in the progression is converted to MIDI notes and added to a
    single MIDI track. Each chord is played as a block chord for a fixed duration.

    Args:
        chord_progression (list[str]): A list of chord name strings.
        output_filename (str, optional): The name of the MIDI file to create.
                                         Defaults to "chord_progression.mid".
        tempo (int, optional): The tempo of the MIDI file in beats per minute.
                               Defaults to 120.
    
    Side Effects:
        - Writes a MIDI file to the specified `output_filename`.
        - Prints status messages ([INFO], [WARNING], [ERROR]) to the console.
    
    Handled Exceptions:
        - `IOError`: If writing the MIDI file fails (e.g., due to permissions).
        - `Exception`: For other unexpected errors during MIDI file writing.
    """
    print("[INFO] Generating MIDI file...")
    if not chord_progression:
        print("[WARNING] Chord progression is empty. No MIDI file will be created.")
        return

    # Initialize MIDIFile object with one track.
    MyMIDI = MIDIFile(1)
    track = 0
    time = 0 # Start time for MIDI events.

    # Add track name and tempo. These are common metadata for MIDI files.
    MyMIDI.addTrackName(track, time, "Chord Progression")
    MyMIDI.addTempo(track, time, tempo)
    # Add a time signature (4/4 time, 24 MIDI clocks per quarter note).
    MyMIDI.addTimeSignature(track, time, 4, 2, 24) 

    current_time_in_beats = 0 # Keeps track of the current position in the MIDI sequence (in beats).
    chord_duration_in_beats = 4 # Each chord will last for 4 beats (e.g., a whole note in 4/4 time).
    skipped_chords_details = [] # To store names and reasons for any skipped chords.
    processed_chord_count = 0   # To count how many chords were successfully added.

    # Iterate through each chord in the progression.
    for i, chord_name in enumerate(chord_progression):
        # Convert chord name to MIDI pitches.
        midi_pitches, error_msg = chord_to_midi_pitches(chord_name)
        
        if midi_pitches:
            # If conversion is successful, add each note of the chord to the MIDI track.
            for pitch in midi_pitches:
                MyMIDI.addNote(track=track, 
                               channel=0, # MIDI channel (usually 0-15).
                               pitch=pitch, # MIDI note number (0-127).
                               time=current_time_in_beats, # Start time of the note in beats.
                               duration=chord_duration_in_beats, # Duration of the note in beats.
                               volume=100) # Velocity (loudness) of the note (0-127).
            current_time_in_beats += chord_duration_in_beats # Advance time for the next chord.
            processed_chord_count +=1
        else:
            # If chord conversion fails, record the skipped chord and reason.
            print(f"[WARNING] Skipping chord '{chord_name}': {error_msg}")
            skipped_chords_details.append(f"{chord_name} (Reason: {error_msg})")
    
    # Check if any valid chords were processed.
    if processed_chord_count == 0:
        print("[ERROR] No valid chords were processed. MIDI file will not be created.")
        if skipped_chords_details: # If there were issues with all chords.
            print("[INFO] Details of skipped chords:")
            for sc_detail in skipped_chords_details:
                print(f"  - {sc_detail}")
        return

    # Attempt to write the MIDI data to a file.
    try:
        with open(output_filename, "wb") as outfile: # Open in binary write mode.
            MyMIDI.writeFile(outfile)
        print(f"[INFO] MIDI file saved as '{output_filename}'.")
        # If some chords were skipped, list them now.
        if skipped_chords_details:
            print("[WARNING] Some chords were skipped during MIDI generation:")
            for sc_detail in skipped_chords_details:
                print(f"  - {sc_detail}")
    except IOError as e: # Handle file writing errors (e.g., permission denied).
        print(f"[ERROR] Could not write MIDI file to '{output_filename}'. Please check permissions or path: {e}")
    except Exception as e: # Handle other unexpected errors during file writing.
        print(f"[ERROR] An unexpected error occurred while writing MIDI file: {e}")


# Main execution block: This code runs when the script is executed directly.
if __name__ == "__main__":
    print("--- Chord Progression Generator ---")

    # 1. Get user preferences for the chord progression.
    user_preferences = get_user_preferences()
    
    # 2. Get OpenAI API Key from the user.
    print("\n[INFO] Preparing to get API Key...")
    api_key_input = input("Enter your OpenAI API Key (leave blank to use placeholder/sample data): ").strip()
    # The `get_chord_suggestions` function handles the logic for empty/placeholder keys.
    
    # 3. Request chord suggestions from OpenAI (or use sample data if key is placeholder/empty).
    suggestions_response = get_chord_suggestions(
        user_preferences['mood'],
        user_preferences['key'],
        user_preferences['genre'],
        api_key_input
    )

    # The raw LLM response is useful for debugging but can be noisy.
    # It's printed within parse_llm_response if DEBUG level logging is desired or if parsing fails.
    # print("\n[DEBUG] Raw LLM Response:") 
    # print(suggestions_response)

    # 4. Parse the LLM's response to extract chord names.
    parsed_chords = parse_llm_response(suggestions_response)

    # 5. If chords were successfully parsed, proceed to MIDI generation.
    if parsed_chords:
        print("\n[INFO] Parsed Chord Progression:")
        for i, chord in enumerate(parsed_chords):
            print(f"  Chord {i+1}: {chord}")
        
        # Get desired filename for the MIDI output.
        midi_filename_input = input("\nEnter the desired MIDI output filename (default: chord_progression.mid): ").strip()
        if not midi_filename_input: # Default if user enters nothing.
            midi_filename_input = "chord_progression.mid"
        
        # Create the MIDI file.
        create_midi_file(parsed_chords, midi_filename_input)
    else:
        # If parsing failed, an error message would have been printed by parse_llm_response.
        # Inform the user that MIDI generation is skipped.
        print("[INFO] MIDI generation skipped due to issues in previous steps (e.g., API error or parsing failure).")
    
    print("\n--- Chord progression generation complete. ---")
