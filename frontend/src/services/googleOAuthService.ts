import api from './api';

export interface GoogleSheetsConnectionRequest {
  name: string;
  description?: string;
  spreadsheet_url: string;
  sheet_name?: string;
}

export interface GoogleSheetsConnectionResponse {
  data_source_id: string;
  auth_url: string;
  message: string;
}

export interface OAuthCallbackRequest {
  authorization_code: string;
  data_source_id: string;
}

export interface OAuthCallbackResponse {
  success: boolean;
  message: string;
  user_info?: {
    email: string;
    name: string;
    photo?: string;
  };
}

export interface GoogleAuthUrlResponse {
  auth_url: string;
  message: string;
}

export interface SheetsTestConnectionResponse {
  success: boolean;
  message: string;
  sheet_info?: {
    spreadsheet_id: string;
    sheet_name: string;
    columns: number;
    rows: number;
    sample_columns: string[];
  };
}

export interface DataPreviewResponse {
  data_source_id: string;
  schema: {
    columns: Array<{
      name: string;
      original_name: string;
      type: string;
      nullable: boolean;
      unique_count: number;
      null_count: number;
      null_percentage: number;
      sample_values: string[];
    }>;
    total_rows: number;
    spreadsheet_id: string;
    sheet_name: string;
  };
  data: {
    rows: Array<Record<string, any>>;
    count: number;
    limit: number;
    offset: number;
    has_more: boolean;
  };
  message: string;
}

export interface SchemaResponse {
  data_source_id: string;
  schema: {
    columns: Array<{
      name: string;
      original_name: string;
      type: string;
      nullable: boolean;
      unique_count: number;
      null_count: number;
      null_percentage: number;
      sample_values: string[];
    }>;
    row_count: number;
    spreadsheet_id: string;
    sheet_name: string;
    sheet_dimensions: {
      rows: number;
      columns: number;
    };
    last_updated: string | null;
  };
  message: string;
}

class GoogleOAuthService {
  /**
   * Create a new Google Sheets connection and get OAuth URL
   */
  async connectGoogleSheets(request: GoogleSheetsConnectionRequest): Promise<GoogleSheetsConnectionResponse> {
    const response = await api.post('/api/v1/google/sheets/connect', request);
    return response.data;
  }

  /**
   * Handle OAuth callback with authorization code
   */
  async handleOAuthCallback(request: OAuthCallbackRequest): Promise<OAuthCallbackResponse> {
    const response = await api.post('/api/v1/google/oauth/callback', request);
    return response.data;
  }

  /**
   * Get authorization URL for existing data source
   */
  async getAuthUrl(dataSourceId: string): Promise<GoogleAuthUrlResponse> {
    const response = await api.get(`/api/v1/google/auth-url/${dataSourceId}`);
    return response.data;
  }

  /**
   * Test Google Sheets connection
   */
  async testSheetsConnection(dataSourceId: string): Promise<SheetsTestConnectionResponse> {
    const response = await api.post(`/api/v1/google/sheets/${dataSourceId}/test-connection`);
    return response.data;
  }

  /**
   * Open OAuth window and handle the flow
   */
  async openOAuthWindow(authUrl: string): Promise<string> {
    return new Promise((resolve, reject) => {
      // Open OAuth window
      const popup = window.open(
        authUrl,
        'google-oauth',
        'width=600,height=700,scrollbars=yes,resizable=yes'
      );

      if (!popup) {
        reject(new Error('Failed to open OAuth window. Please allow popups for this site.'));
        return;
      }

      // Poll for the callback URL
      const checkClosed = setInterval(() => {
        try {
          if (popup.closed) {
            clearInterval(checkClosed);
            reject(new Error('OAuth window was closed by user'));
            return;
          }

          // Check if we can access the popup URL (same-origin)
          let currentUrl;
          try {
            currentUrl = popup.location.href;
          } catch (e) {
            // Cross-origin, can't access URL yet
            return;
          }

          // Check if we're on the callback page
          if (currentUrl && currentUrl.includes('/api/v1/google/callback')) {
            // Extract the authorization code from URL
            const urlParams = new URLSearchParams(new URL(currentUrl).search);
            const authorizationCode = urlParams.get('code');
            
            if (authorizationCode) {
              popup.close();
              clearInterval(checkClosed);
              resolve(authorizationCode);
            } else {
              popup.close();
              clearInterval(checkClosed);
              reject(new Error('Authorization failed - no code received'));
            }
          }
        } catch (e) {
          // Cross-origin error, continue polling
        }
      }, 1000);

      // Timeout after 5 minutes
      setTimeout(() => {
        if (!popup.closed) {
          popup.close();
        }
        clearInterval(checkClosed);
        reject(new Error('OAuth flow timed out'));
      }, 300000);
    });
  }

  /**
   * Complete Google Sheets OAuth flow
   */
  async completeGoogleSheetsOAuth(
    request: GoogleSheetsConnectionRequest
  ): Promise<{ dataSource: any; userInfo: any }> {
    try {
      // Step 1: Create connection and get auth URL
      const connectionResponse = await this.connectGoogleSheets(request);
      
      // Step 2: Open OAuth window and get authorization code
      const authorizationCode = await this.openOAuthWindow(connectionResponse.auth_url);
      
      // Step 3: Complete OAuth flow
      const callbackResponse = await this.handleOAuthCallback({
        authorization_code: authorizationCode,
        data_source_id: connectionResponse.data_source_id
      });

      if (!callbackResponse.success) {
        throw new Error(callbackResponse.message);
      }

      return {
        dataSource: { id: connectionResponse.data_source_id },
        userInfo: callbackResponse.user_info
      };
    } catch (error) {
      console.error('Google Sheets OAuth flow failed:', error);
      throw error;
    }
  }

  /**
   * Preview data from Google Sheets data source
   */
  async previewSheetsData(
    dataSourceId: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<DataPreviewResponse> {
    const response = await api.get(`/api/v1/google/sheets/${dataSourceId}/preview`, {
      params: { limit, offset }
    });
    return response.data;
  }

  /**
   * Get detailed schema information for Google Sheets data source
   */
  async getSheetsSchema(dataSourceId: string): Promise<SchemaResponse> {
    const response = await api.get(`/api/v1/google/sheets/${dataSourceId}/schema`);
    return response.data;
  }
}

export default new GoogleOAuthService();