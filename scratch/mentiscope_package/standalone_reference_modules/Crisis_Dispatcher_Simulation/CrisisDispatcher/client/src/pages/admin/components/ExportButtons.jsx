import React from 'react';
import { Button, Space } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

export default function ExportButtons({ data, filenamePrefix }) {
  const handleExportCSV = () => {
    if (!data || !data.length) return;

    // Get all unique keys from the data array
    const headers = Array.from(
      new Set(data.flatMap(obj => Object.keys(obj)))
    );

    // Build CSV string
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          let val = row[header];
          // Handle nested objects/arrays by stringifying
          if (typeof val === 'object' && val !== null) {
            val = JSON.stringify(val).replace(/"/g, '""');
          }
          // Escape quotes and wrap in quotes
          return `"${String(val || '').replace(/"/g, '""')}"`;
        }).join(',')
      )
    ].join('\n');

    // Create Blob and download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${filenamePrefix}_${dayjs().format('YYYYMMDD_HHmm')}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Space>
      <Button 
        type="primary" 
        icon={<DownloadOutlined />} 
        onClick={handleExportCSV}
        disabled={!data || data.length === 0}
      >
        Export CSV
      </Button>
    </Space>
  );
}
