import os
from typing import List, Dict, Optional
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

class PDFParser:

    @staticmethod
    def parse_pdf_by_docling(file_path: str, output_dir: Optional[str] = None) -> List[Dict[str, any]]:
        """使用Docling解析PDF文档"""
        try:
            print(f"正在使用Docling解析PDF: {file_path}")
            
            # 配置 Docling 禁用 OCR，避免下载模型失败
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.do_table_structure = True
            
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            
            result = converter.convert(file_path)
            
            # 输出为 Markdown
            markdown_content = result.document.export_to_markdown()
            
            # 如果指定了输出目录，保存 document.md
            if output_dir:
                md_file = os.path.join(output_dir, "document.md")
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                print(f"Docling解析完成，已保存至: {md_file}")
            
            # 将 Markdown 内容简单包装为 page 结构
            # Docling 的 Markdown 输出是整篇文档，这里暂时作为一个大页面处理
            # 或者如果有分页符，可以尝试分割
            pages = []
            
            # 简单的分页尝试（Docling markdown 可能不包含明确的分页符）
            # 这里为了兼容后续流程，先整体作为一个页面
            pages.append({
                "page_num": 1,
                "content": markdown_content,
                "page_width": 0,
                "page_height": 0
            })
                
            return pages

        except Exception as e:
            print(f"使用Docling解析PDF失败: {e}")
            import traceback
            traceback.print_exc()
            return []
