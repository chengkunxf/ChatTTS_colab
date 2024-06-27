import requests
import time

# 定义请求URL
APP_BASE_URL = "https://17f6-34-75-193-236.ngrok-free.app"
url = "%s/tts_audio" % APP_BASE_URL

# 定义请求数据
data = {
    "text_file": "在一个遥远的神奇世界里，住着一只名叫提米的小恐龙。提米喜欢在阳光下探险，他的梦想是找到传说中的彩虹泉。一天，提米在森林里闲逛时，遇到了一只会说话的蝴蝶，名叫莉莉。",
    "num_seeds": 1,
    "seed": 0,
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
    "pt_file": "seed_1315_restored_emb.pt",
    "stream_mode": "fake"
}

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "any-value"  # 添加自定义请求头
}

# 记录开始时间
start_time = time.time()

# 发送POST请求
response = requests.post(url, headers=headers, json=data)

# 记录结束时间
end_time = time.time()

# 计算执行时间
execution_time = end_time - start_time

# 打印返回结果
if response.status_code == 200:
    print("成功返回结果:")
    wav_file_path = response.content.decode('utf-8')  # 解码路径
    print(f"文件路径: {wav_file_path}")

    # 构造完整URL
    base_url = "%s" % APP_BASE_URL
    full_url = base_url + "/" + wav_file_path.lstrip("/")
    print(f"完整URL: {full_url}")
else:
    print(f"请求失败，状态码: {response.status_code}")
    print("返回内容:")
    print(response.text)

# 打印执行时间
print(f"请求执行时间: {execution_time:.2f} 秒")
