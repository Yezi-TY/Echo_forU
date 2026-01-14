/**
 * WebSocket 客户端
 */
type ProgressCallback = (data: {
  task_id: string;
  status: string;
  progress: number;
  message: string;
}) => void;

type ErrorCallback = (error: Error) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(baseURL: string = 'ws://localhost:8000') {
    this.url = baseURL;
  }

  connect(
    taskId: string,
    onProgress: ProgressCallback,
    onError?: ErrorCallback
  ): void {
    const wsUrl = `${this.url}/api/tasks/${taskId}/progress`;
    
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onProgress(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
          if (onError) {
            onError(error as Error);
          }
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) {
          onError(new Error('WebSocket connection error'));
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.ws = null;
        
        // 尝试重连（如果任务还在进行中）
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
            this.connect(taskId, onProgress, onError);
          }, this.reconnectDelay * this.reconnectAttempts);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// 创建默认实例
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
export const wsClient = new WebSocketClient(WS_BASE_URL);

export default WebSocketClient;

