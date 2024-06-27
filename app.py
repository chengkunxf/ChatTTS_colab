import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, request, Response, jsonify
from gevent import pywsgi
from datetime import timedelta
import logging
from flask.logging import default_handler
from pyngrok import ngrok
import sys

sys.path.insert(0, os.getcwd())
import argparse
import numpy as np
import random
import json
from utils import normalize_zh, batch_split, normalize_audio, combine_audio
from tts_model import load_chat_tts_model, clear_cuda_cache, generate_audio_for_seed
import torch

parser = argparse.ArgumentParser(description="Gradio ChatTTS MIX")
parser.add_argument("--source", type=str, default="huggingface", help="Model source: 'huggingface' or 'local'.")
parser.add_argument("--local_path", type=str, help="Path to local model if source is 'local'.")
parser.add_argument("--share", default=False, action="store_true", help="Share the server publicly.")

args = parser.parse_args()

# 存放音频种子文件的目录
SAVED_DIR = "saved_seeds"

# mkdir
if not os.path.exists(SAVED_DIR):
    os.makedirs(SAVED_DIR)

# 文件路径
SAVED_SEEDS_FILE = os.path.join(SAVED_DIR, "saved_seeds.json")

# 选中的种子index
SELECTED_SEED_INDEX = -1

# 初始化JSON文件
if not os.path.exists(SAVED_SEEDS_FILE):
    with open(SAVED_SEEDS_FILE, "w") as f:
        f.write("[]")

chat = load_chat_tts_model(source=args.source, local_path=args.local_path)

app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)


@app.route('/')
def index():
    return 'Hell Flask'


@app.route('/tts', methods=['POST'])
def generate_tts_audio_stream():
    data = request.json
    text_file = data.get("text_file", "")
    num_seeds = 1
    seed = 0
    speed = 2
    oral = 2
    laugh = 0
    bk = 4
    min_length = 80
    batch_size = 3
    temperature = 0.1
    top_P = 0.7
    top_K = 20
    roleid = "1"
    refine_text = True
    speaker_type = "pt"
    pt_file = "seed_1315_restored_emb.pt"
    stream_mode = "fake"

    # 打印参数值
    print(f"text_file: {text_file}")

    from utils import split_text, replace_tokens, restore_tokens
    from tts_model import deterministic
    if seed in [0, -1, None]:
        seed = random.randint(1, 9999)
    content = ''
    if os.path.isfile(text_file):
        content = ""
    elif isinstance(text_file, str):
        content = text_file
    # 将  [uv_break]  [laugh] 替换为 _uv_break_ _laugh_ 处理后再还原
    content = replace_tokens(content)
    # texts = [normalize_zh(_) for _ in content.split('\n') if _.strip()]
    texts = split_text(content, min_length=min_length)

    for i, text in enumerate(texts):
        texts[i] = restore_tokens(text)

    if oral < 0 or oral > 9 or laugh < 0 or laugh > 2 or bk < 0 or bk > 7:
        raise ValueError("oral_(0-9), laugh_(0-2), break_(0-7) out of range")

    refine_text_prompt = f"[oral_{oral}][laugh_{laugh}][break_{bk}]"

    print(f"speaker_type: {speaker_type}")
    if speaker_type == "seed":
        if seed in [None, -1, 0, "", "random"]:
            seed = np.random.randint(0, 9999)
        deterministic(seed)
        rnd_spk_emb = chat.sample_random_speaker()
    elif speaker_type == "role":
        # 从 JSON 文件中读取数据
        with open('./slct_voice_240605.json', 'r', encoding='utf-8') as json_file:
            slct_idx_loaded = json.load(json_file)
        # 将包含 Tensor 数据的部分转换回 Tensor 对象
        for key in slct_idx_loaded:
            tensor_list = slct_idx_loaded[key]["tensor"]
            slct_idx_loaded[key]["tensor"] = torch.tensor(tensor_list)
        # 将音色 tensor 打包进params_infer_code，固定使用此音色发音，调低temperature
        rnd_spk_emb = slct_idx_loaded[roleid]["tensor"]
        # temperature = 0.001
    elif speaker_type == "pt":
        print(pt_file)
        rnd_spk_emb = torch.load(pt_file)
        print(rnd_spk_emb.shape)
        if rnd_spk_emb.shape != (768,):
            raise ValueError("维度应为 768。")
    else:
        raise ValueError(f"Invalid speaker_type: {speaker_type}. ")

    params_infer_code = {
        'spk_emb': rnd_spk_emb,
        'prompt': f'[speed_{speed}]',
        'top_P': top_P,
        'top_K': top_K,
        'temperature': temperature
    }
    params_refine_text = {
        'prompt': refine_text_prompt,
        'top_P': top_P,
        'top_K': top_K,
        'temperature': temperature
    }

    if stream_mode == "real":
        for text in texts:
            _params_infer_code = {**params_infer_code}
            wavs_gen = chat.infer(text, params_infer_code=_params_infer_code, params_refine_text=params_refine_text,
                                  use_decoder=True, skip_refine_text=True, stream=True)
            for gen in wavs_gen:
                wavs = [np.array([[]])]
                wavs[0] = np.hstack([wavs[0], np.array(gen[0])])
                audio = wavs[0][0]
                yield 24000, normalize_audio(audio)

            clear_cuda_cache()
    else:
        for text in batch_split(texts, batch_size):
            _params_infer_code = {**params_infer_code}
            wavs = chat.infer(text, params_infer_code=_params_infer_code, params_refine_text=params_refine_text,
                              use_decoder=True, skip_refine_text=False, stream=False)
            combined_audio = combine_audio(wavs)
            yield 24000, combined_audio[0]


if __name__ == '__main__':
    os.makedirs("./logs", exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    file_handler = TimedRotatingFileHandler(
        "logs/app.log", when="D", interval=1, backupCount=15,
        encoding="UTF-8", delay=False, utc=True)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)

    default_handler.setFormatter(formatter)

    app.logger.info("app run")

    # 将your_authtoken替换为你从ngrok获取的认证令牌
    ngrok.set_auth_token("2iRX8HHHMsM00D6ywjfd3MsfYM8_78TdHoi73L1wi1jA4vWZa")

    # 启动ngrok，并将本地5000端口映射到公网
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")

    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
