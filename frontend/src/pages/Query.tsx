import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  Row, 
  Col, 
  Typography, 
  Space, 
  Table, 
  Select, 
  message, 
  Tabs, 
  Tag, 
  Tooltip, 
  Switch, 
  Divider, 
  Progress, 
  Badge, 
  List, 
  Avatar,
  Dropdown,
  Menu,
  Modal,
  Form,
  TreeSelect,
  Slider,
  DatePicker,
  Statistic,
  Empty
} from 'antd';
import {
  SendOutlined,
  HistoryOutlined,
  SaveOutlined,
  ShareAltOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  CodeOutlined,
  EyeOutlined,
  FilterOutlined,
  SortAscendingOutlined,
  GroupOutlined,
  CalculatorOutlined,
  TableOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  SettingOutlined,
  BulbOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  ApiOutlined
} from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

// Mock data for the visual query builder
const mockTables = [
  {
    name: 'users',
    columns: [
      { name: 'id', type: 'integer', isPrimaryKey: true },
      { name: 'name', type: 'varchar', nullable: false },
      { name: 'email', type: 'varchar', nullable: false },
      { name: 'created_at', type: 'timestamp', nullable: false },
      { name: 'status', type: 'varchar', nullable: true },
      { name: 'age', type: 'integer', nullable: true }
    ]
  },
  {
    name: 'orders',
    columns: [
      { name: 'id', type: 'integer', isPrimaryKey: true },
      { name: 'user_id', type: 'integer', nullable: false },
      { name: 'product_name', type: 'varchar', nullable: false },
      { name: 'amount', type: 'decimal', nullable: false },
      { name: 'order_date', type: 'timestamp', nullable: false },
      { name: 'status', type: 'varchar', nullable: false }
    ]
  },
  {
    name: 'products',
    columns: [
      { name: 'id', type: 'integer', isPrimaryKey: true },
      { name: 'name', type: 'varchar', nullable: false },
      { name: 'category', type: 'varchar', nullable: false },
      { name: 'price', type: 'decimal', nullable: false },
      { name: 'stock', type: 'integer', nullable: false }
    ]
  }
];

const suggestedQueries = [
  { 
    category: 'Sales Analytics',
    queries: [
      'Show me total sales by month for the last year',
      'What are the top 10 best-selling products?',
      'Compare sales performance by region',
      'Show customer acquisition trends'
    ]
  },
  {
    category: 'Customer Insights',
    queries: [
      'Who are our most valuable customers?',
      'Customer retention rate analysis',
      'Average order value by customer segment',
      'Customer geographic distribution'
    ]
  },
  {
    category: 'Operational',
    queries: [
      'Current inventory levels by product',
      'Orders pending fulfillment',
      'Daily active users trend',
      'Revenue forecast for next quarter'
    ]
  }
];

const Query: React.FC = () => {
  const [activeTab, setActiveTab] = useState('natural');
  const [queryText, setQueryText] = useState('');
  const [sqlQuery, setSqlQuery] = useState('SELECT * FROM users LIMIT 10;');
  const [selectedDataSource, setSelectedDataSource] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<any>(null);
  const [isRealTime, setIsRealTime] = useState(false);
  const [queryExecutionTime, setQueryExecutionTime] = useState(0);
  
  // Visual Query Builder State
  const [selectedTable, setSelectedTable] = useState('');
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [whereConditions, setWhereConditions] = useState<any[]>([]);
  const [orderBy, setOrderBy] = useState<any>({});
  const [groupBy, setGroupBy] = useState<string[]>([]);
  const [limit, setLimit] = useState(100);

  const [executionHistory, setExecutionHistory] = useState([
    { id: 1, query: 'Show me total sales by region', time: '2 min ago', duration: '0.23s', status: 'success', rows: 1542 },
    { id: 2, query: 'Top 10 customers by revenue', time: '5 min ago', duration: '0.45s', status: 'success', rows: 10 },
    { id: 3, query: 'Monthly growth analysis', time: '8 min ago', duration: '1.2s', status: 'warning', rows: 365 },
  ]);

  // Simulate real-time query execution
  useEffect(() => {
    if (isRealTime && queryResult) {
      const interval = setInterval(() => {
        // Simulate new data
        setQueryResult(prev => ({
          ...prev,
          data: prev.data.map((row: any) => ({
            ...row,
            sales: '$' + (Math.random() * 1000000 + 500000).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ','),
            growth: (Math.random() * 20 - 5).toFixed(1) + '%'
          }))
        }));
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isRealTime, queryResult]);

  const handleRunQuery = async (customQuery?: string) => {
    const query = customQuery || queryText;
    if (!query.trim()) {
      message.warning('Please enter a query');
      return;
    }

    setIsLoading(true);
    const startTime = Date.now();
    
    // Simulate API call with realistic delay
    setTimeout(() => {
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      setQueryExecutionTime(parseFloat(duration));
      
      setQueryResult({
        columns: [
          { title: 'Region', dataIndex: 'region', key: 'region', sorter: true },
          { title: 'Sales', dataIndex: 'sales', key: 'sales', sorter: true },
          { title: 'Growth', dataIndex: 'growth', key: 'growth', sorter: true, 
            render: (text: string) => {
              const isPositive = parseFloat(text) > 0;
              return <Tag color={isPositive ? 'green' : 'red'}>{text}</Tag>;
            }
          },
          { title: 'Customers', dataIndex: 'customers', key: 'customers', sorter: true },
          { title: 'Avg Order', dataIndex: 'avgOrder', key: 'avgOrder', sorter: true },
        ],
        data: [
          { key: '1', region: 'North America', sales: '$1,234,567', growth: '+12.3%', customers: '2,456', avgOrder: '$502' },
          { key: '2', region: 'Europe', sales: '$987,654', growth: '+8.7%', customers: '1,823', avgOrder: '$541' },
          { key: '3', region: 'Asia Pacific', sales: '$756,432', growth: '+15.2%', customers: '1,567', avgOrder: '$483' },
          { key: '4', region: 'Latin America', sales: '$432,109', growth: '+5.1%', customers: '892', avgOrder: '$484' },
          { key: '5', region: 'Middle East', sales: '$345,678', growth: '+9.8%', customers: '654', avgOrder: '$529' },
        ]
      });
      setIsLoading(false);
      message.success(`Query executed successfully in ${duration}s!`);
      
      // Add to execution history
      setExecutionHistory(prev => [{
        id: Date.now(),
        query: query.substring(0, 50) + (query.length > 50 ? '...' : ''),
        time: 'Just now',
        duration: duration + 's',
        status: 'success',
        rows: 5
      }, ...prev.slice(0, 9)]);
    }, 800 + Math.random() * 1200);
  };

  const generateSQLFromVisual = () => {
    if (!selectedTable || selectedColumns.length === 0) return '';
    
    let sql = `SELECT ${selectedColumns.join(', ')} FROM ${selectedTable}`;
    
    if (whereConditions.length > 0) {
      const conditions = whereConditions.map(c => `${c.column} ${c.operator} '${c.value}'`).join(' AND ');
      sql += ` WHERE ${conditions}`;
    }
    
    if (groupBy.length > 0) {
      sql += ` GROUP BY ${groupBy.join(', ')}`;
    }
    
    if (orderBy.column) {
      sql += ` ORDER BY ${orderBy.column} ${orderBy.direction || 'ASC'}`;
    }
    
    sql += ` LIMIT ${limit};`;
    
    return sql;
  };

  const addWhereCondition = () => {
    setWhereConditions([...whereConditions, { column: '', operator: '=', value: '' }]);
  };

  const updateWhereCondition = (index: number, field: string, value: any) => {
    const updated = [...whereConditions];
    updated[index][field] = value;
    setWhereConditions(updated);
  };

  const removeWhereCondition = (index: number) => {
    setWhereConditions(whereConditions.filter((_, i) => i !== index));
  };

  const queryHistoryColumns = [
    {
      title: 'Query',
      dataIndex: 'query',
      key: 'query',
      ellipsis: true,
      render: (text: string) => <Text code style={{ fontSize: '11px' }}>{text}</Text>
    },
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
      width: 100,
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      width: 80,
      render: (duration: string) => (
        <Tag color={parseFloat(duration) > 1 ? 'orange' : 'green'}>{duration}</Tag>
      )
    },
    {
      title: 'Rows',
      dataIndex: 'rows',
      key: 'rows',
      width: 80,
      render: (rows: number) => rows.toLocaleString()
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => (
        <Badge status={status === 'success' ? 'success' : 'warning'} />
      )
    }
  ];

  const exportOptions = [
    { key: 'csv', label: 'Export to CSV', icon: <FileTextOutlined /> },
    { key: 'excel', label: 'Export to Excel', icon: <TableOutlined /> },
    { key: 'json', label: 'Export to JSON', icon: <CodeOutlined /> },
    { key: 'pdf', label: 'Export to PDF', icon: <FileTextOutlined /> },
  ];

  const visualizationOptions = [
    { key: 'bar', label: 'Bar Chart', icon: <BarChartOutlined /> },
    { key: 'line', label: 'Line Chart', icon: <LineChartOutlined /> },
    { key: 'pie', label: 'Pie Chart', icon: <PieChartOutlined /> },
    { key: 'table', label: 'Data Table', icon: <TableOutlined /> },
  ];

  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <RocketOutlined /> Query Builder
        </Title>
        <Paragraph type="secondary">
          Build powerful queries with our intelligent query interface - Natural Language, Visual Builder, or SQL Editor
        </Paragraph>
      </div>

      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          size="large"
          tabBarExtraContent={
            <Space>
              <Tooltip title="Real-time updates">
                <Switch 
                  checked={isRealTime}
                  onChange={setIsRealTime}
                  checkedChildren={<ThunderboltOutlined />}
                  unCheckedChildren={<PauseCircleOutlined />}
                />
              </Tooltip>
              <Select value={selectedDataSource} onChange={setSelectedDataSource} style={{ width: 200 }}>
                <Option value="all"><DatabaseOutlined /> All Sources</Option>
                <Option value="postgres">PostgreSQL - Production</Option>
                <Option value="mysql">MySQL - Analytics</Option>
                <Option value="sheets">Google Sheets - Sales</Option>
              </Select>
            </Space>
          }
        >
          {/* Natural Language Query Tab */}
          <TabPane 
            tab={
              <span>
                <BulbOutlined />
                Natural Language
              </span>
            } 
            key="natural"
          >
            <Row gutter={[24, 24]}>
              <Col xs={24} lg={16}>
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <Card size="small" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                    <Paragraph style={{ color: '#fff', margin: 0 }}>
                      <BulbOutlined /> Ask questions about your data in plain English. Our AI understands complex queries and relationships.
                    </Paragraph>
                  </Card>

                  <div>
                    <Text strong style={{ fontSize: '16px' }}>What would you like to know?</Text>
                    <TextArea
                      value={queryText}
                      onChange={(e) => setQueryText(e.target.value)}
                      placeholder="Example: Show me the total sales by region for customers who ordered more than $1000 in the last quarter"
                      rows={4}
                      style={{ marginTop: 12, fontSize: '14px' }}
                      onPressEnter={(e) => {
                        if (e.shiftKey) return;
                        e.preventDefault();
                        handleRunQuery();
                      }}
                    />
                  </div>

                  <Row gutter={[12, 12]}>
                    <Col>
                      <Button
                        type="primary"
                        icon={<SendOutlined />}
                        onClick={() => handleRunQuery()}
                        loading={isLoading}
                        size="large"
                        style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}
                      >
                        Ask AI
                      </Button>
                    </Col>
                    <Col>
                      <Button icon={<SaveOutlined />} size="large">Save Query</Button>
                    </Col>
                    <Col>
                      <Button icon={<ShareAltOutlined />} size="large">Share</Button>
                    </Col>
                    <Col>
                      <Button icon={<HistoryOutlined />} size="large">History</Button>
                    </Col>
                  </Row>

                  {queryExecutionTime > 0 && (
                    <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
                      <Statistic 
                        title="Execution Time" 
                        value={queryExecutionTime} 
                        suffix="s" 
                        precision={2}
                        valueStyle={{ color: '#52c41a' }}
                      />
                      <Statistic 
                        title="Rows Returned" 
                        value={queryResult?.data?.length || 0} 
                        valueStyle={{ color: '#1890ff' }}
                      />
                      {isRealTime && (
                        <Badge status="processing" text="Live Updates Active" />
                      )}
                    </div>
                  )}
                </Space>
              </Col>

              <Col xs={24} lg={8}>
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <Card 
                    title={<><BulbOutlined /> Suggested Queries</>} 
                    size="small"
                    bodyStyle={{ padding: '12px' }}
                  >
                    {suggestedQueries.map((category, idx) => (
                      <div key={idx} style={{ marginBottom: '16px' }}>
                        <Text strong style={{ color: '#1890ff', fontSize: '12px' }}>
                          {category.category.toUpperCase()}
                        </Text>
                        <div style={{ marginTop: '8px' }}>
                          {category.queries.map((query, qIdx) => (
                            <div
                              key={qIdx}
                              style={{
                                padding: '6px 8px',
                                cursor: 'pointer',
                                borderRadius: '4px',
                                fontSize: '12px',
                                transition: 'all 0.2s',
                                marginBottom: '4px'
                              }}
                              onClick={() => setQueryText(query)}
                              onMouseEnter={(e) => e.currentTarget.style.background = '#f0f0f0'}
                              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            >
                              {query}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </Card>

                  <Card 
                    title={<><ApiOutlined /> Query Tips</>} 
                    size="small"
                    bodyStyle={{ padding: '12px' }}
                  >
                    <Space direction="vertical" size="small">
                      <Text style={{ fontSize: '12px' }}>• Use specific time ranges: "last quarter", "past 30 days"</Text>
                      <Text style={{ fontSize: '12px' }}>• Ask for comparisons: "compare X vs Y"</Text>
                      <Text style={{ fontSize: '12px' }}>• Request specific metrics: "top 10", "average", "total"</Text>
                      <Text style={{ fontSize: '12px' }}>• Filter by conditions: "customers who", "products where"</Text>
                    </Space>
                  </Card>
                </Space>
              </Col>
            </Row>
          </TabPane>

          {/* Visual Query Builder Tab */}
          <TabPane 
            tab={
              <span>
                <FilterOutlined />
                Visual Builder
              </span>
            } 
            key="visual"
          >
            <Row gutter={[24, 24]}>
              <Col xs={24} lg={12}>
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <Card title="1. Select Table" size="small">
                    <Select
                      value={selectedTable}
                      onChange={setSelectedTable}
                      style={{ width: '100%' }}
                      placeholder="Choose a table"
                      size="large"
                    >
                      {mockTables.map(table => (
                        <Option key={table.name} value={table.name}>
                          <TableOutlined /> {table.name}
                        </Option>
                      ))}
                    </Select>
                  </Card>

                  {selectedTable && (
                    <Card title="2. Select Columns" size="small">
                      <Select
                        mode="multiple"
                        value={selectedColumns}
                        onChange={setSelectedColumns}
                        style={{ width: '100%' }}
                        placeholder="Choose columns"
                        size="large"
                      >
                        {mockTables.find(t => t.name === selectedTable)?.columns.map(col => (
                          <Option key={col.name} value={col.name}>
                            <Tag color={col.type === 'integer' ? 'blue' : col.type === 'varchar' ? 'green' : 'orange'}>
                              {col.type}
                            </Tag>
                            {col.name}
                            {col.isPrimaryKey && <Tag color="red" size="small">PK</Tag>}
                          </Option>
                        ))}
                      </Select>
                    </Card>
                  )}

                  <Card 
                    title="3. Add Filters (WHERE)" 
                    size="small"
                    extra={
                      <Button size="small" onClick={addWhereCondition}>
                        + Add Filter
                      </Button>
                    }
                  >
                    {whereConditions.map((condition, index) => (
                      <Row key={index} gutter={[8, 8]} style={{ marginBottom: '8px' }}>
                        <Col span={8}>
                          <Select
                            value={condition.column}
                            onChange={(value) => updateWhereCondition(index, 'column', value)}
                            placeholder="Column"
                            style={{ width: '100%' }}
                          >
                            {mockTables.find(t => t.name === selectedTable)?.columns.map(col => (
                              <Option key={col.name} value={col.name}>{col.name}</Option>
                            ))}
                          </Select>
                        </Col>
                        <Col span={6}>
                          <Select
                            value={condition.operator}
                            onChange={(value) => updateWhereCondition(index, 'operator', value)}
                            style={{ width: '100%' }}
                          >
                            <Option value="=">=</Option>
                            <Option value="!=">!=</Option>
                            <Option value=">">&gt;</Option>
                            <Option value="<">&lt;</Option>
                            <Option value=">=">&gt;=</Option>
                            <Option value="<=">&lt;=</Option>
                            <Option value="LIKE">LIKE</Option>
                          </Select>
                        </Col>
                        <Col span={8}>
                          <Input
                            value={condition.value}
                            onChange={(e) => updateWhereCondition(index, 'value', e.target.value)}
                            placeholder="Value"
                          />
                        </Col>
                        <Col span={2}>
                          <Button 
                            size="small" 
                            danger 
                            onClick={() => removeWhereCondition(index)}
                          >
                            ×
                          </Button>
                        </Col>
                      </Row>
                    ))}
                  </Card>

                  <Row gutter={[12, 12]}>
                    <Col span={12}>
                      <Card title="4. Group By" size="small">
                        <Select
                          mode="multiple"
                          value={groupBy}
                          onChange={setGroupBy}
                          style={{ width: '100%' }}
                          placeholder="Group columns"
                        >
                          {mockTables.find(t => t.name === selectedTable)?.columns.map(col => (
                            <Option key={col.name} value={col.name}>{col.name}</Option>
                          ))}
                        </Select>
                      </Card>
                    </Col>
                    <Col span={12}>
                      <Card title="5. Order By" size="small">
                        <Row gutter={[8, 8]}>
                          <Col span={16}>
                            <Select
                              value={orderBy.column}
                              onChange={(value) => setOrderBy({...orderBy, column: value})}
                              style={{ width: '100%' }}
                              placeholder="Column"
                            >
                              {mockTables.find(t => t.name === selectedTable)?.columns.map(col => (
                                <Option key={col.name} value={col.name}>{col.name}</Option>
                              ))}
                            </Select>
                          </Col>
                          <Col span={8}>
                            <Select
                              value={orderBy.direction}
                              onChange={(value) => setOrderBy({...orderBy, direction: value})}
                              style={{ width: '100%' }}
                            >
                              <Option value="ASC">ASC</Option>
                              <Option value="DESC">DESC</Option>
                            </Select>
                          </Col>
                        </Row>
                      </Card>
                    </Col>
                  </Row>

                  <Card title="6. Limit Results" size="small">
                    <Row align="middle" gutter={[16, 16]}>
                      <Col span={16}>
                        <Slider
                          min={1}
                          max={1000}
                          value={limit}
                          onChange={setLimit}
                          marks={{
                            1: '1',
                            100: '100',
                            500: '500',
                            1000: '1K'
                          }}
                        />
                      </Col>
                      <Col span={8}>
                        <Input
                          type="number"
                          value={limit}
                          onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
                          addonBefore="Limit"
                        />
                      </Col>
                    </Row>
                  </Card>
                </Space>
              </Col>

              <Col xs={24} lg={12}>
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <Card 
                    title="Generated SQL Query" 
                    size="small"
                    extra={
                      <Button 
                        type="primary" 
                        icon={<PlayCircleOutlined />}
                        onClick={() => handleRunQuery(generateSQLFromVisual())}
                        loading={isLoading}
                        disabled={!selectedTable || selectedColumns.length === 0}
                      >
                        Execute
                      </Button>
                    }
                  >
                    <div style={{ 
                      background: '#f6f8fa', 
                      border: '1px solid #d1d9e0', 
                      borderRadius: '6px',
                      padding: '12px',
                      minHeight: '120px',
                      fontFamily: 'Monaco, Consolas, monospace',
                      fontSize: '12px',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {generateSQLFromVisual() || 'Select a table and columns to generate SQL...'}
                    </div>
                  </Card>

                  {selectedTable && (
                    <Card title={`Table: ${selectedTable}`} size="small">
                      <List
                        size="small"
                        dataSource={mockTables.find(t => t.name === selectedTable)?.columns}
                        renderItem={(column: any) => (
                          <List.Item style={{ padding: '4px 0' }}>
                            <Space>
                              <Tag color={column.type === 'integer' ? 'blue' : column.type === 'varchar' ? 'green' : 'orange'}>
                                {column.type}
                              </Tag>
                              <Text strong>{column.name}</Text>
                              {column.isPrimaryKey && <Tag color="red" size="small">PRIMARY KEY</Tag>}
                              {!column.nullable && <Tag size="small">NOT NULL</Tag>}
                            </Space>
                          </List.Item>
                        )}
                      />
                    </Card>
                  )}
                </Space>
              </Col>
            </Row>
          </TabPane>

          {/* SQL Editor Tab */}
          <TabPane 
            tab={
              <span>
                <CodeOutlined />
                SQL Editor
              </span>
            } 
            key="sql"
          >
            <div style={{ height: '600px' }}>
              <PanelGroup direction="vertical">
                <Panel defaultSize={60} minSize={30}>
                  <Card 
                    title="SQL Editor" 
                    size="small"
                    style={{ height: '100%' }}
                    bodyStyle={{ padding: 0, height: 'calc(100% - 57px)' }}
                    extra={
                      <Space>
                        <Button 
                          type="primary" 
                          icon={<PlayCircleOutlined />}
                          onClick={() => handleRunQuery(sqlQuery)}
                          loading={isLoading}
                        >
                          Execute (Ctrl+Enter)
                        </Button>
                        <Button icon={<SaveOutlined />}>Save</Button>
                        <Button icon={<ShareAltOutlined />}>Share</Button>
                      </Space>
                    }
                  >
                    <Editor
                      height="100%"
                      defaultLanguage="sql"
                      value={sqlQuery}
                      onChange={(value) => setSqlQuery(value || '')}
                      theme="vs-dark"
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        wordWrap: 'on',
                        lineNumbers: 'on',
                        folding: true,
                        autoIndent: 'full',
                        formatOnPaste: true,
                        formatOnType: true,
                      }}
                      onMount={(editor) => {
                        editor.addCommand(2048 | 3, () => {
                          handleRunQuery(sqlQuery);
                        });
                      }}
                    />
                  </Card>
                </Panel>
                
                <PanelResizeHandle style={{ height: '4px', background: '#f0f0f0' }} />
                
                <Panel defaultSize={40} minSize={20}>
                  <Card 
                    title="Query Results" 
                    size="small"
                    style={{ height: '100%' }}
                    bodyStyle={{ padding: '12px', height: 'calc(100% - 57px)', overflow: 'auto' }}
                  >
                    {queryResult ? (
                      <Table
                        columns={queryResult.columns}
                        dataSource={queryResult.data}
                        pagination={{ pageSize: 10 }}
                        size="small"
                        scroll={{ x: 800 }}
                      />
                    ) : (
                      <Empty description="Run a query to see results" />
                    )}
                  </Card>
                </Panel>
              </PanelGroup>
            </div>
          </TabPane>
        </Tabs>

        {/* Query Results Section */}
        {queryResult && activeTab !== 'sql' && (
          <div style={{ marginTop: '24px' }}>
            <Card 
              title={
                <Space>
                  <TableOutlined />
                  <Text strong>Query Results</Text>
                  <Badge count={queryResult.data.length} style={{ backgroundColor: '#52c41a' }} />
                  {isRealTime && <Badge status="processing" text="Live" />}
                </Space>
              }
              extra={
                <Space>
                  <Dropdown
                    overlay={
                      <Menu>
                        {exportOptions.map(option => (
                          <Menu.Item key={option.key} icon={option.icon}>
                            {option.label}
                          </Menu.Item>
                        ))}
                      </Menu>
                    }
                  >
                    <Button icon={<DownloadOutlined />}>Export</Button>
                  </Dropdown>
                  <Dropdown
                    overlay={
                      <Menu>
                        {visualizationOptions.map(option => (
                          <Menu.Item key={option.key} icon={option.icon}>
                            {option.label}
                          </Menu.Item>
                        ))}
                      </Menu>
                    }
                  >
                    <Button icon={<BarChartOutlined />}>Visualize</Button>
                  </Dropdown>
                  <Button icon={<ShareAltOutlined />}>Share</Button>
                </Space>
              }
            >
              <Table
                columns={queryResult.columns}
                dataSource={queryResult.data}
                pagination={{ 
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`
                }}
                scroll={{ x: 800 }}
                size="small"
              />
            </Card>
          </div>
        )}

        {/* Query History Section */}
        <div style={{ marginTop: '24px' }}>
          <Card 
            title={
              <Space>
                <HistoryOutlined />
                <Text strong>Execution History</Text>
              </Space>
            }
            size="small"
          >
            <Table
              columns={queryHistoryColumns}
              dataSource={executionHistory}
              pagination={false}
              size="small"
            />
          </Card>
        </div>
      </Card>
    </div>
  );
};

export default Query;