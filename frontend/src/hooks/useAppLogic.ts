import { useState, useEffect, useCallback, useRef } from 'react'
import { message } from 'antd'
import { getPdfFiles, vectorizePdf, askQuestion, deletePdfFile, getVectorizeProgress } from '../api'
import type { PDFFile, Answer, Message } from '../types'

const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2)

export const useAppLogic = () => {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  
  // File management
  const [pdfFiles, setPdfFiles] = useState<PDFFile[]>([])
  const [selectedFile, setSelectedFile] = useState('')
  const [loadingFiles, setLoadingFiles] = useState(false)
  const [vectorizing, setVectorizing] = useState(false)
  const [progress, setProgress] = useState(0)
  
  // Settings
  const [retrievalMode, setRetrievalMode] = useState<'global' | 'single'>('global')

  const fetchFiles = useCallback(async () => {
    setLoadingFiles(true)
    try {
      const files = await getPdfFiles()
      setPdfFiles(files)
    } catch (error: any) {
      message.error(error.message)
    } finally {
      setLoadingFiles(false)
    }
  }, [])

  useEffect(() => {
    fetchFiles()
  }, [fetchFiles])

  // Clear selected file when switching to global mode
  useEffect(() => {
    if (retrievalMode === 'global') {
      setSelectedFile('')
    }
  }, [retrievalMode])

  const handleVectorize = async () => {
    if (!selectedFile) {
      message.warning('请选择要解析的PDF文件')
      return
    }

    setVectorizing(true)
    setProgress(0)
    
    // Start polling progress
    const pollInterval = setInterval(async () => {
      try {
        const p = await getVectorizeProgress(selectedFile)
        setProgress(p)
      } catch (e) {
        console.error('Progress polling error:', e)
      }
    }, 1000)

    try {
      await vectorizePdf(selectedFile)
      message.success('PDF向量解析成功')
      setProgress(100)
      await fetchFiles()
    } catch (error: any) {
      message.error(error.message)
    } finally {
      clearInterval(pollInterval)
      setVectorizing(false)
      // Optional: reset progress after a delay?
    }
  }

  const handleDeleteFile = async (filename: string) => {
    try {
      await deletePdfFile(filename)
      message.success('文件删除成功')
      if (selectedFile === filename) {
        setSelectedFile('')
      }
      await fetchFiles()
    } catch (error: any) {
      message.error(error.message)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      message.warning('请输入问题')
      return
    }

    if (retrievalMode === 'single') {
      if (!selectedFile) {
        message.warning('请选择要检索的文件')
        return
      }
      const file = pdfFiles.find(f => f.filename === selectedFile)
      if (!file || !file.vectorized) {
        message.warning('请选择一个已向量化的文件')
        return
      }
    }

    const userMsg: Message = { id: generateId(), role: 'user', content: question }
    setMessages(prev => [...prev, userMsg])
    const currentQuestion = question
    setQuestion('') // Clear input immediately
    setLoading(true)

    try {
      const result = await askQuestion(currentQuestion, retrievalMode, selectedFile)
      const assistantMsg: Message = { id: generateId(), role: 'assistant', content: result }
      setMessages(prev => [...prev, assistantMsg])
      message.success('获取答案成功')
    } catch (error: any) {
      console.error('Ask question error:', error)
      const errorAnswer: Answer = {
        stepByStepReasoning: '',
        reasoningSummary: '',
        relatedPages: [],
        finalAnswer: `请求失败: ${error.message || '未知错误'}`
      }
      const errorMsg: Message = { id: generateId(), role: 'assistant', content: errorAnswer }
      setMessages(prev => [...prev, errorMsg])
      message.error(`处理问题失败: ${error.message || '未知错误'}`)
    } finally {
      setLoading(false)
    }
  }

  return {
    question,
    setQuestion,
    messages,
    loading,
    pdfFiles,
    selectedFile,
    setSelectedFile,
    loadingFiles,
    fetchFiles,
    vectorizing,
    progress,
    handleVectorize,
    handleDeleteFile,
    retrievalMode,
    setRetrievalMode,
    handleAskQuestion
  }
}
