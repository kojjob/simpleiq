import React, { useState } from 'react';
import { Card, Button, Row, Col, Typography, Space, Tag, Modal, Form, Input, Select, Upload, message } from 'antd';
import {
  PlusOutlined,
  DatabaseOutlined,
  CloudOutlined,
  FileTextOutlined,
  ApiOutlined,
  GoogleOutlined,
  UploadOutlined,
  SyncOutlined,
  SettingOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const DataSources: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  const dataSources = [
    {
      id: 1,
      name: 'PostgreSQL - Production',
      type: 'PostgreSQL',
      icon: <DatabaseOutlined />,
      status: 'connected',
      lastSync: '5 minutes ago',
      records: '1.2M records',
      color: '#1890ff',
    },
    {
      id: 2,
      name: 'Google Sheets - Sales Data',
      type: 'Google Sheets',
      icon: <GoogleOutlined />,
      status: 'connected',
      lastSync: '1 hour ago',
      records: '45K records',
      color: '#34a853',
    },
    {
      id: 3,
      name: 'Customer Data Upload',
      type: 'CSV Upload',
      icon: <FileTextOutlined />,
      status: 'syncing',
      lastSync: 'In progress',
      records: '12K records',
      color: '#fa8c16',
    },
    {
      id: 4,
      name: 'Shopify Store',
      type: 'REST API',
      icon: <ApiOutlined />,
      status: 'error',
      lastSync: 'Failed 2 hours ago',
      records: '89K records',
      color: '#f5222d',
    },
  ];

  const connectorTypes = [
    { type: 'PostgreSQL', icon: <DatabaseOutlined />, category: 'Database' },
    { type: 'MySQL', icon: <DatabaseOutlined />, category: 'Database' },
    { type: 'MongoDB', icon: <DatabaseOutlined />, category: 'Database' },
    { type: 'Google Sheets', icon: <GoogleOutlined />, category: 'Cloud Storage' },
    { type: 'Google Drive', icon: <GoogleOutlined />, category: 'Cloud Storage' },
    { type: 'Dropbox', icon: <CloudOutlined />, category: 'Cloud Storage' },
    { type: 'CSV Upload', icon: <UploadOutlined />, category: 'File Upload' },
    { type: 'Excel Upload', icon: <FileTextOutlined />, category: 'File Upload' },
    { type: 'REST API', icon: <ApiOutlined />, category: 'API' },
    { type: 'GraphQL', icon: <ApiOutlined />, category: 'API' },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'syncing':
        return <ClockCircleOutlined style={{ color: '#fa8c16' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#f5222d' }} />;
      default:
        return null;
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'connected':
        return <Tag color="success">Connected</Tag>;
      case 'syncing':
        return <Tag color="processing">Syncing</Tag>;
      case 'error':
        return <Tag color="error">Error</Tag>;
      default:
        return null;
    }
  };

  const handleAddDataSource = () => {
    setIsModalVisible(true);
  };

  const handleModalOk = () => {
    form.validateFields().then((values) => {
      console.log('Form values:', values);
      message.success('Data source added successfully!');
      setIsModalVisible(false);
      form.resetFields();
    });
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Title level={2}>Data Sources</Title>
              <Text type="secondary">
                Connect and manage your data sources. SimpleIQ supports 50+ connectors.
              </Text>
            </div>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              size="large"
              onClick={handleAddDataSource}
            >
              Add Data Source
            </Button>
          </div>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {dataSources.map((source) => (
          <Col xs={24} sm={12} lg={6} key={source.id}>
            <Card
              hoverable
              style={{ height: '100%' }}
              actions={[
                <Button type="text" icon={<SyncOutlined />} key="sync">
                  Sync
                </Button>,
                <Button type="text" icon={<SettingOutlined />} key="settings">
                  Settings
                </Button>,
                <Button type="text" danger icon={<DeleteOutlined />} key="delete">
                  Delete
                </Button>,
              ]}
            >
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 48, color: source.color, marginBottom: 16 }}>
                  {source.icon}
                </div>
                <Title level={4} style={{ marginBottom: 8 }}>
                  {source.name}
                </Title>
                <Text type="secondary">{source.type}</Text>
                <div style={{ marginTop: 16 }}>
                  {getStatusTag(source.status)}
                </div>
                <div style={{ marginTop: 16 }}>
                  <div style={{ marginBottom: 8 }}>
                    <Text type="secondary">Last sync: </Text>
                    <Text>{source.lastSync}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Records: </Text>
                    <Text strong>{source.records}</Text>
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 32 }}>
        <Col span={24}>
          <Card title="Available Connectors">
            <Paragraph>
              SimpleIQ supports a wide range of data connectors. Choose from databases, cloud storage,
              file uploads, and API integrations.
            </Paragraph>
            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              {connectorTypes.map((connector, index) => (
                <Col xs={12} sm={8} md={6} lg={4} key={index}>
                  <div
                    style={{
                      textAlign: 'center',
                      padding: 16,
                      border: '1px solid #f0f0f0',
                      borderRadius: 8,
                      cursor: 'pointer',
                      transition: 'all 0.3s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#1890ff';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#f0f0f0';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                  >
                    <div style={{ fontSize: 32, color: '#1890ff', marginBottom: 8 }}>
                      {connector.icon}
                    </div>
                    <Text>{connector.type}</Text>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      <Modal
        title="Add New Data Source"
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="type"
            label="Connection Type"
            rules={[{ required: true, message: 'Please select a connection type' }]}
          >
            <Select placeholder="Select a connection type" size="large">
              {connectorTypes.map((connector) => (
                <Option key={connector.type} value={connector.type}>
                  <Space>
                    {connector.icon}
                    {connector.type}
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="name"
            label="Connection Name"
            rules={[{ required: true, message: 'Please enter a connection name' }]}
          >
            <Input placeholder="e.g., Production Database" size="large" />
          </Form.Item>

          <Form.Item
            name="host"
            label="Host"
            rules={[{ required: true, message: 'Please enter the host' }]}
          >
            <Input placeholder="e.g., localhost or 192.168.1.1" size="large" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="port"
                label="Port"
                rules={[{ required: true, message: 'Please enter the port' }]}
              >
                <Input placeholder="e.g., 5432" size="large" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="database"
                label="Database Name"
                rules={[{ required: true, message: 'Please enter the database name' }]}
              >
                <Input placeholder="e.g., mydb" size="large" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="username"
                label="Username"
                rules={[{ required: true, message: 'Please enter the username' }]}
              >
                <Input placeholder="Username" size="large" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="password"
                label="Password"
                rules={[{ required: true, message: 'Please enter the password' }]}
              >
                <Input.Password placeholder="Password" size="large" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default DataSources;