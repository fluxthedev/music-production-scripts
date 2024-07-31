import librosa
import numpy as np
from openai import OpenAI
import json

# Initialize the OpenAI client
# client = OpenAI(api_key='')

def analyze_audio(file_path):
    """
    Analyze the audio file and return relevant metrics for compressor settings.
    """
    audio, sr = librosa.load(file_path)
    rms = np.sqrt(np.mean(audio**2))
    peak = np.max(np.abs(audio))
    dynamic_range = peak - rms
    stft = np.abs(librosa.stft(audio))
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(S=stft))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(S=stft))

    return {
        'rms': rms,
        'peak': peak,
        'dynamic_range': dynamic_range,
        'spectral_centroid': spectral_centroid,
        'spectral_rolloff': spectral_rolloff
    }

def recommend_compressor_settings(metrics):
    """
    Based on the audio metrics, recommend compressor settings using OpenAI's GPT-3.5-turbo.
    """
    prompt = f"""
    Based on the following audio metrics, recommend compressor settings:
    RMS: {metrics['rms']:.2f}
    Peak: {metrics['peak']:.2f}
    Dynamic Range: {metrics['dynamic_range']:.2f}
    Spectral Centroid: {metrics['spectral_centroid']:.2f} Hz
    Spectral Rolloff: {metrics['spectral_rolloff']:.2f} Hz

    Provide the settings in the following JSON format:
    {{
        "threshold": (float value in dB),
        "ratio": (float value),
        "attack": (float value in ms),
        "release": (float value in ms),
        "makeup_gain": (float value in dB)
    }}

    Also provide a brief explanation for these settings.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert audio engineer specializing in compression."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the JSON and explanation from the response
    ai_response = response.choices[0].message.content
    settings_json = ai_response.split('\n\n')[0]
    explanation = '\n'.join(ai_response.split('\n\n')[1:])

    try:
        settings = json.loads(settings_json)
    except json.JSONDecodeError:
        print("Error parsing JSON. Using fallback settings.")
        settings = {
            "threshold": -20,
            "ratio": 4,
            "attack": 10,
            "release": 100,
            "makeup_gain": 5
        }

    return settings, explanation

def main():
    file_path = 'stroll.wav'  # Use 'stroll.wav' as the default file
    metrics = analyze_audio(file_path)
    settings, explanation = recommend_compressor_settings(metrics)

    print("Audio Metrics:")
    print(f"RMS: {metrics['rms']:.2f}")
    print(f"Peak: {metrics['peak']:.2f}")
    print(f"Dynamic Range: {metrics['dynamic_range']:.2f}")
    print(f"Spectral Centroid: {metrics['spectral_centroid']:.2f} Hz")
    print(f"Spectral Rolloff: {metrics['spectral_rolloff']:.2f} Hz")

    print("\nCompressor Settings Recommendations:")
    for key, value in settings.items():
        print(f"{key.capitalize()}: {value}")

    print("\nExplanation:")
    print(explanation)

if __name__ == "__main__":
    main()