import requests, time
from gradio_client import Client

BASE_URL = "https://644fc3a497bb672d10.gradio.live"

TEXT_FILE = "在一个遥远的神奇世界里，住着一只名叫提米的小恐龙。提米喜欢在阳光下探险，他的梦想是找到传说中的彩虹泉。一天，提米在森林里闲逛时，遇到了一只会说话的蝴蝶，名叫莉莉。莉莉告诉提米，彩虹泉就在森林的另一边，但去那里的路充满了挑战。提米决定踏上寻找彩虹泉的旅程。他穿过了五颜六色的花朵，跳过了欢快的小溪。突然，他听到了一阵奇怪的声音。那是一只聪明的小狐狸，名叫弗雷德。弗雷德知道森林里的每一条小路，他决定帮助提米找到彩虹泉。孩子们，提米和弗雷德在前往彩虹泉的路上会遇到什么奇妙的生物呢？是一只会唱歌的树懒，还是一只会跳舞的松鼠？"


def convert_to_accessible_url(remote_path):
    # 从 /gradio 开始截取路径并拼接成可访问的 URL
    path_start = remote_path.find("/gradio")
    accessible_path = remote_path[path_start:]
    accessible_url = BASE_URL + "/file=/tmp" + accessible_path
    return accessible_url


def download_file_from_url(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"Audio file saved as {local_path}")
    else:
        print(f"Failed to download audio file. Status code: {response.status_code}, Response: {response.text}")


def generate_tts_audio_with_gradio_client():
    start_time = time.time()
    client = Client(BASE_URL)

    # 设置请求数据
    result = client.predict(
        text_file=("%s" % TEXT_FILE),
        num_seeds=1,
        seed=3,
        speed=5,
        oral=2,
        laugh=0,
        bk=4,
        min_length=80,
        batch_size=3,
        temperature=0.1,
        top_P=0.7,
        top_K=20,
        roleid="1",
        refine_text=True,
        pt_file=None,
        api_name="/generate_tts_audio"
    )

    # 获取返回的文件路径并转换为可访问的 URL
    remote_file_path = result
    accessible_url = convert_to_accessible_url(remote_file_path)
    print(f"Accessible URL: {accessible_url}")

    # 下载文件并保存到本地
    # local_file_path = "output.wav"
    # download_file_from_url(accessible_url, local_file_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")


# 调用函数生成 TTS 音频
generate_tts_audio_with_gradio_client()
