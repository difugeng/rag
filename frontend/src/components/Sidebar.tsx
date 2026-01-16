import React from 'react'
import { Layout, Card, Divider, Radio, Space, Typography } from 'antd'
import FileList from './FileList'
import FileUploader from './FileUploader'
import type { PDFFile } from '../types'

const { Sider } = Layout
const { Text } = Typography

interface SidebarProps {
  files: PDFFile[]
  selectedFile: string
  onSelectFile: (filename: string) => void
  onRefresh: () => void
  loadingFiles: boolean
  onVectorize: () => void
  vectorizing: boolean
  progress: number
  onDeleteFile: (filename: string) => void
  retrievalMode: 'global' | 'single'
  onRetrievalModeChange: (mode: 'global' | 'single') => void
}

const Sidebar: React.FC<SidebarProps> = ({
  files,
  selectedFile,
  onSelectFile,
  onRefresh,
  loadingFiles,
  onVectorize,
  vectorizing,
  progress,
  onDeleteFile,
  retrievalMode,
  onRetrievalModeChange
}) => {
  return (
    <Sider width={320} theme="light" style={{ borderRight: '1px solid #f0f0f0', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', height: '100%' }}>
        
        <Card title="检索设置" size="small" variant="borderless" styles={{ body: { padding: '12px 0' } }}>
          <Space orientation="vertical" style={{ width: '100%' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>检索模式</Text>
            <Radio.Group 
              value={retrievalMode} 
              onChange={(e) => onRetrievalModeChange(e.target.value)}
              buttonStyle="solid"
              style={{ width: '100%' }}
            >
              <Radio.Button value="global" style={{ width: '50%', textAlign: 'center' }}>全局检索</Radio.Button>
              <Radio.Button value="single" style={{ width: '50%', textAlign: 'center' }}>单文件</Radio.Button>
            </Radio.Group>
          </Space>
        </Card>

        <Divider style={{ margin: '12px 0' }} />

        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ marginBottom: '12px' }}>
             <FileUploader onUploadSuccess={onRefresh} />
          </div>
          
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <FileList 
              files={files}
              selectedFile={selectedFile}
              onSelectFile={onSelectFile}
              onRefresh={onRefresh}
              loading={loadingFiles}
              onVectorize={onVectorize}
              vectorizing={vectorizing}
              progress={progress}
              retrievalMode={retrievalMode}
              onDeleteFile={onDeleteFile}
            />
          </div>
        </div>
      </div>
    </Sider>
  )
}

export default Sidebar
