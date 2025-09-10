import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Tag,
  Tooltip,
  message,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Badge,
  Typography,
  Tabs,
  Alert,
  Progress,
  Drawer,
  Dropdown,
  Menu
} from 'antd';
import dataSourcesService, { DataSource, DataSourceCreate } from '../services/dataSourcesService';
import googleOAuthService from '../services/googleOAuthService';
import GoogleSheetsModal from '../components/GoogleSheetsModal';
import {
  DatabaseOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  ApiOutlined,
  FileTextOutlined,
  CloudOutlined,
  GoogleOutlined,
  SyncOutlined,
  SettingOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  TableOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;
const { TextArea } = Input;

const DataSources: React.FC = () => {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingSource, setEditingSource] = useState<DataSource | null>(null);
  const [testingConnection, setTestingConnection] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [googleSheetsModalVisible, setGoogleSheetsModalVisible] = useState(false);
  const [form] = Form.useForm();

  // Load data sources from API
  const loadDataSources = async () => {
    try {
      const sources = await dataSourcesService.getDataSources();
      setDataSources(sources);
    } catch (error) {
      console.error('Error loading data sources:', error);
      message.error('Failed to load data sources');
    }
  };

  useEffect(() => {
    loadDataSources();
  }, []);

  const dataSourceTypes = [
    { value: 'postgresql', label: 'PostgreSQL', icon: <DatabaseOutlined />, color: '#336791' },
    { value: 'mysql', label: 'MySQL', icon: <DatabaseOutlined />, color: '#4479A1' },
    { value: 'sqlite', label: 'SQLite', icon: <DatabaseOutlined />, color: '#003B57' },
    { value: 'mongodb', label: 'MongoDB', icon: <DatabaseOutlined />, color: '#47A248' },
    { value: 'bigquery', label: 'Google BigQuery', icon: <CloudOutlined />, color: '#4285F4' },
    { value: 'snowflake', label: 'Snowflake', icon: <CloudOutlined />, color: '#56C0E0' },
    { value: 'rest_api', label: 'REST API', icon: <ApiOutlined />, color: '#FF6B35' },
    { value: 'csv', label: 'CSV File', icon: <FileTextOutlined />, color: '#52C41A' },
    { value: 'google_sheets', label: 'Google Sheets', icon: <GoogleOutlined />, color: '#34A853' }
  ];

  const handleAddDataSource = () => {
    setEditingSource(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleAddGoogleSheets = () => {
    setGoogleSheetsModalVisible(true);
  };

  const handleGoogleSheetsSuccess = async (dataSource: any, userInfo: any) => {
    setGoogleSheetsModalVisible(false);
    // Reload data sources to show the new connection
    await loadDataSources();
    message.success(`Google Sheets connected successfully! Welcome ${userInfo?.name}`);
  };

  const handleEditDataSource = (source: DataSource) => {
    setEditingSource(source);
    form.setFieldsValue(source);
    setIsModalVisible(true);
  };

  const handleDeleteDataSource = async (id: string) => {
    try {
      await dataSourcesService.deleteDataSource(id);
      setDataSources(prev => prev.filter(ds => ds.id !== id));
      message.success('Data source deleted successfully');
    } catch (error) {
      console.error('Error deleting data source:', error);
      message.error('Failed to delete data source');
    }
  };

  const handleTestConnection = async (source: DataSource) => {
    setTestingConnection(source.id);
    
    try {
      // Set status to testing while we test
      setDataSources(prev => 
        prev.map(ds => 
          ds.id === source.id 
            ? { ...ds, status: 'testing' }
            : ds
        )
      );

      let result;
      
      // Use Google Sheets specific test connection for Google Sheets sources
      if (source.type === 'google_sheets') {
        result = await googleOAuthService.testSheetsConnection(source.id);
      } else {
        result = await dataSourcesService.testConnection(source.id);
      }
      
      // Update status and metadata based on test result
      setDataSources(prev => 
        prev.map(ds => 
          ds.id === source.id 
            ? { 
                ...ds, 
                status: result.success ? 'connected' : 'error',
                last_connected: new Date().toISOString(),
                tables_count: result.sheet_info?.rows || result.tables_count || ds.tables_count,
                size: result.size || ds.size,
                tables: result.tables || ds.tables
              }
            : ds
        )
      );
      
      message[result.success ? 'success' : 'error'](result.message);
    } catch (error) {
      console.error('Error testing connection:', error);
      
      // Set status to error
      setDataSources(prev => 
        prev.map(ds => 
          ds.id === source.id 
            ? { ...ds, status: 'error' }
            : ds
        )
      );
      
      message.error('Connection test failed');
    } finally {
      setTestingConnection(null);
    }
  };

  const handleViewTables = (source: DataSource) => {
    setSelectedSource(source);
    setDrawerVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingSource) {
        // Update existing data source
        const updatedSource = await dataSourcesService.updateDataSource(editingSource.id, values);
        setDataSources(prev => prev.map(ds => ds.id === editingSource.id ? updatedSource : ds));
        message.success('Data source updated successfully');
      } else {
        // Create new data source
        const newSource = await dataSourcesService.createDataSource(values as DataSourceCreate);
        setDataSources(prev => [...prev, newSource]);
        message.success('Data source added successfully');
        
        // Test connection automatically after creation
        setTimeout(() => handleTestConnection(newSource), 500);
      }

      setIsModalVisible(false);
    } catch (error) {
      console.error('Error saving data source:', error);
      message.error('Failed to save data source');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'green';
      case 'disconnected': return 'orange';
      case 'testing': return 'blue';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircleOutlined />;
      case 'error': return <CloseCircleOutlined />;
      case 'testing': return <ReloadOutlined spin />;
      default: return <ReloadOutlined spin />;
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: DataSource) => {
        const typeConfig = dataSourceTypes.find(t => t.value === record.type);
        return (
          <Space>
            <span style={{ color: typeConfig?.color }}>{typeConfig?.icon}</span>
            <strong>{text}</strong>
          </Space>
        );
      }
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const typeConfig = dataSourceTypes.find(t => t.value === type);
        return (
          <Tag color="blue">
            {typeConfig?.label}
          </Tag>
        );
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Badge 
          status={getStatusColor(status) as any}
          text={
            <Space>
              {getStatusIcon(status)}
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Space>
          }
        />
      )
    },
    {
      title: 'Connection',
      key: 'connection',
      render: (_, record: DataSource) => {
        if (record.host) {
          return `${record.host}:${record.port}`;
        }
        if (record.connection_string) {
          return record.connection_string.length > 40 
            ? `${record.connection_string.substring(0, 40)}...`
            : record.connection_string;
        }
        return record.database || 'N/A';
      }
    },
    {
      title: 'Tables',
      dataIndex: 'tables_count',
      key: 'tables_count',
      render: (count: number) => count || 0
    },
    {
      title: 'Size',
      dataIndex: 'size',
      key: 'size',
      render: (size: string) => size || 'N/A'
    },
    {
      title: 'Last Connected',
      dataIndex: 'last_connected',
      key: 'last_connected',
      render: (date: string) => date ? new Date(date).toLocaleString() : 'Never'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record: DataSource) => (
        <Space>
          <Tooltip title="Test Connection">
            <Button
              size="small"
              icon={<ReloadOutlined />}
              loading={testingConnection === record.id}
              onClick={() => handleTestConnection(record)}
            />
          </Tooltip>
          <Tooltip title="View Tables">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewTables(record)}
              disabled={!record.tables || record.tables.length === 0}
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEditDataSource(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Are you sure you want to delete this data source?"
            onConfirm={() => handleDeleteDataSource(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Tooltip title="Delete">
              <Button
                size="small"
                icon={<DeleteOutlined />}
                danger
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const connectedCount = dataSources.filter(ds => ds.status === 'connected').length;
  const errorCount = dataSources.filter(ds => ds.status === 'error').length;
  const totalTables = dataSources.reduce((sum, ds) => sum + (ds.tables_count || 0), 0);

  const renderConnectionFields = (type: string) => {
    switch (type) {
      case 'postgresql':
      case 'mysql':
        return (
          <>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="host"
                  label="Host"
                  rules={[{ required: true, message: 'Please enter host' }]}
                >
                  <Input placeholder="localhost" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="port"
                  label="Port"
                  rules={[{ required: true, message: 'Please enter port' }]}
                >
                  <Input placeholder={type === 'postgresql' ? '5432' : '3306'} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item
              name="database"
              label="Database"
              rules={[{ required: true, message: 'Please enter database name' }]}
            >
              <Input placeholder="database_name" />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="username"
                  label="Username"
                  rules={[{ required: true, message: 'Please enter username' }]}
                >
                  <Input placeholder="username" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="password"
                  label="Password"
                  rules={[{ required: true, message: 'Please enter password' }]}
                >
                  <Input.Password placeholder="password" />
                </Form.Item>
              </Col>
            </Row>
          </>
        );
      case 'rest_api':
      case 'csv':
        return (
          <Form.Item
            name="connection_string"
            label="URL/Path"
            rules={[{ required: true, message: 'Please enter URL or file path' }]}
          >
            <Input placeholder="https://api.example.com or /path/to/file.csv" />
          </Form.Item>
        );
      case 'google_sheets':
        return (
          <Alert
            message="Google Sheets Connection"
            description="Google Sheets connections require OAuth authentication. Please use the 'Google Sheets' option from the Add Data Source dropdown to set up this connection."
            type="info"
            showIcon
            action={
              <Button
                size="small"
                type="primary"
                icon={<GoogleOutlined />}
                onClick={() => {
                  setIsModalVisible(false);
                  setGoogleSheetsModalVisible(true);
                }}
              >
                Use Google Sheets Flow
              </Button>
            }
          />
        );
      case 'bigquery':
      case 'snowflake':
        return (
          <>
            <Form.Item
              name="database"
              label="Project/Account"
              rules={[{ required: true, message: 'Please enter project or account' }]}
            >
              <Input placeholder="project-id or account-name" />
            </Form.Item>
            <Form.Item
              name="connection_string"
              label="Service Account/Connection String"
              rules={[{ required: true, message: 'Please enter credentials' }]}
            >
              <TextArea placeholder="Service account JSON or connection string" />
            </Form.Item>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* Statistics Row */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Data Sources"
              value={dataSources.length}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Connected"
              value={connectedCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Errors"
              value={errorCount}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Tables"
              value={totalTables}
              prefix={<TableOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Data Sources Table */}
      <Card
        title={
          <Space>
            <DatabaseOutlined />
            <span>Data Sources</span>
          </Space>
        }
        extra={
          <Space>
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'google-sheets',
                    label: 'Google Sheets',
                    icon: <GoogleOutlined style={{ color: '#34A853' }} />,
                    onClick: handleAddGoogleSheets
                  },
                  {
                    key: 'divider',
                    type: 'divider'
                  },
                  {
                    key: 'other',
                    label: 'Other Data Sources',
                    icon: <DatabaseOutlined />,
                    onClick: handleAddDataSource
                  }
                ]
              }}
              placement="bottomRight"
            >
              <Button type="primary" icon={<PlusOutlined />}>
                Add Data Source
              </Button>
            </Dropdown>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={dataSources}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingSource ? 'Edit Data Source' : 'Add Data Source'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="Name"
            rules={[{ required: true, message: 'Please enter a name' }]}
          >
            <Input placeholder="My Database" />
          </Form.Item>

          <Form.Item
            name="type"
            label="Type"
            rules={[{ required: true, message: 'Please select a type' }]}
          >
            <Select placeholder="Select database type">
              {dataSourceTypes.map(type => (
                <Option key={type.value} value={type.value}>
                  <Space>
                    <span style={{ color: type.color }}>{type.icon}</span>
                    {type.label}
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, current) => prev.type !== current.type}>
            {({ getFieldValue }) => renderConnectionFields(getFieldValue('type'))}
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
          >
            <TextArea
              placeholder="Optional description of this data source"
              rows={3}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setIsModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {editingSource ? 'Update' : 'Add'} Data Source
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Tables Drawer */}
      <Drawer
        title={
          <Space>
            <TableOutlined />
            <span>Tables - {selectedSource?.name}</span>
          </Space>
        }
        width={600}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        {selectedSource?.tables && (
          <div>
            <Alert
              message={`${selectedSource.tables.length} tables found in ${selectedSource.name}`}
              type="info"
              style={{ marginBottom: 16 }}
            />
            
            <Table
              dataSource={selectedSource.tables}
              pagination={false}
              size="small"
              columns={[
                {
                  title: 'Table Name',
                  dataIndex: 'name',
                  key: 'name',
                  render: (name: string) => (
                    <Space>
                      <TableOutlined />
                      <strong>{name}</strong>
                    </Space>
                  )
                },
                {
                  title: 'Rows',
                  dataIndex: 'rows',
                  key: 'rows',
                  render: (rows: number) => rows.toLocaleString()
                },
                {
                  title: 'Size',
                  dataIndex: 'size',
                  key: 'size'
                }
              ]}
            />
          </div>
        )}
      </Drawer>

      {/* Google Sheets OAuth Modal */}
      <GoogleSheetsModal
        visible={googleSheetsModalVisible}
        onCancel={() => setGoogleSheetsModalVisible(false)}
        onSuccess={handleGoogleSheetsSuccess}
      />
    </div>
  );
};

export default DataSources;