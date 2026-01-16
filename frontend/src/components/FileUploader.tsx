import React from 'react'
import { Upload, Button, message } from 'antd'
import { UploadOutlined } from '@ant-design/icons'
import { uploadPdf } from '../api'

interface FileUploaderProps {
  onUploadSuccess: () => void
}

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess }) => {
  const handleUpload = async (file: File) => {
    try {
      await uploadPdf(file)
      message.success('PDF上传成功')
      onUploadSuccess()
      return false
    } catch (error: any) {
      message.error(error.message || '上传失败')
      return false
    }
  }

  return (
    <Upload
      beforeUpload={handleUpload}
      showUploadList={false}
      accept=".pdf"
    >
      <Button icon={<UploadOutlined />} block>
        上传新文档
      </Button>
    </Upload>
  )
}

export default FileUploader
