/**
 * Server-Sent Events (SSE) 客户端 - 用于实时获取任务进度
 */
export interface TaskProgress {
  task_id: string;
  status: string;
  progress: number;
  message: string;
  output_path?: string;
  error?: string;
}

type ProgressCallback = (data: TaskProgress) => void;
type ErrorCallback = (error: Error) => void;

export class SSEClient {
  private eventSource: EventSource | null = null;
  private taskId: string;
  private onProgress: ProgressCallback;
  private onError?: ErrorCallback;
  private baseURL: string;

  constructor(
    taskId: string,
    onProgress: ProgressCallback,
    onError?: ErrorCallback,
    baseURL: string = 'http://localhost:8000'
  ) {
    this.taskId = taskId;
    this.onProgress = onProgress;
    this.onError = onError;
    this.baseURL = baseURL;
  }

  connect(): void {
    if (this.eventSource) {
      return; // 已经连接
    }

    const url = `${this.baseURL}/api/tasks/${this.taskId}/stream`;
    this.eventSource = new EventSource(url);

    this.eventSource.onmessage = (event) => {
      try {
        const data: TaskProgress = JSON.parse(event.data);
        this.onProgress(data);
        
        // 如果任务完成、失败或取消，关闭连接
        if (['completed', 'failed', 'cancelled'].includes(data.status)) {
          this.disconnect();
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
        if (this.onError) {
          this.onError(error as Error);
        }
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      if (this.onError) {
        this.onError(new Error('SSE connection error'));
      }
      // 注意：EventSource 会自动重连，所以不需要手动重连
    };

    this.eventSource.onopen = () => {
      console.log('SSE connection opened');
    };
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }
}

