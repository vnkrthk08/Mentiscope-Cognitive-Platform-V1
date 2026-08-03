import { useState, useEffect } from 'react';
import { Card, Table, Tag, Select, Typography, Space, Spin } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import { adminService } from '../../api/services';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Option } = Select;

const EVENT_COLORS = {
  ASSESSMENT_STARTED: 'blue',
  MODULE_STARTED: 'cyan',
  SCENARIO_LOADED: 'default',
  DECISION_SELECTED: 'purple',
  CORRECT_DECISION: 'green',
  WRONG_DECISION: 'red',
  PANIC_CLICK: 'orange',
  RESOURCE_CHANGED: 'gold',
  TIMEOUT: 'volcano',
  MODULE_COMPLETED: 'geekblue',
  ASSESSMENT_COMPLETED: 'lime',
};

export default function EventLogsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, limit: 50, total: 0 });
  const [filters, setFilters] = useState({ eventType: null, module: null });

  useEffect(() => {
    loadEvents();
  }, [pagination.page, filters]);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
      };
      if (filters.eventType) params.eventType = filters.eventType;
      if (filters.module) params.module = filters.module;

      const res = await adminService.getEvents(params);
      setEvents(res.data.data.events);
      setPagination((prev) => ({ ...prev, total: res.data.data.pagination.total }));
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      render: (val) => dayjs(val).format('MMM DD HH:mm:ss'),
      width: 140,
    },
    {
      title: 'Student',
      dataIndex: ['studentId', 'name'],
      render: (name) => <Text strong>{name || '—'}</Text>,
    },
    {
      title: 'Event Type',
      dataIndex: 'eventType',
      render: (type) => <Tag color={EVENT_COLORS[type] || 'default'}>{type}</Tag>,
    },
    {
      title: 'Module',
      dataIndex: 'module',
      render: (m) => m ? <Tag>M{m}</Tag> : '—',
      width: 80,
    },
    {
      title: 'Scenario',
      dataIndex: 'scenarioId',
      render: (id) => id || '—',
      responsive: ['lg'],
    },
    {
      title: 'Reaction (ms)',
      dataIndex: 'reactionTime',
      render: (val) => val ? `${val}ms` : '—',
      responsive: ['md'],
    },
    {
      title: 'Resource',
      dataIndex: 'selectedResource',
      render: (val) => val || '—',
      responsive: ['lg'],
    },
    {
      title: 'Correct',
      dataIndex: 'correctDecision',
      render: (val) => val === null ? '—' : val ? '✅' : '❌',
      width: 80,
    },
  ];

  return (
    <div className="animate-fade-in">
      <Title level={3} style={{ marginBottom: 24 }}>
        <FileTextOutlined style={{ marginRight: 8 }} />
        Event Logs
      </Title>

      <Card style={{ borderRadius: 12 }}>
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="Filter by event type"
            allowClear
            style={{ width: 220 }}
            onChange={(val) => {
              setFilters((f) => ({ ...f, eventType: val }));
              setPagination((p) => ({ ...p, page: 1 }));
            }}
          >
            {Object.keys(EVENT_COLORS).map((type) => (
              <Option key={type} value={type}>
                <Tag color={EVENT_COLORS[type]} style={{ marginRight: 4 }}>{type}</Tag>
              </Option>
            ))}
          </Select>

          <Select
            placeholder="Filter by module"
            allowClear
            style={{ width: 150 }}
            onChange={(val) => {
              setFilters((f) => ({ ...f, module: val }));
              setPagination((p) => ({ ...p, page: 1 }));
            }}
          >
            <Option value="1">Module 1</Option>
            <Option value="2">Module 2</Option>
            <Option value="3">Module 3</Option>
            <Option value="4">Module 4</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={events}
          rowKey="_id"
          loading={loading}
          pagination={{
            current: pagination.page,
            pageSize: pagination.limit,
            total: pagination.total,
            showSizeChanger: false,
            onChange: (page) => setPagination((prev) => ({ ...prev, page })),
          }}
          scroll={{ x: 900 }}
          size="small"
        />
      </Card>
    </div>
  );
}
