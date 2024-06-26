import requests

def save_audio_stream(url, params, output_file):
    """保存流式生成的音频到文件"""
    with requests.post(url, json=params, stream=True) as response:
        response.raise_for_status()  # 如果请求返回错误，抛出异常
        with open(output_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

# 设置请求参数
params = {
    "text_file": "在一个遥远的神奇世界里，住着一只名叫提米的小恐龙。提米喜欢在阳光下探险，他的梦想是找到传说中的彩虹泉。一天，提米在森林里闲逛时，遇到了一只会说话的蝴蝶，名叫莉莉。莉莉告诉提米，彩虹泉就在森林的另一边，但去那里的路充满了挑战。提米决定踏上寻找彩虹泉的旅程。他穿过了五颜六色的花朵，跳过了欢快的小溪。突然，他听到了一阵奇怪的声音。那是一只聪明的小狐狸，名叫弗雷德。弗雷德知道森林里的每一条小路，他决定帮助提米找到彩虹泉。孩子们，提米和弗雷德在前往彩虹泉的路上会遇到什么奇妙的生物呢？是一只会唱歌的树懒，还是一只会跳舞的松鼠？",
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
    "stream_mode": "fake"
}

# API地址
api_url = "https://516352053023a33fcf.gradio.live/generate_tts_audio_stream"

# 输出音频文件路径
output_audio_file = "output_audio.wav"

# 保存流式生成的音频到文件
save_audio_stream(api_url, params, output_audio_file)

print(f"音频已保存至 {output_audio_file}")