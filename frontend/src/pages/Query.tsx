import React, { useState } from 'react';
import { Card, Input, Button, Row, Col, Typography, Space, Table, Select, message } from 'antd';
import {
  SendOutlined,
  HistoryOutlined,
  SaveOutlined,
  ShareAltOutlined,
  DatabaseOutlined,
  FileTextOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const Query: React.FC = () => {
  const [queryText, setQueryText] = useState('');
  const [selectedDataSource, setSelectedDataSource] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<any>(null);

  const handleRunQuery = async () => {
    if (!queryText.trim()) {
      message.warning('Please enter a query');
      return;
    }

    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setQueryResult({
        columns: [
          { title: 'Region', dataIndex: 'region', key: 'region' },
          { title: 'Sales', dataIndex: 'sales', key: 'sales' },
          { title: 'Growth', dataIndex: 'growth', key: 'growth' },
          { title: 'Customers', dataIndex: 'customers', key: 'customers' },
        ],
        data: [
          { key: '1', region: 'North America', sales: '$1,234,567', growth: '+12%', customers: '2,456' },
          { key: '2', region: 'Europe', sales: '$987,654', growth: '+8%', customers: '1,823' },
          { key: '3', region: 'Asia Pacific', sales: '$756,432', growth: '+15%', customers: '1,567' },
          { key: '4', region: 'Latin America', sales: '$432,109', growth: '+5%', customers: '892' },
        ]
      });
      setIsLoading(false);
      message.success('Query executed successfully!');
    }, 1500);
  };

  const queryHistory = [
    { id: 1, query: 'Show me total sales by region for Q4 2023', time: '10 mins ago' },
    { id: 2, query: 'What are the top performing products?', time: '1 hour ago' },
    { id: 3, query: 'Customer growth rate last 6 months', time: '2 hours ago' },
    { id: 4, query: 'Revenue forecast for next quarter', time: 'Yesterday' },
    { id: 5, query: 'Compare sales YoY', time: 'Yesterday' },
  ];

  const savedQueries = [
    { id: 1, name: 'Monthly Sales Report', description: 'Sales breakdown by region and product' },
    { id: 2, name: 'Customer Analytics', description: 'Customer segmentation and behavior' },
    { id: 3, name: 'Inventory Status', description: 'Current stock levels and projections' },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Title level={2}>Natural Language Query</Title>
          <Text type="secondary">
            Ask questions about your data in plain English. Our AI will understand and fetch the insights you need.
          </Text>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={16}>
          <Card>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong>Select Data Source:</Text>
                <Select
                  value={selectedDataSource}
                  onChange={setSelectedDataSource}
                  style={{ width: '100%', marginTop: 8 }}
                  size="large"
                >
                  <Option value="all">
                    <DatabaseOutlined /> All Data Sources
                  </Option>
                  <Option value="postgres">PostgreSQL - Production</Option>
                  <Option value="sheets">Google Sheets - Sales Data</Option>
                  <Option value="csv">CSV - Customer Data</Option>
                </Select>
              </div>

              <div>
                <Text strong>Enter your question:</Text>
                <TextArea
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="Example: Show me the total sales by region for the last quarter"
                  rows={4}
                  style={{ marginTop: 8 }}
                />
              </div>

              <Space>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleRunQuery}
                  loading={isLoading}
                  size="large"
                >
                  Run Query
                </Button>
                <Button icon={<SaveOutlined />} size="large">
                  Save Query
                </Button>
                <Button icon={<ShareAltOutlined />} size="large">
                  Share
                </Button>
              </Space>
            </Space>
          </Card>

          {queryResult && (
            <Card title="Query Results" style={{ marginTop: 16 }}>
              <Table
                columns={queryResult.columns}
                dataSource={queryResult.data}
                pagination={false}
              />
              <Space style={{ marginTop: 16 }}>
                <Button icon={<FileTextOutlined />}>Export to CSV</Button>
                <Button>Create Dashboard Widget</Button>
              </Space>
            </Card>
          )}
        </Col>

        <Col xs={24} lg={8}>
          <Card title={<><HistoryOutlined /> Query History</>} style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {queryHistory.map(item => (
                <div
                  key={item.id}
                  style={{
                    padding: '8px',
                    cursor: 'pointer',
                    borderRadius: 4,
                    transition: 'background 0.3s',
                  }}
                  onClick={() => setQueryText(item.query)}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f0f0f0'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ fontWeight: 500 }}>{item.query}</div>
                  <Text type="secondary" style={{ fontSize: 12 }}>{item.time}</Text>
                </div>
              ))}
            </Space>
          </Card>

          <Card title={<><SaveOutlined /> Saved Queries</>}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {savedQueries.map(item => (
                <div
                  key={item.id}
                  style={{
                    padding: '8px',
                    cursor: 'pointer',
                    borderRadius: 4,
                    border: '1px solid #f0f0f0',
                  }}
                >
                  <div style={{ fontWeight: 500 }}>{item.name}</div>
                  <Text type="secondary" style={{ fontSize: 12 }}>{item.description}</Text>
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Query;