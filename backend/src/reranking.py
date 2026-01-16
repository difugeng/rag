from typing import List, Dict
import dashscope
from src.config import settings

class Reranking:
    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    def rerank(self, query: str, chunks: List[Dict[str, any]], top_k: int = None) -> List[Dict[str, any]]:
        """使用LLM对检索结果进行重排序"""
        if not chunks:
            return []
        
        top_k = top_k or settings.RERANK_TOP_K
        
        # 构建文本块内容
        chunks_text = chr(10).join([f"{i}. {chunk['content'][:200]}..." for i, chunk in enumerate(chunks)])
        
        # 构建重排序请求
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的重排序助手，请根据查询与文本块的相关性对文本块进行排序，最相关的排在前面。请返回排序后的文本块索引，用逗号分隔，例如：2,0,1"
            },
            {
                "role": "user",
                "content": f"查询：{query}\n\n文本块：\n{chunks_text}\n\n请返回排序后的索引，用逗号分隔："
            }
        ]
        
        try:
            response = dashscope.Generation.call(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.0,
                top_p=0.0
            )
            
            # 解析重排序结果
            rerank_result = response.output['text'].strip()
            # 提取索引
            indices = [int(idx.strip()) for idx in rerank_result.split(',') if idx.strip().isdigit()]
            
            # 确保索引有效
            valid_indices = [idx for idx in indices if 0 <= idx < len(chunks)]
            
            # 构建重排序后的结果
            reranked_chunks = [chunks[idx] for idx in valid_indices]
            
            # 如果重排序结果不足，补充原始结果
            if len(reranked_chunks) < top_k:
                original_indices = set(range(len(chunks)))
                used_indices = set(valid_indices)
                remaining_indices = list(original_indices - used_indices)
                for idx in remaining_indices[:top_k - len(reranked_chunks)]:
                    reranked_chunks.append(chunks[idx])
            
            return reranked_chunks[:top_k]
        except Exception as e:
            print(f"重排序失败: {e}")
            # 失败时返回原始结果的前top_k个
            return chunks[:top_k]
