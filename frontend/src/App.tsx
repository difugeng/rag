import React from 'react'
import { Layout, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import { useAppLogic } from './hooks/useAppLogic'
import './App.css'

const App: React.FC = () => {
  const {
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
  } = useAppLogic()

  return (
    <ConfigProvider locale={zhCN}>
      <Layout style={{ height: '100vh', overflow: 'hidden' }}>
        <Header />
        <Layout style={{ height: 'calc(100vh - 64px)' }}>
          <Sidebar
            files={pdfFiles}
            selectedFile={selectedFile}
            onSelectFile={setSelectedFile}
            onRefresh={fetchFiles}
            loadingFiles={loadingFiles}
            onVectorize={handleVectorize}
            vectorizing={vectorizing}
            progress={progress}
            onDeleteFile={handleDeleteFile}
            retrievalMode={retrievalMode}
            onRetrievalModeChange={setRetrievalMode}
          />
          <Layout style={{ padding: 0 }}>
            <ChatInterface
              question={question}
              onQuestionChange={setQuestion}
              onAskQuestion={handleAskQuestion}
              loading={loading}
              messages={messages}
            />
          </Layout>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}

export default App
