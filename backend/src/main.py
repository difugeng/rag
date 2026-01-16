from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import os
import tempfile
import json
import shutil
import hashlib
import numpy as np
from pathlib import Path
from src.pdf_parsing import PDFParser
from src.text_splitter import TextSplitter
from src.questions_processing import QuestionProcessor
from src.retrieval import Retrieval
from src.config import settings, pipeline_config

app = FastAPI(title="RAG问答系统 API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务，用于提供上传的PDF文件访问
app.mount("/uploads", StaticFiles(directory=str(pipeline_config.uploads_dir)), name="uploads")

# 全局变量
# 向量解析进度跟踪
task_progress = {}

# 从配置中获取路径
vector_store_dir = str(pipeline_config.vector_store_dir)
uploads_dir = str(pipeline_config.uploads_dir)



def get_file_vector_status(filename: str) -> Dict[str, Any]:
    """获取文件的向量状态"""
    file_path = os.path.join(uploads_dir, filename)
    if not os.path.exists(file_path):
        return {"status": "error", "message": "文件不存在"}
    
    # 使用文件名（不带扩展名）作为向量存储目录名
    file_name_without_ext = os.path.splitext(filename)[0]
    file_vector_dir = os.path.join(vector_store_dir, file_name_without_ext)
    vectorized = os.path.exists(os.path.join(file_vector_dir, "chunks.json"))
    
    return {
        "status": "success",
        "filename": filename,
        "vectorized": vectorized,
        "vector_store_dir": file_vector_dir
    }


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """上传PDF文档"""
    try:
        # 确保上传目录存在
        pipeline_config.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建文件路径
        file_path = pipeline_config.uploads_dir / file.filename
        
        # 保存上传的文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "status": "success",
            "message": "PDF上传成功",
            "filename": file.filename,
            "file_path": str(file_path)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"PDF上传失败: {str(e)}"
        }

@app.get("/api/get-pdf-files")
async def get_pdf_files():
    """获取uploads文件夹中的PDF文件列表，包含向量状态"""
    try:
        # 获取文件夹中的所有PDF文件
        pdf_files = []
        for filename in os.listdir(pipeline_config.uploads_dir):
            if filename.lower().endswith(".pdf"):
                file_path = pipeline_config.uploads_dir / filename
                file_stats = file_path.stat()
                
                # 获取向量状态，使用文件名（不带扩展名）作为向量存储目录名
                file_name_without_ext = os.path.splitext(filename)[0]
                file_vector_dir = pipeline_config.vector_store_dir / file_name_without_ext
                vectorized = (file_vector_dir / "chunks.json").exists()
                
                pdf_files.append({
                    "filename": filename,
                    "file_path": str(file_path),
                    "size": file_stats.st_size,
                    "mtime": file_stats.st_mtime,
                    "vectorized": vectorized
                })
        
        # 按修改时间排序，最新的在前
        pdf_files.sort(key=lambda x: x["mtime"], reverse=True)
        
        return {
            "status": "success",
            "files": pdf_files
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"获取文件列表失败: {str(e)}"
        }

@app.post("/api/vectorize-pdf")
def vectorize_pdf(file_info: Dict[str, str]):
    """将PDF文件向量化并存储"""
    try:
        filename = file_info.get("filename", "")
        if not filename:
            return {
                "status": "error",
                "message": "文件名不能为空"
            }
        
        # 初始化进度
        task_progress[filename] = 0
        
        # 构建完整文件路径
        file_path = pipeline_config.uploads_dir / filename
        
        # 检查文件是否存在
        if not file_path.exists():
            return {
                "status": "error",
                "message": "文件不存在"
            }
        
        # 检查文件是否为PDF
        if not filename.lower().endswith(".pdf"):
            return {
                "status": "error",
                "message": "请选择PDF文件"
            }
        
        # 使用文件名（不带扩展名）作为向量存储目录名
        file_name_without_ext = os.path.splitext(filename)[0]
        file_vector_dir = pipeline_config.vector_store_dir / file_name_without_ext
        
        # 创建文件向量存储目录
        file_vector_dir.mkdir(parents=True, exist_ok=True)
        task_progress[filename] = 5
        
        # --------------------------
        # 1. 调用Docling API解析PDF生成document.md
        # --------------------------
        markdown_file = file_vector_dir / "document.md"
        # 检查是否已存在document.md且不为空
        if markdown_file.exists() and markdown_file.stat().st_size > 0:
            print(f"步骤1: PDF {filename} 已存在document.md，跳过Docling解析...")
            task_progress[filename] = 30
        else:
            print(f"步骤1: 调用Docling API解析PDF {filename} 生成document.md...")
            parser = PDFParser()
            task_progress[filename] = 10
            
            # 使用Docling解析PDF
            # parse_pdf_by_docling方法内部已经处理了document.md的生成
            pages = parser.parse_pdf_by_docling(str(file_path), output_dir=str(file_vector_dir))
            
            # 检查是否生成了document.md
            if not markdown_file.exists() or markdown_file.stat().st_size == 0:
                print(f"步骤1: Docling未生成document.md，解析失败")
                task_progress[filename] = 0
                return {
                    "status": "error",
                    "message": "PDF解析失败，未生成文档内容"
                }
            
            task_progress[filename] = 40
        
        # --------------------------
        # 2. 从document.md解析并分块
        # --------------------------
        print(f"步骤2: 从document.md解析并分块...")
        task_progress[filename] = 45
        
        # 从document.md读取内容
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # 将markdown转换为pages格式，用于分块
        # 检查是否包含"# Page "标记
        pages = []
        if "# Page " in markdown_content:
            # 按"# Page "分割markdown内容
            page_sections = markdown_content.split("# Page ")
            for i, section in enumerate(page_sections[1:], 1):
                # 提取页面内容
                content = section.split("\n\n", 1)[1].strip() if "\n\n" in section else section.strip()
                pages.append({
                    "page_num": i,
                    "content": content,
                    "page_width": 0,
                    "page_height": 0
                })
        else:
            # 如果没有"# Page "标记，将整个文档作为一个页面
            pages.append({
                "page_num": 1,
                "content": markdown_content,
                "page_width": 0,
                "page_height": 0
            })
        
        # 文本分块
        splitter = TextSplitter()
        chunks = splitter.split_document(pages)
        
        # 获取分块统计信息
        stats = splitter.get_chunk_statistics(chunks)
        print(f"分块统计: {stats}")
        
        # 保存切块数据到向量存储目录
        chunks_file = file_vector_dir / "chunks.json"
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        task_progress[filename] = 60
        
        # --------------------------
        # 3. 从分块报告创建向量数据库
        # --------------------------
        print(f"步骤3: 为PDF {filename} 创建向量数据库...")
        task_progress[filename] = 70
        
        # 构建向量索引
        retrieval = Retrieval()
        retrieval.build_index(chunks)
        task_progress[filename] = 90
        
        # 保存向量和索引信息
        vectors_file = file_vector_dir / "vectors.npy"
        np.save(vectors_file, retrieval.vectors)
        
        # 保存文件元信息
        metadata = {
            "filename": filename,
            "file_path": str(file_path),
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "vectorized_at": json.dumps({"$date": "2024-01-13T00:00:00.000Z"}),
            "has_markdown": True,
            "has_chunks": True,
            "has_vectors": True
        }
        metadata_file = file_vector_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 完成进度
        task_progress[filename] = 100
        
        return {
            "status": "success",
            "message": "PDF向量化成功",
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "steps": [
                "PDF转markdown完成",
                "报告分块完成",
                "向量数据库创建完成"
            ]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 出错时清除进度
        if filename in task_progress:
            del task_progress[filename]
        return {
            "status": "error",
            "message": f"PDF向量化失败: {str(e)}"
        }

@app.get("/api/vectorize-progress/{filename}")
async def get_vectorize_progress(filename: str):
    """获取PDF向量化进度"""
    return {
        "status": "success",
        "filename": filename,
        "progress": task_progress.get(filename, 0)
    }

@app.post("/api/ask-question")
async def ask_question(question: Dict[str, str]):
    """处理用户问题，生成答案"""
    try:
        query = question.get("question", "")
        filename = question.get("filename", "")
        
        if not query:
            return {
                "status": "error",
                "message": "问题不能为空"
            }
        
        # 加载向量和切块数据
        all_chunks = []
        all_vectors = []
        
        if filename:
            # 单文件检索，使用文件名（不带扩展名）作为向量存储目录名
            file_name_without_ext = os.path.splitext(filename)[0]
            file_vector_dir = os.path.join(vector_store_dir, file_name_without_ext)
            chunks_file = os.path.join(file_vector_dir, "chunks.json")
            vectors_file = os.path.join(file_vector_dir, "vectors.npy")
            
            if not os.path.exists(chunks_file):
                return {
                    "status": "error",
                    "message": "该文件尚未向量化，请先进行向量解析"
                }
            
            # 加载单个文件的切块数据
            with open(chunks_file, "r", encoding="utf-8") as f:
                all_chunks = json.load(f)
            
            # 加载向量数据
            if os.path.exists(vectors_file):
                try:
                    vectors = np.load(vectors_file)
                    all_vectors.extend(vectors.tolist())
                except Exception as e:
                    print(f"加载向量文件失败 {vectors_file}: {e}")
        else:
            # 全局检索，加载所有向量化文件的切块数据
            vectorized_files = []
            for dir_name in os.listdir(vector_store_dir):
                file_vector_dir = os.path.join(vector_store_dir, dir_name)
                chunks_file = os.path.join(file_vector_dir, "chunks.json")
                if os.path.exists(chunks_file):
                    vectorized_files.append(file_vector_dir)
            
            if not vectorized_files:
                return {
                    "status": "error",
                    "message": "没有已向量化的文件，请先对文件进行向量解析"
                }
            
            # 加载所有文件的切块数据
            for file_vector_dir in vectorized_files:
                chunks_file = os.path.join(file_vector_dir, "chunks.json")
                vectors_file = os.path.join(file_vector_dir, "vectors.npy")
                
                with open(chunks_file, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                    all_chunks.extend(chunks)
                
                # 加载向量数据
                if os.path.exists(vectors_file):
                    try:
                        vectors = np.load(vectors_file)
                        all_vectors.extend(vectors.tolist())
                    except Exception as e:
                        print(f"加载向量文件失败 {vectors_file}: {e}")
        
        # 确保向量数量与chunks数量一致，否则不使用预计算向量
        if len(all_vectors) != len(all_chunks):
            print(f"警告: 向量数量 ({len(all_vectors)}) 与 Chunks 数量 ({len(all_chunks)}) 不一致，将重新计算向量")
            all_vectors = None
        
        # 处理问题
        processor = QuestionProcessor()
        # 传入预计算的向量
        answer = processor.process_question(query, all_chunks, all_vectors)
        
        return {
            "status": "success",
            "answer": answer
        }
    except Exception as e:
        # 打印错误详情，方便调试
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"处理问题失败: {str(e)}"
        }

@app.delete("/api/delete-file/{filename}")
async def delete_file(filename: str):
    """删除文件及其相关数据"""
    try:
        # 1. 删除上传的文件
        file_path = pipeline_config.uploads_dir / filename
        if file_path.exists():
            os.remove(file_path)
            
        # 2. 删除向量存储目录
        file_name_without_ext = os.path.splitext(filename)[0]
        file_vector_dir = pipeline_config.vector_store_dir / file_name_without_ext
        if file_vector_dir.exists():
            shutil.rmtree(file_vector_dir)
            
        # 3. 清除进度信息
        if filename in task_progress:
            del task_progress[filename]
            
        return {
            "status": "success",
            "message": f"文件 {filename} 及相关数据已删除"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"删除文件失败: {str(e)}"
        }

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    # 简单的状态检查，不再依赖processed_chunks全局变量
    return {
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
