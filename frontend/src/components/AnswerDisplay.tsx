import React, { useState } from 'react'
import { Card, Typography, Space, Tag, Empty, Button } from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { 
  BulbOutlined, 
  OrderedListOutlined, 
  FileTextOutlined,
  BugOutlined
} from '@ant-design/icons'
import type { Answer } from '../types'

const { Title, Text } = Typography

interface AnswerDisplayProps {
  answer: Answer | null
  loading: boolean
}

const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ answer, loading }) => {
  const [showDebug, setShowDebug] = useState(false)

  if (loading && !answer) {
    return (
      <Card variant="borderless" loading={true} style={{ height: '100%' }}>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <Text type="secondary">正在思考中...</Text>
        </div>
      </Card>
    )
  }

  if (!answer) {
    return (
      <div style={{ 
        height: '100%', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        background: '#fcfcfc',
        borderRadius: '8px'
      }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="请输入问题开始检索"
        />
      </div>
    )
  }

  return (
    <div style={{ padding: '0 16px 24px' }}>
      {/* Reasoning Summary */}
      {answer.reasoningSummary && (
        <Card 
          variant="borderless" 
          style={{ 
            marginBottom: '16px', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            borderLeft: '4px solid #faad14'
          }}
        >
          <Space align="start" style={{ marginBottom: '12px' }}>
            <BulbOutlined style={{ fontSize: '20px', color: '#faad14', marginTop: '4px' }} />
            <Title level={5} style={{ margin: 0 }}>推理思路</Title>
          </Space>
          <div style={{ color: '#595959', lineHeight: '1.5' }}>
            {answer.reasoningSummary}
          </div>
        </Card>
      )}

      {/* Step by Step Reasoning */}
      {answer.stepByStepReasoning && (
        <Card 
          variant="borderless" 
          style={{ 
            marginBottom: '16px', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            borderLeft: '4px solid #52c41a'
          }}
        >
          <Space align="start" style={{ marginBottom: '12px' }}>
            <OrderedListOutlined style={{ fontSize: '20px', color: '#52c41a', marginTop: '4px' }} />
            <Title level={5} style={{ margin: 0 }}>检索答案</Title>
          </Space>
          <div style={{ color: '#595959', lineHeight: '1.6' }} className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {answer.stepByStepReasoning}
            </ReactMarkdown>
          </div>
        </Card>
      )}

      {/* Sources */}
      {answer.relatedPages && answer.relatedPages.length > 0 && (
        <Card 
          variant="borderless" 
          style={{ 
            marginBottom: '16px', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            borderLeft: '4px solid #722ed1'
          }}
        >
          <Space align="start" style={{ marginBottom: '12px' }}>
            <FileTextOutlined style={{ fontSize: '20px', color: '#722ed1', marginTop: '4px' }} />
            <Title level={5} style={{ margin: 0 }}>参考来源</Title>
          </Space>
          <div>
            {answer.relatedPages.map((page, index) => (
              <Tag key={index} color="purple" style={{ margin: '4px' }}>
                第 {page} 页
              </Tag>
            ))}
          </div>
        </Card>
      )}

      {/* Timing Info */}
      {answer.timing && (
        <Card 
          size="small"
          variant="borderless"
          style={{ 
            marginBottom: '16px', 
            background: '#fafafa'
          }}
        >
          <Space wrap size="large">
             {answer.timing.total !== undefined && (
                 <Text type="secondary" style={{ fontSize: '12px' }}>
                    总耗时: {answer.timing.total.toFixed(2)}s
                 </Text>
             )}
             {answer.timing.retrieval !== undefined && (
                 <Text type="secondary" style={{ fontSize: '12px' }}>
                    检索: {answer.timing.retrieval.toFixed(2)}s
                 </Text>
             )}
             {answer.timing.llm_generation !== undefined && (
                 <Text type="secondary" style={{ fontSize: '12px' }}>
                    生成: {answer.timing.llm_generation.toFixed(2)}s
                 </Text>
             )}
          </Space>
        </Card>
      )}

      {/* Debug Info Toggle */}
      <div style={{ textAlign: 'right' }}>
        <Button 
          type="text" 
          size="small" 
          icon={<BugOutlined />} 
          onClick={() => setShowDebug(!showDebug)}
          style={{ color: '#8c8c8c' }}
        >
          {showDebug ? '隐藏调试信息' : '显示调试信息'}
        </Button>
      </div>

      {showDebug && (
        <Card size="small" style={{ marginTop: '8px', background: '#f5f5f5' }}>
          <pre style={{ margin: 0, overflow: 'auto', maxHeight: '300px', fontSize: '12px' }}>
            {JSON.stringify(answer, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}

export default AnswerDisplay
