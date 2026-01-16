export interface PDFFile {
  filename: string
  size: number
  mtime: number
  vectorized: boolean
}

export interface Answer {
  stepByStepReasoning: string
  reasoningSummary: string
  relatedPages: number[]
  finalAnswer: string
  timing?: {
    index_build?: number
    retrieval?: number
    llm_generation?: number
    total?: number
  }
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string | Answer
}

export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  message?: string
  data?: T
  files?: PDFFile[]
  answer?: Answer
}
