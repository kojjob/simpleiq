import React, { useState } from 'react';
import { Card, Form, Input, Button, Switch, Select, Tabs, Typography, Space, message, Divider, Tag } from 'antd';
import {
  UserOutlined,
  LockOutlined,
  BellOutlined,
  SettingOutlined,
  ApiOutlined,
  TeamOutlined,
  SaveOutlined,
  PlusOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const Settings: React.FC = () => {
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [notificationForm] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleProfileSave = (values: any) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      message.success('Profile updated successfully!');
      console.log('Profile values:', values);
    }, 1000);
  };

  const handlePasswordChange = (values: any) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      message.success('Password changed successfully!');
      passwordForm.resetFields();
      console.log('Password change:', values);
    }, 1000);
  };

  const handleNotificationSave = (values: any) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      message.success('Notification preferences saved!');
      console.log('Notification preferences:', values);
    }, 1000);
  };

  return (
    <div>
      <Title level={2}>Settings</Title>
      <Text type="secondary">Manage your account settings and preferences</Text>

      <Tabs defaultActiveKey="profile" style={{ marginTop: 24 }}>
        <TabPane
          tab={
            <span>
              <UserOutlined />
              Profile
            </span>
          }
          key="profile"
        >
          <Card>
            <Form
              form={profileForm}
              layout="vertical"
              onFinish={handleProfileSave}
              initialValues={{
                email: 'user@example.com',
                fullName: 'John Doe',
                company: 'Acme Inc',
                role: 'Data Analyst',
                timezone: 'UTC-5',
              }}
            >
              <Form.Item
                name="email"
                label="Email Address"
                rules={[{ required: true, type: 'email', message: 'Please enter a valid email' }]}
              >
                <Input size="large" disabled />
              </Form.Item>

              <Form.Item
                name="fullName"
                label="Full Name"
                rules={[{ required: true, message: 'Please enter your full name' }]}
              >
                <Input size="large" />
              </Form.Item>

              <Form.Item
                name="company"
                label="Company"
                rules={[{ required: true, message: 'Please enter your company name' }]}
              >
                <Input size="large" />
              </Form.Item>

              <Form.Item name="role" label="Role">
                <Input size="large" />
              </Form.Item>

              <Form.Item name="timezone" label="Timezone">
                <Select size="large">
                  <Option value="UTC-12">UTC-12:00</Option>
                  <Option value="UTC-11">UTC-11:00</Option>
                  <Option value="UTC-10">UTC-10:00</Option>
                  <Option value="UTC-9">UTC-09:00</Option>
                  <Option value="UTC-8">UTC-08:00</Option>
                  <Option value="UTC-7">UTC-07:00</Option>
                  <Option value="UTC-6">UTC-06:00</Option>
                  <Option value="UTC-5">UTC-05:00</Option>
                  <Option value="UTC-4">UTC-04:00</Option>
                  <Option value="UTC-3">UTC-03:00</Option>
                  <Option value="UTC-2">UTC-02:00</Option>
                  <Option value="UTC-1">UTC-01:00</Option>
                  <Option value="UTC+0">UTC+00:00</Option>
                  <Option value="UTC+1">UTC+01:00</Option>
                  <Option value="UTC+2">UTC+02:00</Option>
                  <Option value="UTC+3">UTC+03:00</Option>
                  <Option value="UTC+4">UTC+04:00</Option>
                  <Option value="UTC+5">UTC+05:00</Option>
                  <Option value="UTC+6">UTC+06:00</Option>
                  <Option value="UTC+7">UTC+07:00</Option>
                  <Option value="UTC+8">UTC+08:00</Option>
                  <Option value="UTC+9">UTC+09:00</Option>
                  <Option value="UTC+10">UTC+10:00</Option>
                  <Option value="UTC+11">UTC+11:00</Option>
                  <Option value="UTC+12">UTC+12:00</Option>
                </Select>
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                  Save Changes
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <LockOutlined />
              Security
            </span>
          }
          key="security"
        >
          <Card title="Change Password">
            <Form form={passwordForm} layout="vertical" onFinish={handlePasswordChange}>
              <Form.Item
                name="currentPassword"
                label="Current Password"
                rules={[{ required: true, message: 'Please enter your current password' }]}
              >
                <Input.Password size="large" />
              </Form.Item>

              <Form.Item
                name="newPassword"
                label="New Password"
                rules={[
                  { required: true, message: 'Please enter a new password' },
                  { min: 8, message: 'Password must be at least 8 characters' },
                ]}
              >
                <Input.Password size="large" />
              </Form.Item>

              <Form.Item
                name="confirmPassword"
                label="Confirm New Password"
                dependencies={['newPassword']}
                rules={[
                  { required: true, message: 'Please confirm your new password' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('newPassword') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('Passwords do not match'));
                    },
                  }),
                ]}
              >
                <Input.Password size="large" />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Change Password
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="Two-Factor Authentication" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <Text strong>Enable Two-Factor Authentication</Text>
                  <br />
                  <Text type="secondary">Add an extra layer of security to your account</Text>
                </div>
                <Switch />
              </div>
            </Space>
          </Card>

          <Card title="Active Sessions" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Text strong>Current Session</Text>
                <br />
                <Text type="secondary">Chrome on MacOS • Last active: Now</Text>
              </div>
              <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Text>Safari on iPhone</Text>
                <br />
                <Text type="secondary">Last active: 2 hours ago</Text>
              </div>
            </Space>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <BellOutlined />
              Notifications
            </span>
          }
          key="notifications"
        >
          <Card>
            <Form
              form={notificationForm}
              layout="vertical"
              onFinish={handleNotificationSave}
              initialValues={{
                emailNotifications: true,
                queryCompleted: true,
                dataSourceStatus: true,
                weeklyReport: false,
                productUpdates: true,
              }}
            >
              <Form.Item name="emailNotifications" valuePropName="checked">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong>Email Notifications</Text>
                    <br />
                    <Text type="secondary">Receive notifications via email</Text>
                  </div>
                  <Form.Item name="emailNotifications" valuePropName="checked" style={{ margin: 0 }}>
                    <Switch />
                  </Form.Item>
                </div>
              </Form.Item>

              <Divider />

              <Form.Item name="queryCompleted" valuePropName="checked">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong>Query Completed</Text>
                    <br />
                    <Text type="secondary">Get notified when your queries finish running</Text>
                  </div>
                  <Form.Item name="queryCompleted" valuePropName="checked" style={{ margin: 0 }}>
                    <Switch />
                  </Form.Item>
                </div>
              </Form.Item>

              <Divider />

              <Form.Item name="dataSourceStatus" valuePropName="checked">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong>Data Source Status</Text>
                    <br />
                    <Text type="secondary">Alerts for data source connection issues</Text>
                  </div>
                  <Form.Item name="dataSourceStatus" valuePropName="checked" style={{ margin: 0 }}>
                    <Switch />
                  </Form.Item>
                </div>
              </Form.Item>

              <Divider />

              <Form.Item name="weeklyReport" valuePropName="checked">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong>Weekly Usage Report</Text>
                    <br />
                    <Text type="secondary">Receive weekly summary of your usage</Text>
                  </div>
                  <Form.Item name="weeklyReport" valuePropName="checked" style={{ margin: 0 }}>
                    <Switch />
                  </Form.Item>
                </div>
              </Form.Item>

              <Divider />

              <Form.Item name="productUpdates" valuePropName="checked">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong>Product Updates</Text>
                    <br />
                    <Text type="secondary">New features and improvements</Text>
                  </div>
                  <Form.Item name="productUpdates" valuePropName="checked" style={{ margin: 0 }}>
                    <Switch />
                  </Form.Item>
                </div>
              </Form.Item>

              <Form.Item style={{ marginTop: 24 }}>
                <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                  Save Preferences
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <ApiOutlined />
              API Keys
            </span>
          }
          key="api"
        >
          <Card>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Title level={4}>API Access</Title>
                <Text type="secondary">
                  Manage API keys for programmatic access to SimpleIQ
                </Text>
              </div>

              <Button type="primary" icon={<PlusOutlined />}>
                Generate New API Key
              </Button>

              <div style={{ marginTop: 24 }}>
                <div style={{ padding: 16, background: '#f0f0f0', borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>Production API Key</Text>
                      <br />
                      <Text type="secondary" style={{ fontFamily: 'monospace' }}>
                        sk_live_...abc123
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Created: Jan 15, 2024 • Last used: 2 hours ago
                      </Text>
                    </div>
                    <Button danger size="small">
                      Revoke
                    </Button>
                  </div>
                </div>
              </div>
            </Space>
          </Card>
        </TabPane>

        <TabPane
          tab={
            <span>
              <TeamOutlined />
              Team
            </span>
          }
          key="team"
        >
          <Card>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Title level={4}>Team Members</Title>
                <Text type="secondary">
                  Invite and manage team members
                </Text>
              </div>

              <Button type="primary" icon={<PlusOutlined />}>
                Invite Team Member
              </Button>

              <div style={{ marginTop: 24 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Text strong>John Doe</Text> <Tag color="blue">Owner</Tag>
                        <br />
                        <Text type="secondary">john.doe@example.com</Text>
                      </div>
                    </div>
                  </div>
                  <div style={{ padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Text strong>Jane Smith</Text> <Tag>Admin</Tag>
                        <br />
                        <Text type="secondary">jane.smith@example.com</Text>
                      </div>
                      <Button size="small">Edit Role</Button>
                    </div>
                  </div>
                  <div style={{ padding: '12px 0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <Text strong>Bob Wilson</Text> <Tag>Viewer</Tag>
                        <br />
                        <Text type="secondary">bob.wilson@example.com</Text>
                      </div>
                      <Button size="small">Edit Role</Button>
                    </div>
                  </div>
                </Space>
              </div>
            </Space>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Settings;