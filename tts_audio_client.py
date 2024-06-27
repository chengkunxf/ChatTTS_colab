import requests

# 定义请求URL
APP_BASE_URL = "https://0a6d-34-75-193-236.ngrok-free.app/"
url = "%s/tts_audio" % APP_BASE_URL

# 定义请求数据
data = {
    "text_file": "你好，这是一个测试。",
    "num_seeds": 1,
    "seed": 0,
    "speed": 1,
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
    "pt_file": "seed_1315_restored_emb.pt",
    "stream_mode": "fake"
}

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "any-value"  # 添加自定义请求头
}

# 发送POST请求
response = requests.post(url, headers=headers, json=data)

# 打印返回结果
if response.status_code == 200:
    print("成功返回结果:")
    wav_file_path = response.content.decode('utf-8')  # 解码路径
    print(f"文件路径: {wav_file_path}")

    # 构造完整URL
    base_url = "%s" % APP_BASE_URL
    full_url = base_url + wav_file_path.lstrip("/")
    print(f"完整URL: {full_url}")
else:
    print(f"请求失败，状态码: {response.status_code}")
    print("返回内容:")
    print(response.text)

