import React from 'react'
import { Typography, Tag, Button, Empty, Popconfirm, Space, Progress } from 'antd'
import { FileTextOutlined, ReloadOutlined, DeleteOutlined, CloseCircleOutlined } from '@ant-design/icons'
import type { PDFFile } from '../types'

const { Text } = Typography

interface FileListProps {
  files: PDFFile[]
  selectedFile: string
  onSelectFile: (filename: string) => void
  onRefresh: () => void
  loading: boolean
  onVectorize: () => void
  vectorizing: boolean
  progress: number
  retrievalMode: 'global' | 'single'
  onDeleteFile: (filename: string) => void
}

const FileList: React.FC<FileListProps> = ({
  files,
  selectedFile,
  onSelectFile,
  onRefresh,
  loading,
  onVectorize,
  vectorizing,
  progress,
  retrievalMode,
  onDeleteFile
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <Text strong>文件列表</Text>
        <Button 
          type="text" 
          icon={<ReloadOutlined spin={loading} />} 
          onClick={onRefresh}
          size="small"
        />
      </div>

      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '12px' }}>
        {files.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无文件" />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {files.map((file) => {
              const isSelected = selectedFile === file.filename
              const isProcessing = vectorizing && isSelected
              
              return (
                <div
                  key={file.filename}
                  onClick={() => {
                    if (retrievalMode === 'single') {
                      onSelectFile(isSelected ? '' : file.filename)
                    }
                  }}
                  style={{
                    cursor: retrievalMode === 'single' ? 'pointer' : 'default',
                    backgroundColor: isSelected ? '#e6f7ff' : 'transparent',
                    borderLeft: isSelected ? '3px solid #1890ff' : '3px solid transparent',
                    padding: '8px 12px',
                    transition: 'all 0.3s',
                    borderRadius: '4px',
                    marginBottom: '4px',
                    opacity: retrievalMode === 'global' ? 0.6 : 1
                  }}
                >
                  <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <Text ellipsis style={{ maxWidth: '140px', fontWeight: isSelected ? 500 : 400 }}>
                        <FileTextOutlined style={{ marginRight: '8px' }} />
                        {file.filename}
                      </Text>
                      <Space size={2}>
                        {file.vectorized && <Tag color="success" style={{ margin: 0 }}>已向量化</Tag>}
                        <Popconfirm
                          title="删除文件"
                          description="确定要删除此文件及其向量数据吗？"
                          onConfirm={(e) => {
                            e?.stopPropagation()
                            onDeleteFile(file.filename)
                          }}
                          onCancel={(e) => e?.stopPropagation()}
                          okText="删除"
                          cancelText="取消"
                        >
                          <Button 
                            type="text" 
                            size="small" 
                            danger
                            icon={<DeleteOutlined />} 
                            onClick={(e) => e.stopPropagation()}
                          />
                        </Popconfirm>
                      </Space>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {Math.round(file.size / 1024)} KB
                      </Text>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {new Date(file.mtime * 1000).toLocaleDateString()}
                      </Text>
                    </div>
                    {isProcessing && (
                      <div style={{ marginTop: '4px' }}>
                         <Progress percent={progress} size="small" status="active" />
                         <Text type="secondary" style={{ fontSize: '10px' }}>
                           正在解析中... {progress}%
                         </Text>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {selectedFile && retrievalMode === 'single' && (
        <div style={{ padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <Text style={{ fontSize: '12px' }} ellipsis>
              当前选中: {selectedFile}
            </Text>
            <Button 
              type="text" 
              size="small" 
              icon={<CloseCircleOutlined />} 
              onClick={() => onSelectFile('')} // Pass empty string to deselect
              title="取消选择"
            />
          </div>
          
          {files.find(f => f.filename === selectedFile)?.vectorized ? (
            <Button block disabled type="default" style={{ color: '#52c41a', borderColor: '#52c41a' }}>
              ✅ 已向量化
            </Button>
          ) : (
            <Button 
              type="primary" 
              block 
              onClick={onVectorize}
              loading={vectorizing}
              disabled={vectorizing}
            >
              {vectorizing ? '正在解析...' : '向量化解析'}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

export default FileList
