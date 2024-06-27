import requests

def save_audio_stream(url, text, output_file):
    with open(output_file, 'wb') as f:
        response = requests.get(url, stream=True, params={'text_file': text})
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        else:
            print(f"Failed to get audio stream. Status code: {response.status_code}")

if __name__ == "__main__":
    tts_url = "https://57b4-34-16-152-150.ngrok-free.app/tts"  # 需要根据实际情况修改
    text = "Hello, this is a test of the TTS service."
    output_wav = "output.wav"

    save_audio_stream(tts_url, text, output_wav)
    print(f"Audio saved to {output_wav}")