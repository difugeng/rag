import axios from 'axios'
import type { ApiResponse, Answer, PDFFile } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getPdfFiles = async (): Promise<PDFFile[]> => {
  const response = await api.get<ApiResponse>('/get-pdf-files')
  if (response.data.status === 'success' && response.data.files) {
    return response.data.files
  }
  throw new Error(response.data.message || '获取文件列表失败')
}

export const uploadPdf = async (file: File): Promise<void> => {
  const formData = new FormData()
  formData.append('file', file)
  
  // Use direct axios call to avoid default Content-Type: application/json header
  // Browser will automatically set Content-Type: multipart/form-data with boundary
  const response = await axios.post<ApiResponse>('/api/upload-pdf', formData)
  
  if (response.data.status !== 'success') {
    throw new Error(response.data.message || 'PDF上传失败')
  }
}

export const vectorizePdf = async (filename: string): Promise<void> => {
  const response = await api.post<ApiResponse>('/vectorize-pdf', {
    filename,
  })
  
  if (response.data.status !== 'success') {
    throw new Error(response.data.message || '向量解析失败')
  }
}

export const deletePdfFile = async (filename: string): Promise<void> => {
  const response = await api.delete<ApiResponse>(`/delete-file/${filename}`)
  if (response.data.status !== 'success') {
    throw new Error(response.data.message || '删除文件失败')
  }
}

export const getVectorizeProgress = async (filename: string): Promise<number> => {
  const response = await api.get<any>(`/vectorize-progress/${filename}`)
  if (response.data.status === 'success') {
    return response.data.progress
  }
  return 0
}

export const askQuestion = async (
  question: string,
  mode: 'global' | 'single',
  filename?: string
): Promise<Answer> => {
  const requestData: any = { question }
  
  if (mode === 'single' && filename) {
    requestData.filename = filename
  }
  
  const response = await api.post<ApiResponse>('/ask-question', requestData)
  
  if (response.data && response.data.answer) {
    const backendAnswer = response.data.answer
    return {
      stepByStepReasoning: backendAnswer.stepByStepReasoning || '',
      reasoningSummary: backendAnswer.reasoningSummary || '',
      relatedPages: backendAnswer.relatedPages || [],
      finalAnswer: backendAnswer.finalAnswer || '',
      timing: backendAnswer.timing,
    }
  }
  
  throw new Error('API返回的数据格式不正确')
}
