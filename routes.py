import json
import os
import random

import numpy as np
import torch
from flask import request, jsonify, send_from_directory

from app import app, chat
from tts_model import clear_cuda_cache
from utils import normalize_audio, batch_split, combine_audio


@app.route('/')
def index():
    return 'Hell Flask'


@app.route('/tts_audio_stream', methods=['POST'])
def generate_tts_audio_stream():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 400

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


@app.route('/tts_audio', methods=['POST'])
def generate_tts_audio():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.json
    text_file = data.get("text_file", "")
    num_seeds = 1
    seed = 0
    speed = 1
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
    print(f"num_seeds: {num_seeds}")
    print(f"seed: {seed}")
    print(f"speed: {speed}")
    print(f"oral: {oral}")
    print(f"laugh: {laugh}")
    print(f"bk: {bk}")
    print(f"min_length: {min_length}")
    print(f"batch_size: {batch_size}")
    print(f"temperature: {temperature}")
    print(f"top_P: {top_P}")
    print(f"top_K: {top_K}")
    print(f"roleid: {roleid}")
    print(f"refine_text: {refine_text}")
    print(f"speaker_type: {speaker_type}")
    print(f"pt_file: {pt_file}")
    print(f"stream_mode: {stream_mode}")

    from tts_model import generate_audio_for_seed
    from utils import split_text, replace_tokens, restore_tokens
    if seed in [0, -1, None]:
        seed = random.randint(1, 9999)
    content = ''
    if os.path.isfile(text_file):
        content = ""
    elif isinstance(text_file, str):
        content = text_file
    # 将  [uv_break]  [laugh] 替换为 _uv_break_ _laugh_ 处理后再还原
    content = replace_tokens(content)
    texts = split_text(content, min_length=min_length)
    for i, text in enumerate(texts):
        texts[i] = restore_tokens(text)

    if oral < 0 or oral > 9 or laugh < 0 or laugh > 2 or bk < 0 or bk > 7:
        raise ValueError("oral_(0-9), laugh_(0-2), break_(0-7) out of range")

    refine_text_prompt = f"[oral_{oral}][laugh_{laugh}][break_{bk}]"
    try:
        output_files = generate_audio_for_seed(
            chat=chat,
            seed=seed,
            texts=texts,
            batch_size=batch_size,
            speed=speed,
            refine_text_prompt=refine_text_prompt,
            roleid=roleid,
            temperature=temperature,
            top_P=top_P,
            top_K=top_K,
            cur_tqdm=None,
            skip_save=False,
            skip_refine_text=not refine_text,
            speaker_type=speaker_type,
            pt_file=pt_file,
        )
        return output_files
    except Exception as e:
        raise e


@app.route('/output/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('output', filename)
