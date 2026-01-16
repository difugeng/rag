from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

class PipelineConfig:
    """流水线配置类，管理所有路径和基本配置"""
    def __init__(self, root_path: Path):
        # 路径配置
        self.root_path = root_path
        
        # 主目录结构
        self.uploads_dir = root_path / "uploads"  # 上传的PDF文件目录
        self.vector_store_dir = root_path / "vector_store"  # 向量存储目录
        
        # 子目录结构
        self.vector_db_dir = self.vector_store_dir  # 向量数据库目录
        
        # 确保目录存在
        for dir_path in [
            self.uploads_dir,
            self.vector_store_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    # API密钥配置
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    
    # 检索配置
    TOP_K: int = 10
    RERANK_TOP_K: int = 5
    
    # 文本分块配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # 模型配置
    LLM_MODEL: str = "qwen-plus"
    
    # PDF解析配置
    PDF_PARSER: str = "docling"  # 可选值: pymupdf, docling
    
    class Config:
        extra = "ignore"  # 忽略未定义的额外字段

# 初始化配置
settings = Settings()

# 获取根路径
ROOT_PATH = Path(__file__).parent.parent

# 初始化流水线配置
pipeline_config = PipelineConfig(ROOT_PATH)
