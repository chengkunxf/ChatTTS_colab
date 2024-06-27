import requests

def save_audio_stream(url, payload, output_file, user_agent):
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json'
    }

    with open(output_file, 'wb') as f:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        else:
            print(f"Failed to get audio stream. Status code: {response.status_code}")

if __name__ == "__main__":
    tts_url = "https://9ad0-34-16-152-150.ngrok-free.app/tts"  # 根据实际情况修改
    text = "Hello, this is a test of the TTS service."
    payload = {"text_file": text}
    output_wav = "output.wav"
    user_agent = "CustomUserAgent/1.0"

    save_audio_stream(tts_url, payload, output_wav, user_agent)
    print(f"Audio saved to {output_wav}")