I have analyzed the project structure and requirements. The `backend` project is already partially set up with FastAPI and the necessary configuration structure. I will now proceed with the implementation to fully meet your requirements.

### **Implementation Plan**

1.  **Modify `backend/src/pdf_parsing.py`**:
    *   Implement the correct MinerU API upload flow:
        1.  Request an upload URL using `/api/v4/file-urls/batch`.
        2.  Upload the local PDF file via `PUT` request to the returned URL.
        3.  Wait for the system to automatically start parsing and poll for results using the `batch_id`.
    *   Add error handling and timeout logic for the upload and polling process.

2.  **Verify & Update Configuration (`backend/src/config.py`)**:
    *   Ensure `DASHSCOPE_API_KEY`, `MINERU_API_KEY`, `LLM_MODEL` (qwen-plus), and `PDF_PARSER` (mineru) are correctly configured.
    *   Confirm `text_embedding_v4` is used for embeddings.

3.  **Review Retrieval & Reranking**:
    *   Verify `backend/src/retrieval.py` uses `dashscope.TextEmbedding.call` with `text-embedding-v4`.
    *   Verify `backend/src/reranking.py` uses `dashscope.Generation.call` with `qwen-plus` for reranking.

4.  **Finalize `backend/src/main.py`**:
    *   Ensure the `vectorize_pdf` endpoint correctly calls the updated `pdf_parsing.py` logic.
    *   Verify the "No Routing" requirement is met (the current implementation already supports direct file/global retrieval without company routing).

5.  **Create `.env` File**:
    *   Although keys are in `config.py`, I will create a `.env` file in `backend/` with the keys to follow best practices and ensure `BaseSettings` loads them correctly.

### **Verification**
*   I will verify the code logic by reading the modified files.
*   Since I cannot make actual API calls to external services (DashScope/MinerU) without a real execution environment and valid keys (I have keys but I am an AI), I will ensure the code follows the official API documentation and the snippets found.

I will start by creating the `.env` file and then modifying the python files.