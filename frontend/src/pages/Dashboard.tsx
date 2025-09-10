import React from 'react';
import { Card, Typography, Row, Col } from 'antd';
import { DashboardOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: '24px', background: '#f0f2f5' }}>
      <Title level={2}>
        <DashboardOutlined /> Dashboard
      </Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#1890ff' }}>150</Title>
              <Paragraph>Total Queries</Paragraph>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#52c41a' }}>98.5%</Title>
              <Paragraph>Success Rate</Paragraph>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#fa8c16' }}>0.3s</Title>
              <Paragraph>Avg Response Time</Paragraph>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#722ed1' }}>12</Title>
              <Paragraph>Active Data Sources</Paragraph>
            </div>
          </Card>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card title="Welcome to SimpleIQ Dashboard">
            <Paragraph>
              This is your analytics dashboard. Here you can monitor query performance, 
              view data source status, and get insights into your data usage patterns.
            </Paragraph>
            <Paragraph>
              🚀 <strong>Tip:</strong> Use the Query page to run natural language queries against your data sources.
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;