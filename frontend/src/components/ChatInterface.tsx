import React, { useRef, useEffect } from 'react'
import { Layout, Input, Button, Space, Avatar } from 'antd'
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons'
import AnswerDisplay from './AnswerDisplay'
import type { Answer, Message } from '../types'

const { Content, Footer } = Layout

interface ChatInterfaceProps {
  question: string
  onQuestionChange: (value: string) => void
  onAskQuestion: () => void
  loading: boolean
  messages: Message[]
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  question,
  onQuestionChange,
  onAskQuestion,
  loading,
  messages
}) => {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <Layout style={{ height: '100%', background: '#fff' }}>
      <Content style={{ 
        overflowY: 'auto', 
        padding: '24px 24px',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', width: '100%', flex: 1 }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {messages.map((item) => (
              <div key={item.id} style={{ padding: '16px 0', display: 'flex', gap: '16px' }}>
                <div style={{ flexShrink: 0 }}>
                  <Avatar 
                    icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />} 
                    style={{ backgroundColor: item.role === 'user' ? '#1890ff' : '#52c41a' }}
                  />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 500, marginBottom: '4px' }}>
                    {item.role === 'user' ? '您' : 'RAG 助手'}
                  </div>
                  {item.role === 'user' ? (
                    <div style={{ color: 'rgba(0, 0, 0, 0.88)', fontSize: '16px', whiteSpace: 'pre-wrap' }}>
                      {item.content as string}
                    </div>
                  ) : (
                    <div style={{ marginTop: '8px' }}>
                       <AnswerDisplay answer={item.content as Answer} loading={false} />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {loading && (
             <div style={{ padding: '16px 0', textAlign: 'center', color: '#999' }}>
                <Space>
                  <RobotOutlined spin />
                  思考中...
                </Space>
             </div>
          )}
          
          <div ref={bottomRef} />
        </div>
      </Content>
      
      <Footer style={{ 
        padding: '16px 24px', 
        background: '#fff', 
        borderTop: '1px solid #f0f0f0',
        zIndex: 10
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <Space.Compact style={{ width: '100%' }}>
            <Input.TextArea
              value={question}
              onChange={(e) => onQuestionChange(e.target.value)}
              placeholder="请输入您的问题..."
              autoSize={{ minRows: 3, maxRows: 10 }}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault()
                  onAskQuestion()
                }
              }}
              style={{ resize: 'none' }}
              disabled={loading}
            />
            <Button 
              type="primary" 
              icon={<SendOutlined />} 
              onClick={onAskQuestion}
              loading={loading}
              style={{ height: 'auto' }}
            >
              发送
            </Button>
          </Space.Compact>
        </div>
      </Footer>
    </Layout>
  )
}

export default ChatInterface
