import React, { useState } from 'react';
import { Upload, App } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Dragger } = Upload;

const InsertData: React.FC = () => {
  const [fileList, setFileList] = useState<any[]>([]);
  const { message } = App.useApp();

  const handleUpload = async (options: any) => {
    const { file, onSuccess, onError } = options;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success(`${file.name} file uploaded successfully.`);
      onSuccess('OK');
    } catch (err: any) {
      console.error('Error uploading file:', err);
      message.error(err.response?.data?.error || `${file.name} file upload failed.`);
      onError(err);
    }
  };

  const props = {
    name: 'file',
    multiple: true,
    fileList,
    customRequest: handleUpload,
    onChange(info: any) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
      setFileList(info.fileList);
    },
    onDrop(e: React.DragEvent) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Upload Documents</h1>
      <Dragger {...props}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Click or drag files to this area to upload</p>
        <p className="ant-upload-hint">
          Support for PDF, TXT, and MD files. You can upload multiple files at once.
        </p>
      </Dragger>
    </div>
  );
};

export default InsertData;