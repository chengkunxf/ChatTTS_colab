import requests

def upload_pt_file(file_path, upload_url):
    """上传 .pt 文件"""
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(upload_url, files=files)
    return response.json()

def stream_audio_generation(api_url, params):
    """流式接收生成的音频"""
    with requests.post(api_url, json=params, stream=True) as response:
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

# 上传.pt文件的URL
upload_url = 'http://your-server/upload'  # 替换为实际的上传URL

# .pt 文件路径
pt_file_path = 'seed_1315_restored_emb.pt'  # 替换为实际的文件路径

# 上传 .pt 文件并获取文件名
upload_response = upload_pt_file(pt_file_path, upload_url)
pt_file_name = upload_response.get('filename')

# 音频生成API的URL
api_url = 'http://your-server/generate_audio_stream'  # 替换为实际的API URL

# 生成音频的参数
params = {
    "text_file": "测试文本",  # 替换为实际的文本
    "num_seeds": 1,
    "seed": 0,  # 替换为实际的种子
    "speed": 2,
    "oral": 2,
    "laugh": 0,
    "bk": 4,
    "min_length": 80,
    "batch_size": 3,
    "temperature": 0.1,
    "top_P": 0.7,
    "top_K": 20,
    "roleid": "1",
    "refine_text": True,
    "speaker_type": "pt",
    "pt_file": pt_file_name,
    "stream_mode": "fake"
}

# 接收并保存生成的音频流
audio_file_path = 'output_audio.wav'
with open(audio_file_path, 'wb') as audio_file:
    for chunk in stream_audio_generation(api_url, params):
        audio_file.write(chunk)

print(f"音频已保存至 {audio_file_path}")