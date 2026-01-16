import tiktoken
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import settings

class TextSplitter:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
    
    def count_tokens(self, text: str) -> int:
        """统计文本的 token 数量"""
        if not text:
            return 0
        tokens = self.encoding.encode(text)
        return len(tokens)
    
    def split_text(self, text: str) -> List[str]:
        """将单段文本分割成多个块，使用智能分块策略"""
        if not text or not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def split_page(self, page: Dict[str, any]) -> List[Dict[str, any]]:
        """将单页文本分块，保留页面信息和 token 统计"""
        text = page.get("content", "")
        if not text or not text.strip():
            return []
        
        page_num = page.get("page_num", 1)
        page_width = page.get("page_width", 0)
        page_height = page.get("page_height", 0)
        
        chunks = self.split_text(text)
        
        chunks_with_meta = []
        for i, chunk in enumerate(chunks):
            chunks_with_meta.append({
                "content": chunk,
                "page_num": page_num,
                "chunk_id": f"{page_num}-{i+1}",
                "length_tokens": self.count_tokens(chunk),
                "original_page": {
                    "page_num": page_num,
                    "page_width": page_width,
                    "page_height": page_height
                }
            })
        
        return chunks_with_meta
    
    def split_document(self, pages: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """将文档分割成多个块，每个块包含原始页面信息和 token 统计"""
        chunks = []
        
        for page in pages:
            page_chunks = self.split_page(page)
            chunks.extend(page_chunks)
        
        return chunks
    
    def split_markdown_by_lines(self, markdown_text: str, chunk_size: int = 30, chunk_overlap: int = 5) -> List[Dict[str, any]]:
        """按行分割 markdown 文本，每个分块记录起止行号和内容"""
        lines = markdown_text.split('\n')
        chunks = []
        i = 0
        total_lines = len(lines)
        
        while i < total_lines:
            start = i
            end = min(i + chunk_size, total_lines)
            chunk_text = '\n'.join(lines[start:end])
            
            chunks.append({
                'lines': [start + 1, end],
                'content': chunk_text,
                'length_tokens': self.count_tokens(chunk_text)
            })
            
            i += chunk_size - chunk_overlap
        
        return chunks
    
    def split_markdown_document(self, markdown_text: str) -> List[Dict[str, any]]:
        """将整个 markdown 文档分割成块，保留文档结构"""
        if not markdown_text or not markdown_text.strip():
            return []
        
        chunks = self.split_text(markdown_text)
        
        chunks_with_meta = []
        for i, chunk in enumerate(chunks):
            chunks_with_meta.append({
                "content": chunk,
                "page_num": 1,
                "chunk_id": f"1-{i+1}",
                "length_tokens": self.count_tokens(chunk),
                "original_page": {
                    "page_num": 1,
                    "page_width": 0,
                    "page_height": 0
                }
            })
        
        return chunks_with_meta
    
    def get_chunk_statistics(self, chunks: List[Dict[str, any]]) -> Dict[str, any]:
        """获取分块统计信息"""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_tokens_per_chunk": 0,
                "min_tokens": 0,
                "max_tokens": 0
            }
        
        total_tokens = sum(chunk.get("length_tokens", 0) for chunk in chunks)
        avg_tokens = total_tokens / len(chunks)
        min_tokens = min(chunk.get("length_tokens", 0) for chunk in chunks)
        max_tokens = max(chunk.get("length_tokens", 0) for chunk in chunks)
        
        return {
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "avg_tokens_per_chunk": round(avg_tokens, 2),
            "min_tokens": min_tokens,
            "max_tokens": max_tokens
        }
