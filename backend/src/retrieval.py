import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple, Optional
import dashscope
import time
from src.config import settings

class Retrieval:
    def __init__(self):
        self.vector_index = None
        self.bm25_index = None
        self.chunks = []
        self.vectors = None
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示"""
        try:
            # t0 = time.time()
            response = dashscope.TextEmbedding.call(
                model="text-embedding-v4",
                input=text
            )
            # print(f"单次Embedding耗时: {time.time() - t0:.4f}s")
            return response.output['embeddings'][0]['embedding']
        except Exception as e:
            print(f"获取向量失败: {e}")
            return [0.0] * 1536
    
    def build_index(self, chunks: List[Dict[str, any]], vectors: Optional[List[List[float]]] = None):
        """
        构建向量索引和BM25索引
        :param chunks: 文本块列表
        :param vectors: 预计算的向量列表 (Optional)
        """
        self.chunks = chunks
        
        if not chunks:
            print("警告：chunks为空，无法构建索引")
            self.vectors = np.array([])
            self.vector_index = None
            self.bm25_index = None
            return
        
        # 1. 处理向量
        if vectors is not None and len(vectors) == len(chunks):
            print(f"[Retrieval] 使用预计算的向量 (数量: {len(vectors)})")
            self.vectors = np.array(vectors, dtype='float32')
        else:
            # 如果没有提供向量或数量不匹配，重新计算
            print(f"[Retrieval] 正在为 {len(chunks)} 个分块生成向量(Embedding)...")
            t_embed_start = time.time()
            self.vectors = np.array([self.get_embedding(chunk['content']) for chunk in chunks])
            print(f"[Retrieval] 生成向量总耗时: {time.time() - t_embed_start:.4f}秒")
        
        # 2. 构建FAISS索引
        if len(self.vectors) > 0:
            dimension = self.vectors.shape[1]
            self.vector_index = faiss.IndexFlatL2(dimension)
            self.vector_index.add(self.vectors)
        else:
            self.vector_index = None
        
        # 3. 构建BM25索引
        if chunks:
            # BM25构建速度通常很快，可以实时构建
            tokenized_chunks = [chunk['content'].split() for chunk in chunks]
            self.bm25_index = BM25Okapi(tokenized_chunks)
        else:
            self.bm25_index = None
    
    def vector_search(self, query: str, top_k: int = None) -> List[Tuple[float, Dict[str, any]]]:
        """向量检索"""
        if not self.vector_index:
            return []
        
        top_k = top_k or settings.TOP_K
        query_vector = np.array([self.get_embedding(query)])
        distances, indices = self.vector_index.search(query_vector, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.chunks):
                results.append((distances[0][i], self.chunks[idx]))
        
        return results
    
    def bm25_search(self, query: str, top_k: int = None) -> List[Tuple[float, Dict[str, any]]]:
        """BM25关键词检索"""
        if not self.bm25_index:
            return []
        
        top_k = top_k or settings.TOP_K
        tokenized_query = query.split()
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # 获取top_k结果
        indices = np.argsort(scores)[::-1][:top_k]
        results = [(scores[idx], self.chunks[idx]) for idx in indices]
        
        return results
    
    def hybrid_search(self, query: str, top_k: int = None) -> List[Dict[str, any]]:
        """混合检索，结合向量检索和BM25检索"""
        top_k = top_k or settings.TOP_K
        
        # 获取两种检索结果
        vector_results = self.vector_search(query, top_k)
        bm25_results = self.bm25_search(query, top_k)
        
        # 合并结果，去重
        chunk_ids = set()
        hybrid_results = []
        
        # 先添加向量检索结果
        for _, chunk in vector_results:
            if chunk['chunk_id'] not in chunk_ids:
                chunk_ids.add(chunk['chunk_id'])
                hybrid_results.append(chunk)
        
        # 再添加BM25检索结果
        for _, chunk in bm25_results:
            if chunk['chunk_id'] not in chunk_ids:
                chunk_ids.add(chunk['chunk_id'])
                hybrid_results.append(chunk)
        
        return hybrid_results[:top_k]
