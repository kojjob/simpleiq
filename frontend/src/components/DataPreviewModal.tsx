import React, { useState, useEffect } from 'react';
import {
  Modal,
  Table,
  Tabs,
  Alert,
  Space,
  Button,
  Spin,
  Typography,
  Card,
  Row,
  Col,
  Tag,
  Pagination,
  Tooltip,
  Progress,
  Statistic,
  Descriptions,
  message
} from 'antd';
import {
  TableOutlined,
  InfoCircleOutlined,
  DatabaseOutlined,
  EyeOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import googleOAuthService, { DataPreviewResponse, SchemaResponse } from '../services/googleOAuthService';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface DataPreviewModalProps {
  visible: boolean;
  onCancel: () => void;
  dataSourceId: string;
  dataSourceName: string;
}

const DataPreviewModal: React.FC<DataPreviewModalProps> = ({
  visible,
  onCancel,
  dataSourceId,
  dataSourceName
}) => {
  const [loading, setLoading] = useState(false);
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [previewData, setPreviewData] = useState<DataPreviewResponse | null>(null);
  const [schemaData, setSchemaData] = useState<SchemaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [activeTab, setActiveTab] = useState('data');

  const loadPreviewData = async (page: number = currentPage, size: number = pageSize) => {
    setLoading(true);
    setError(null);
    
    try {
      const offset = (page - 1) * size;
      const response = await googleOAuthService.previewSheetsData(dataSourceId, size, offset);
      setPreviewData(response);
    } catch (error: any) {
      console.error('Failed to load preview data:', error);
      setError(error.response?.data?.detail || 'Failed to load preview data');
    } finally {
      setLoading(false);
    }
  };

  const loadSchemaData = async () => {
    setSchemaLoading(true);
    
    try {
      const response = await googleOAuthService.getSheetsSchema(dataSourceId);
      setSchemaData(response);
    } catch (error: any) {
      console.error('Failed to load schema data:', error);
      message.error(error.response?.data?.detail || 'Failed to load schema information');
    } finally {
      setSchemaLoading(false);
    }
  };

  useEffect(() => {
    if (visible && dataSourceId) {
      loadPreviewData(1, pageSize);
      setCurrentPage(1);
      
      if (activeTab === 'schema') {
        loadSchemaData();
      }
    }
  }, [visible, dataSourceId, pageSize]);

  const handlePageChange = (page: number, size?: number) => {
    setCurrentPage(page);
    if (size && size !== pageSize) {
      setPageSize(size);
    }
    loadPreviewData(page, size || pageSize);
  };

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    if (key === 'schema' && !schemaData) {
      loadSchemaData();
    }
  };

  const handleRefresh = () => {
    if (activeTab === 'data') {
      loadPreviewData();
    } else {
      loadSchemaData();
    }
  };

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'integer':
        return 'blue';
      case 'float':
        return 'cyan';
      case 'boolean':
        return 'green';
      case 'varchar':
      default:
        return 'default';
    }
  };

  const renderDataColumns = () => {
    if (!previewData || !previewData.schema.columns.length) return [];
    
    return previewData.schema.columns.map((column) => ({
      title: (
        <Space>
          <Text strong>{column.original_name}</Text>
          <Tag color={getTypeColor(column.type)}>{column.type}</Tag>
        </Space>
      ),
      dataIndex: column.name,
      key: column.name,
      ellipsis: {
        showTitle: false,
      },
      render: (text: any) => (
        <Tooltip title={text}>
          <span>{text}</span>
        </Tooltip>
      ),
    }));
  };

  const renderSchemaColumns = () => {
    if (!schemaData) return [];
    
    return [
      {
        title: 'Column Name',
        dataIndex: 'original_name',
        key: 'original_name',
        render: (text: string) => <Text strong>{text}</Text>,
      },
      {
        title: 'Type',
        dataIndex: 'type',
        key: 'type',
        render: (type: string) => <Tag color={getTypeColor(type)}>{type}</Tag>,
      },
      {
        title: 'Nullable',
        dataIndex: 'nullable',
        key: 'nullable',
        render: (nullable: boolean) => (
          <Tag color={nullable ? 'orange' : 'green'}>
            {nullable ? 'Yes' : 'No'}
          </Tag>
        ),
      },
      {
        title: 'Unique Values',
        dataIndex: 'unique_count',
        key: 'unique_count',
      },
      {
        title: 'Null %',
        dataIndex: 'null_percentage',
        key: 'null_percentage',
        render: (percentage: number) => (
          <Progress 
            percent={Math.round(percentage)} 
            size="small" 
            status={percentage > 50 ? 'exception' : 'normal'}
          />
        ),
      },
      {
        title: 'Sample Values',
        dataIndex: 'sample_values',
        key: 'sample_values',
        render: (values: string[]) => (
          <Space wrap>
            {values.slice(0, 3).map((value, index) => (
              <Tag key={index}>{value}</Tag>
            ))}
            {values.length > 3 && <Text type="secondary">+{values.length - 3} more</Text>}
          </Space>
        ),
      },
    ];
  };

  const renderDataContent = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>Loading data preview...</Text>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <Alert
          message="Failed to Load Data"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => loadPreviewData()}>
              Retry
            </Button>
          }
        />
      );
    }

    if (!previewData) {
      return (
        <Alert
          message="No Data Available"
          description="No preview data could be loaded for this data source."
          type="info"
          showIcon
        />
      );
    }

    return (
      <div>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic 
                title="Total Rows" 
                value={previewData.schema.total_rows} 
                prefix={<DatabaseOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Columns" 
                value={previewData.schema.columns.length} 
                prefix={<TableOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Current Page" 
                value={`${previewData.data.offset + 1}-${previewData.data.offset + previewData.data.count}`} 
                prefix={<EyeOutlined />}
              />
            </Col>
            <Col span={6}>
              <Text type="secondary">
                Sheet: <Text strong>{previewData.schema.sheet_name}</Text>
              </Text>
            </Col>
          </Row>
        </div>

        <Table
          columns={renderDataColumns()}
          dataSource={previewData.data.rows.map((row, index) => ({ ...row, key: index }))}
          pagination={false}
          scroll={{ x: true }}
          size="small"
          bordered
        />

        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <Pagination
            current={currentPage}
            total={previewData.schema.total_rows}
            pageSize={pageSize}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) => 
              `${range[0]}-${range[1]} of ${total} rows`
            }
            pageSizeOptions={['10', '20', '50', '100']}
            onChange={handlePageChange}
          />
        </div>
      </div>
    );
  };

  const renderSchemaContent = () => {
    if (schemaLoading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>Loading schema information...</Text>
          </div>
        </div>
      );
    }

    if (!schemaData) {
      return (
        <Alert
          message="Schema Information Not Available"
          description="Could not load detailed schema information for this data source."
          type="info"
          showIcon
        />
      );
    }

    return (
      <div>
        <Card style={{ marginBottom: 16 }}>
          <Descriptions title="Sheet Information" column={2} size="small">
            <Descriptions.Item label="Sheet Name">{schemaData.schema.sheet_name}</Descriptions.Item>
            <Descriptions.Item label="Spreadsheet ID">{schemaData.schema.spreadsheet_id}</Descriptions.Item>
            <Descriptions.Item label="Total Rows">{schemaData.schema.row_count}</Descriptions.Item>
            <Descriptions.Item label="Total Columns">{schemaData.schema.columns.length}</Descriptions.Item>
            <Descriptions.Item label="Sheet Dimensions">
              {schemaData.schema.sheet_dimensions.rows} × {schemaData.schema.sheet_dimensions.columns}
            </Descriptions.Item>
            <Descriptions.Item label="Last Updated">
              {schemaData.schema.last_updated || 'Unknown'}
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <Table
          columns={renderSchemaColumns()}
          dataSource={schemaData.schema.columns.map((column, index) => ({ ...column, key: index }))}
          pagination={{ pageSize: 50, showSizeChanger: true }}
          scroll={{ x: true }}
          size="small"
          bordered
        />
      </div>
    );
  };

  const getFooterButtons = () => {
    return [
      <Button key="refresh" icon={<ReloadOutlined />} onClick={handleRefresh}>
        Refresh
      </Button>,
      <Button key="close" onClick={onCancel}>
        Close
      </Button>
    ];
  };

  return (
    <Modal
      title={
        <Space>
          <DatabaseOutlined />
          Data Preview - {dataSourceName}
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      footer={getFooterButtons()}
      width={1200}
      style={{ top: 20 }}
    >
      <Tabs activeKey={activeTab} onChange={handleTabChange}>
        <TabPane 
          tab={
            <Space>
              <TableOutlined />
              Data Preview
            </Space>
          } 
          key="data"
        >
          {renderDataContent()}
        </TabPane>
        <TabPane 
          tab={
            <Space>
              <InfoCircleOutlined />
              Schema Details
            </Space>
          } 
          key="schema"
        >
          {renderSchemaContent()}
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default DataPreviewModal;