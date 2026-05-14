import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录 (CareerPlanningAgent/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# 加载 .env (优先从 .env 读取)
load_dotenv(ROOT_DIR / ".env")

def get_config():
    """
    统一获取项目配置，自动整合 .env 中的敏感信息
    """
    config_path = ROOT_DIR / "config" / "settings.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"未找到配置文件：{config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 优先从环境变量读取 API Key (如果 .env 中存在)
    if 'llm' in config:
        config['llm']['api_key'] = os.getenv("DASHSCOPE_API_KEY") or config['llm'].get('api_key')
        config['llm']['base_url'] = os.getenv("DASHSCOPE_BASE_URL") or config['llm'].get('base_url', "https://dashscope.aliyuncs.com/compatible-mode/v1")
        config['llm']['model_name'] = os.getenv("DASHSCOPE_MODEL_NAME") or config['llm'].get('model_name', "qwen3.5-flash")

    if 'mysql' in config:
        config['mysql']['password'] = os.getenv("MYSQL_PASSWORD") or config['mysql'].get('password')

    return config

# 导出全局配置对象
settings = get_config()
