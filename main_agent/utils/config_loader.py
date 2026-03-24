import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录 (CareerPlanningAgent/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# 加载 .env
load_dotenv(ROOT_DIR / ".env")

def get_config():
    """
    统一获取项目配置，自动整合 .env 中的敏感信息
    """
    config_path = ROOT_DIR / "config" / "settings.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"未找到配置文件: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 注入环境变量 (如果 .env 中存在，则覆盖 yaml 中的占位符或作为补充)
    if 'llm' in config:
        config['llm']['api_key'] = os.getenv("DASHSCOPE_API_KEY")
    
    if 'mysql' in config:
        config['mysql']['password'] = os.getenv("MYSQL_PASSWORD")
        
    return config

# 导出全局配置对象
settings = get_config()
