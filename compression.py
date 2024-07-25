import librosa
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def analyze_audio(file_path):
    """
    Analyze the audio file and return relevant metrics for compressor settings.
    """
    # Load the audio file
    audio, sr = librosa.load(file_path)

    # Calculate the RMS (Root Mean Square) of the audio signal
    rms = np.sqrt(np.mean(audio**2))

    # Calculate the peak level of the audio signal
    peak = np.max(np.abs(audio))

    # Calculate the dynamic range of the audio signal
    dynamic_range = peak - rms

    # Compute the Short-Time Fourier Transform (STFT)
    stft = np.abs(librosa.stft(audio))

    # Calculate the spectral centroid (brightness) of the audio signal
    spectral_centroid = librosa.feature.spectral_centroid(S=stft)

    # Calculate the spectral rolloff (low-end presence) of the audio signal
    spectral_rolloff = librosa.feature.spectral_rolloff(S=stft)

    return {
        'rms': rms,
        'peak': peak,
        'dynamic_range': dynamic_range,
        'spectral_centroid': np.mean(spectral_centroid),
        'spectral_rolloff': np.mean(spectral_rolloff)
    }

def recommend_compressor_settings(metrics):
    """
    Based on the audio metrics, recommend compressor settings using a pre-trained model.
    """
    # Load pre-trained model and tokenizer
    model_name = "distilbert-base-uncased"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Prepare input text
    input_text = f"rms: {metrics['rms']:.2f}, peak: {metrics['peak']:.2f}, dynamic_range: {metrics['dynamic_range']:.2f}, spectral_centroid: {metrics['spectral_centroid']:.2f}, spectral_rolloff: {metrics['spectral_rolloff']:.2f}"

    # Preprocess input text
    inputs = tokenizer(input_text, return_tensors="pt")

    # Get model output
    outputs = model(**inputs)

    # Get predicted class probabilities
    probs = outputs.logits.softmax(dim=1)

    # Define compressor settings classes
    classes = [
        {"threshold": -20, "ratio": 4, "attack": 10, "release": 100, "makeup_gain": 10},
        {"threshold": -15, "ratio": 3, "attack": 30, "release": 200, "makeup_gain": 5},
        {"threshold": -10, "ratio": 2, "attack": 100, "release": 300, "makeup_gain": 0}
    ]

    # Get recommended compressor settings
    recommended_settings = classes[probs.argmax()]

    return recommended_settings

def main():
    file_path = 'stroll.mp3'  # Use 'stroll.mp3' as the default file
    metrics = analyze_audio(file_path)
    settings = recommend_compressor_settings(metrics)

    print("Audio Metrics:")
    print(f"RMS: {metrics['rms']:.2f} dB")
    print(f"Peak: {metrics['peak']:.2f} dB")
    print(f"Dynamic Range: {metrics['dynamic_range']:.2f} dB")
    print(f"Spectral Centroid: {metrics['spectral_centroid']:.2f} Hz")
    print(f"Spectral Rolloff: {metrics['spectral_rolloff']:.2f} Hz")

    print("\nCompressor Settings Recommendations:")
    print(f"Threshold: {settings['threshold']} dB")
    print(f"Ratio: {settings['ratio']}:1")
    print(f"Attack: {settings['attack']} ms")
    print(f"Release: {settings['release']} ms")
    print(f"Makeup Gain: {settings['makeup_gain']} dB")

if __name__ == "__main__":
    main()