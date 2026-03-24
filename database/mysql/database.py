import yaml
import os
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

# 加载配置
# 优先从环境变量读取 (为了 Monorepo 聚合)
load_dotenv()

# 默认配置 (如果环境变量中没有，则尝试读取旧的 config 目录)
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DATABASE", "job_system")

if not DB_PASSWORD:
    # 尝试读取旧路径以保持向后兼容
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_PATH = os.path.join(BASE_DIR, "config", "mysql-config.yaml")
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)["mysql"]
            DB_USER = config.get('user', DB_USER)
            DB_PASSWORD = config.get('password', DB_PASSWORD)
            DB_HOST = config.get('host', DB_HOST)
            DB_PORT = config.get('port', DB_PORT)
            DB_NAME = config.get('database', DB_NAME)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_name = Column(String(255), nullable=False)
    salary_range = Column(String(100))
    industry = Column(String(255))
    company_detail = Column(Text)
    raw_detail = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    features = relationship("JobFeature", back_populates="job", cascade="all, delete-orphan")
    profile_json = relationship("JobProfileJson", back_populates="job", uselist=False, cascade="all, delete-orphan")

class JobProfileJson(Base):
    __tablename__ = 'job_profiles_json'
    job_id = Column(BigInteger, ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True)
    profile_data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    job = relationship("Job", back_populates="profile_json")

class JobFeature(Base):
    __tablename__ = 'job_features'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    feature_type = Column(Integer, nullable=False) # 1:S, 2:B, 3:Q, 4:G
    name = Column(String(255), nullable=False)
    evidence = Column(Text)

    job = relationship("Job", back_populates="features")

    __table_args__ = (
        Index('idx_feature_name', 'name'),
    )

from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
