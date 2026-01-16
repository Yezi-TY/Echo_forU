/**
 * API 客户端封装
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        // 如果是 FormData，删除 Content-Type 让浏览器自动设置（包括 boundary）
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type'];
        }
        // 可以在这里添加认证 token 等
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        // 统一错误处理
        if (error.response) {
          // 服务器返回了错误状态码
          const { status, data } = error.response;
          console.error(`API Error ${status}:`, data);
        } else if (error.request) {
          // 请求已发出但没有收到响应
          console.error('Network Error:', error.message);
        } else {
          // 其他错误
          console.error('Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // GET 请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  // POST 请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  // PUT 请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  // DELETE 请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // 文件上传
  async uploadFile(
    url: string,
    file: File,
    fileType: string = 'prompt',
    onProgress?: (progress: number) => void
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onProgress(progress);
        }
      },
    });

    return response.data;
  }
}

// 创建默认实例
export const apiClient = new ApiClient();

// 导出类型
export type { AxiosInstance, AxiosRequestConfig, AxiosResponse };

// API 方法
export const api = {
  // 健康检查（使用更长的超时时间）
  health: () => apiClient.get('/api/health', { timeout: 60000 }), // 60秒超时
  version: () => apiClient.get('/api/version'),

  // 硬件
  getHardwareInfo: () => apiClient.get('/api/hardware/info'),
  estimateHardwarePressure: (params: {
    model_size_gb?: number;
    batch_size?: number;
    precision?: string;
  }) => apiClient.get('/api/hardware/estimate', { params }),
  getOptimizationConfig: (model_size_gb?: number) =>
    apiClient.post('/api/hardware/optimize', { model_size_gb }),
  getRealtimeStats: () => apiClient.get('/api/hardware/stats'),

  // 模型
  getModelStatus: () => apiClient.get('/api/models/status'),
  downloadModel: (modelType: string) =>
    apiClient.post('/api/models/download', { model_type: modelType }),
  getHardwareRequirements: (modelType?: string, precision?: string) =>
    apiClient.get('/api/models/requirements', {
      params: { model_type: modelType, precision },
    }),

  // 任务
  createTask: (taskType: string, params: any) =>
    apiClient.post('/api/tasks/create', { task_type: taskType, params }),
  getTask: (taskId: string) => apiClient.get(`/api/tasks/${taskId}`),
  getAllTasks: (status?: string) =>
    apiClient.get('/api/tasks', { params: { status } }),
  cancelTask: (taskId: string) => apiClient.post(`/api/tasks/${taskId}/cancel`),

  // 生成 - 等待响应获取 task_id，然后通过轮询查询进度
  generateMusic: (data: {
    song_name: string;
    lyrics: string;
    style_prompt?: string;
    style_audio?: File;
    precision?: string;
    batch_size?: number;
  }): Promise<{ task_id: string }> => {
    const formData = new FormData();
    formData.append('song_name', data.song_name);
    formData.append('lyrics', data.lyrics);
    if (data.style_prompt) {
      formData.append('style_prompt', data.style_prompt);
    }
    if (data.style_audio) {
      formData.append('style_audio', data.style_audio);
    }
    formData.append('precision', data.precision || 'fp16');
    formData.append('batch_size', String(data.batch_size || 1));

    return apiClient.post('/api/generate', formData, { timeout: 60000 }).then((response) => {
      if (!response || !response.task_id) {
        throw new Error(`Invalid response: ${JSON.stringify(response)}`);
      }
      
      return response;
    });
  },

  // 历史记录
  getHistory: (params?: { limit?: number; offset?: number; search?: string }) =>
    apiClient.get('/api/history', { params }),
  getHistoryById: (historyId: string) =>
    apiClient.get(`/api/history/${historyId}`),
  deleteHistory: (historyId: string) =>
    apiClient.delete(`/api/history/${historyId}`),

  // 配置
  getConfig: (key?: string) =>
    apiClient.get('/api/config', { params: { key } }),
  updateConfig: (key: string, value: any) =>
    apiClient.put('/api/config', { key, value }),
  updateConfigBulk: (updates: Record<string, any>) =>
    apiClient.put('/api/config/bulk', updates),

  // 文件上传
  uploadFile: (file: File, fileType: string = 'prompt', onProgress?: (progress: number) => void) =>
    apiClient.uploadFile('/api/upload', file, fileType, onProgress),
};

export default apiClient;

