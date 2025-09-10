import api from './api';

export interface DataSource {
  id: string;
  name: string;
  type: 'postgresql' | 'mysql' | 'sqlite' | 'mongodb' | 'bigquery' | 'snowflake' | 'rest_api' | 'csv' | 'google_sheets';
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  connection_string?: string;
  status: 'connected' | 'disconnected' | 'testing' | 'error';
  last_connected?: string;
  tables_count?: number;
  size?: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  tables?: Array<{ name: string; rows: number; size: string }>;
}

export interface DataSourceCreate {
  name: string;
  type: DataSource['type'];
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  connection_string?: string;
  description?: string;
}

export interface DataSourceUpdate {
  name?: string;
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  connection_string?: string;
  description?: string;
}

export interface ConnectionTestResponse {
  success: boolean;
  message: string;
  tables_count?: number;
  size?: string;
  tables?: Array<{ name: string; rows: number; size: string }>;
}

export interface UploadCSVResponse {
  id: string;
  name: string;
  type: 'csv';
  status: string;
  file_size: number;
  created_at: string;
}

class DataSourcesService {
  /**
   * Get all data sources
   */
  async getDataSources(skip = 0, limit = 100): Promise<DataSource[]> {
    const response = await api.get('/api/v1/data/sources', {
      params: { skip, limit }
    });
    return response.data;
  }

  /**
   * Create a new data source
   */
  async createDataSource(dataSource: DataSourceCreate): Promise<DataSource> {
    const response = await api.post('/api/v1/data/sources', dataSource);
    return response.data;
  }

  /**
   * Update an existing data source
   */
  async updateDataSource(id: string, dataSource: DataSourceUpdate): Promise<DataSource> {
    const response = await api.put(`/api/v1/data/sources/${id}`, dataSource);
    return response.data;
  }

  /**
   * Delete a data source
   */
  async deleteDataSource(id: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/v1/data/sources/${id}`);
    return response.data;
  }

  /**
   * Test connection to a data source
   */
  async testConnection(id: string): Promise<ConnectionTestResponse> {
    const response = await api.post(`/api/v1/data/sources/${id}/test`);
    return response.data;
  }

  /**
   * Trigger sync for a data source
   */
  async syncDataSource(id: string): Promise<{ message: string; job_id: string; status: string }> {
    const response = await api.post(`/api/v1/data/sources/${id}/sync`);
    return response.data;
  }

  /**
   * Upload a CSV file as a data source
   */
  async uploadCSV(file: File, name?: string): Promise<UploadCSVResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (name) {
      formData.append('name', name);
    }

    const response = await api.post('/api/v1/data/upload/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export default new DataSourcesService();