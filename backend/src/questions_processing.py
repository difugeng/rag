from typing import Dict, List, Optional
import dashscope
import time
from src.config import settings
from src.retrieval import Retrieval
from src.reranking import Reranking

class QuestionProcessor:
    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        self.retrieval = Retrieval()
        self.reranking = Reranking()
    
    def process_question(self, query: str, chunks: List[Dict[str, any]], vectors: Optional[List[List[float]]] = None) -> Dict[str, any]:
        """处理用户问题，生成结构化答案"""
        start_total = time.time()
        print(f"----- 开始处理问题: {query} -----")
        
        timing = {}

        # 1. 构建检索索引
        t0 = time.time()
        self.retrieval.build_index(chunks, vectors)
        timing["index_build"] = time.time() - t0
        print(f"[Timing] 步骤1: 构建索引耗时 {timing['index_build']:.4f}秒 (Chunks数量: {len(chunks)})")
        
        # 2. 混合检索
        t1 = time.time()
        retrieved_chunks = self.retrieval.hybrid_search(query)
        timing["retrieval"] = time.time() - t1
        print(f"[Timing] 步骤2: 混合检索耗时 {timing['retrieval']:.4f}秒")
        
        # 3. 暂时跳过重排序，直接使用检索结果
        # reranked_chunks = self.reranking.rerank(query, retrieved_chunks)
        print(f"[Timing] 步骤3: 重排序已跳过")
        
        # 4. 生成结构化答案
        t2 = time.time()
        answer = self.generate_structured_answer(query, retrieved_chunks)
        timing["llm_generation"] = time.time() - t2
        print(f"[Timing] 步骤4: 生成答案耗时 {timing['llm_generation']:.4f}秒")
        
        total_time = time.time() - start_total
        timing["total"] = total_time
        print(f"----- 处理完成，总耗时: {total_time:.4f}秒 -----")
        
        # 将耗时信息添加到答案中
        answer["timing"] = timing
        
        return answer
    
    def generate_structured_answer(self, query: str, chunks: List[Dict[str, any]]) -> Dict[str, any]:
        """生成结构化答案"""
        # 构建上下文
        context = "\n\n".join([f"相关内容 {i+1} (第{chunk['page_num']}页): {chunk['content']}" for i, chunk in enumerate(chunks)])
        
        # 构建提示词
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的问答助手，请根据提供的上下文，为用户的问题生成结构化的答案。答案应包含：\n1. 分步推理：详细的思考过程\n2. 推理摘要：对推理过程的简要总结\n3. 相关页面：引用的相关内容所在的页面\n4. 最终答案：直接回答用户问题的结论\n\n请严格按照上述结构组织答案，确保逻辑清晰、内容准确。"
            },
            {
                "role": "user",
                "content": f"上下文：{context}\n\n问题：{query}\n\n请生成结构化答案："
            }
        ]
        
        try:
            print("[Timing] 开始调用LLM生成答案...")
            response = dashscope.Generation.call(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.1,
                top_p=0.8
            )
            
            answer_text = response.output['text'].strip()
            
            # 提取结构化信息
            structured_answer = self.parse_structured_answer(answer_text, chunks)
            
            return structured_answer
        except Exception as e:
            print(f"生成答案失败: {e}")
            return {
                "stepByStepReasoning": "生成答案时发生错误",
                "reasoningSummary": "生成答案时发生错误",
                "relatedPages": [],
                "finalAnswer": "生成答案时发生错误"
            }
    
    def parse_structured_answer(self, answer_text: str, chunks: List[Dict[str, any]]) -> Dict[str, any]:
        """解析结构化答案"""
        # 提取分步推理
        step_reasoning_start = answer_text.find("1. 分步推理：")
        step_reasoning_end = answer_text.find("2. 推理摘要：")
        if step_reasoning_start != -1 and step_reasoning_end != -1:
            step_reasoning = answer_text[step_reasoning_start + len("1. 分步推理："):step_reasoning_end].strip()
        else:
            step_reasoning = answer_text
        
        # 提取推理摘要
        summary_start = answer_text.find("2. 推理摘要：")
        summary_end = answer_text.find("3. 相关页面：")
        if summary_start != -1 and summary_end != -1:
            summary = answer_text[summary_start + len("2. 推理摘要："):summary_end].strip()
        else:
            summary = ""
        
        # 提取相关页面
        pages_start = answer_text.find("3. 相关页面：")
        pages_end = answer_text.find("4. 最终答案：")
        if pages_start != -1 and pages_end != -1:
            pages_text = answer_text[pages_start + len("3. 相关页面："):pages_end].strip()
        else:
            pages_text = ""
        
        # 提取最终答案
        final_answer_start = answer_text.find("4. 最终答案：")
        if final_answer_start != -1:
            final_answer = answer_text[final_answer_start + len("4. 最终答案："):].strip()
        else:
            final_answer = answer_text
        
        # 提取相关页面列表
        page_nums = sorted(list(set([chunk['page_num'] for chunk in chunks])))
        
        return {
            "stepByStepReasoning": step_reasoning,
            "reasoningSummary": summary,
            "relatedPages": page_nums,
            "finalAnswer": final_answer
        }
