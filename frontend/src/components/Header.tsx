import React from 'react'
import { Layout, Typography, Space } from 'antd'
import { RobotOutlined } from '@ant-design/icons'

const { Header: AntHeader } = Layout
const { Title } = Typography

const Header: React.FC = () => {
  return (
    <AntHeader style={{ 
      display: 'flex', 
      alignItems: 'center', 
      background: '#fff', 
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      padding: '0 24px',
      zIndex: 10
    }}>
      <Space>
        <RobotOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        <Title level={4} style={{ margin: 0 }}>
          RAG 智能文档问答系统
        </Title>
      </Space>
    </AntHeader>
  )
}

export default Header
