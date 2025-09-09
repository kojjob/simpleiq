import React from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import {
  UserOutlined,
  DatabaseOutlined,
  LineChartOutlined,
  DashboardOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

const Dashboard: React.FC = () => {
  return (
    <div>
      <Title level={2}>Dashboard</Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Users"
              value={1128}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Data Sources"
              value={12}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Queries Today"
              value={93}
              prefix={<LineChartOutlined />}
              suffix={
                <span style={{ fontSize: 14, color: '#3f8600' }}>
                  <ArrowUpOutlined /> 12%
                </span>
              }
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Dashboards"
              value={8}
              prefix={<DashboardOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Query Activity" style={{ height: 400 }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: 300,
              color: '#999'
            }}>
              Chart placeholder - Will be implemented with chart library
            </div>
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="Recent Queries" style={{ height: 400 }}>
            <div style={{ color: '#666' }}>
              <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                Show me sales by region - 2 mins ago
              </div>
              <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                What are top products? - 15 mins ago
              </div>
              <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                Customer growth rate - 1 hour ago
              </div>
              <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                Revenue forecast - 2 hours ago
              </div>
              <div style={{ padding: '8px 0' }}>
                Inventory analysis - 3 hours ago
              </div>
            </div>
          </Card>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24}>
          <Card title="Data Source Status">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <div style={{ padding: 16, background: '#f6ffed', borderRadius: 4 }}>
                  <div style={{ color: '#52c41a', fontWeight: 'bold' }}>
                    PostgreSQL - Production
                  </div>
                  <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>
                    Connected • Last sync: 5 mins ago
                  </div>
                </div>
              </Col>
              <Col xs={24} sm={8}>
                <div style={{ padding: 16, background: '#f6ffed', borderRadius: 4 }}>
                  <div style={{ color: '#52c41a', fontWeight: 'bold' }}>
                    Google Sheets - Sales Data
                  </div>
                  <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>
                    Connected • Last sync: 1 hour ago
                  </div>
                </div>
              </Col>
              <Col xs={24} sm={8}>
                <div style={{ padding: 16, background: '#fff7e6', borderRadius: 4 }}>
                  <div style={{ color: '#fa8c16', fontWeight: 'bold' }}>
                    CSV Upload - Customer Data
                  </div>
                  <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>
                    Syncing • 45% complete
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;