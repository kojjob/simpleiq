import React, { useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
  Steps,
  Alert,
  Space,
  Card,
  Typography,
  Row,
  Col,
  Avatar,
  message,
  Spin
} from 'antd';
import {
  GoogleOutlined,
  CheckCircleOutlined,
  UserOutlined,
  FileTextOutlined,
  LinkOutlined
} from '@ant-design/icons';
import googleOAuthService, { GoogleSheetsConnectionRequest } from '../services/googleOAuthService';

const { Step } = Steps;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface GoogleSheetsModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: (dataSource: any, userInfo: any) => void;
}

const GoogleSheetsModal: React.FC<GoogleSheetsModalProps> = ({
  visible,
  onCancel,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);

  const resetModal = () => {
    setCurrentStep(0);
    setLoading(false);
    setError(null);
    setUserInfo(null);
    form.resetFields();
  };

  const handleCancel = () => {
    resetModal();
    onCancel();
  };

  const handleFormSubmit = async (values: GoogleSheetsConnectionRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      setCurrentStep(1); // Move to connecting step
      
      const result = await googleOAuthService.completeGoogleSheetsOAuth(values);
      
      setCurrentStep(2); // Success step
      setUserInfo(result.userInfo);
      
      message.success('Google Sheets connected successfully!');
      
      // Call onSuccess after a brief delay to show success state
      setTimeout(() => {
        onSuccess(result.dataSource, result.userInfo);
        resetModal();
      }, 2000);
      
    } catch (error: any) {
      console.error('Google Sheets connection failed:', error);
      setError(error.message || 'Failed to connect to Google Sheets');
      setCurrentStep(0); // Go back to form step
    } finally {
      setLoading(false);
    }
  };

  const validateGoogleSheetsUrl = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('Please enter Google Sheets URL'));
    }
    
    const googleSheetsRegex = /^https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9-_]+/;
    if (!googleSheetsRegex.test(value)) {
      return Promise.reject(new Error('Please enter a valid Google Sheets URL'));
    }
    
    return Promise.resolve();
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Form
            form={form}
            layout="vertical"
            onFinish={handleFormSubmit}
            disabled={loading}
          >
            <Alert
              message="Connect Google Sheets"
              description="Enter your Google Sheets information below. You'll be redirected to Google to authorize SimpleIQ to access your sheet."
              type="info"
              icon={<GoogleOutlined />}
              style={{ marginBottom: 24 }}
            />

            {error && (
              <Alert
                message="Connection Failed"
                description={error}
                type="error"
                style={{ marginBottom: 24 }}
                closable
                onClose={() => setError(null)}
              />
            )}

            <Form.Item
              name="name"
              label="Connection Name"
              rules={[{ required: true, message: 'Please enter a name for this connection' }]}
            >
              <Input 
                placeholder="e.g., Sales Data Q4 2024"
                prefix={<FileTextOutlined />}
              />
            </Form.Item>

            <Form.Item
              name="spreadsheet_url"
              label="Google Sheets URL"
              rules={[
                { required: true, message: 'Please enter Google Sheets URL' },
                { validator: validateGoogleSheetsUrl }
              ]}
            >
              <Input
                placeholder="https://docs.google.com/spreadsheets/d/..."
                prefix={<LinkOutlined />}
              />
            </Form.Item>

            <Form.Item
              name="sheet_name"
              label="Sheet Name"
              initialValue="Sheet1"
            >
              <Input placeholder="Sheet1" />
            </Form.Item>

            <Form.Item
              name="description"
              label="Description (Optional)"
            >
              <TextArea
                placeholder="Description of this data source"
                rows={3}
              />
            </Form.Item>

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Text type="secondary">
                By clicking "Connect", you'll be redirected to Google to authorize access to your sheet.
              </Text>
            </div>
          </Form>
        );

      case 1:
        return (
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <Spin size="large" />
            <Title level={4} style={{ marginTop: 16 }}>
              Connecting to Google Sheets...
            </Title>
            <Paragraph type="secondary">
              Please complete the authorization in the popup window.
            </Paragraph>
            <Alert
              message="OAuth Window"
              description="If the popup window doesn't appear, please check if your browser is blocking popups and try again."
              type="warning"
              showIcon
              style={{ marginTop: 16 }}
            />
          </div>
        );

      case 2:
        return (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            <Title level={3} style={{ marginTop: 16, color: '#52c41a' }}>
              Successfully Connected!
            </Title>

            {userInfo && (
              <Card style={{ marginTop: 24 }}>
                <Row align="middle" justify="center" gutter={16}>
                  <Col>
                    <Avatar
                      src={userInfo.photo}
                      icon={<UserOutlined />}
                      size={48}
                    />
                  </Col>
                  <Col>
                    <div style={{ textAlign: 'left' }}>
                      <Text strong>{userInfo.name}</Text>
                      <br />
                      <Text type="secondary">{userInfo.email}</Text>
                    </div>
                  </Col>
                </Row>
              </Card>
            )}

            <Paragraph type="secondary" style={{ marginTop: 16 }}>
              Your Google Sheets connection has been established successfully.
              You can now use this data source to create queries and dashboards.
            </Paragraph>
          </div>
        );

      default:
        return null;
    }
  };

  const getFooter = () => {
    switch (currentStep) {
      case 0:
        return [
          <Button key="cancel" onClick={handleCancel} disabled={loading}>
            Cancel
          </Button>,
          <Button
            key="connect"
            type="primary"
            icon={<GoogleOutlined />}
            onClick={() => form.submit()}
            loading={loading}
          >
            Connect Google Sheets
          </Button>
        ];
      case 1:
        return [
          <Button key="cancel" onClick={handleCancel} disabled={loading}>
            Cancel
          </Button>
        ];
      case 2:
        return [
          <Button key="done" type="primary" onClick={handleCancel}>
            Done
          </Button>
        ];
      default:
        return [];
    }
  };

  return (
    <Modal
      title={
        <Space>
          <GoogleOutlined style={{ color: '#4285f4' }} />
          Connect Google Sheets
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      footer={getFooter()}
      width={600}
      maskClosable={false}
      destroyOnClose={true}
    >
      <Steps current={currentStep} size="small" style={{ marginBottom: 24 }}>
        <Step title="Enter Details" icon={<FileTextOutlined />} />
        <Step title="Authorize" icon={<GoogleOutlined />} />
        <Step title="Connected" icon={<CheckCircleOutlined />} />
      </Steps>

      {renderStepContent()}
    </Modal>
  );
};

export default GoogleSheetsModal;