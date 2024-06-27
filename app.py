import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from gevent import pywsgi
from datetime import timedelta
import logging
from flask.logging import default_handler
from pyngrok import ngrok
import sys

sys.path.insert(0, os.getcwd())
import argparse
from tts_model import load_chat_tts_model

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

# 顺序不能改变，必须完成 Flask 的初始化
from routes import *

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
