import requests
import wave
import numpy as np


def generate_tts_audio_stream(url, data):
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json={"data": data}, stream=True)
    response.raise_for_status()

    return response


def save_stream_to_wav(stream, filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit samples
        wf.setframerate(24000)  # 24kHz sample rate

        buffer = b""
        for chunk in stream.iter_content(chunk_size=None):
            if chunk:
                try:
                    # 解析chunk为JSON数据
                    chunk_data = chunk.decode('utf-8')
                    if chunk_data.startswith('{"event_id":'):
                        # 忽略包含event_id的消息
                        continue
                    sample_rate, audio = eval(chunk_data)
                    audio_data = np.array(audio, dtype=np.float32)
                    buffer += audio_data.astype(np.int16).tobytes()
                except ValueError:
                    print(f"Unexpected data format: {chunk}")
                    continue

        wf.writeframes(buffer)


if __name__ == "__main__":
    url = "https://6ebfaea0e399aebc85.gradio.live/call/generate_tts_audio_stream"
    data = [
        "Hello!!",  # text_file
        3,  # num_seeds
        3,  # seed
        1,  # speed
        0,  # oral
        0,  # laugh
        0,  # bk
        3,  # min_length
        3,  # batch_size
        0.01,  # temperature
        0.1,  # top_P
        1,  # top_K
        "1",  # roleid
        True,  # refine_text
        {"path": "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"},  # pt_file
        "real"  # stream_mode
    ]

    stream = generate_tts_audio_stream(url, data)
    save_stream_to_wav(stream, "output.wav")