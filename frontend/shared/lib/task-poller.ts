/**
 * 任务进度轮询器 - 作为 WebSocket 的备选方案
 */
import { api } from './api-client';

export interface TaskProgress {
  task_id: string;
  status: string;
  progress: number;
  message: string;
  output_path?: string;
}

type ProgressCallback = (data: TaskProgress) => void;
type ErrorCallback = (error: Error) => void;

export class TaskPoller {
  private taskId: string;
  private intervalId: NodeJS.Timeout | null = null;
  private pollInterval: number = 1000; // 1秒轮询一次
  private maxPollAttempts: number = 3600; // 最多轮询1小时（3600次）
  private pollAttempts: number = 0;
  private onProgress: ProgressCallback;
  private onError?: ErrorCallback;
  private isPolling: boolean = false;

  constructor(
    taskId: string,
    onProgress: ProgressCallback,
    onError?: ErrorCallback,
    pollInterval: number = 1000
  ) {
    this.taskId = taskId;
    this.onProgress = onProgress;
    this.onError = onError;
    this.pollInterval = pollInterval;
  }

  start(): void {
    if (this.isPolling) {
      return;
    }

    this.isPolling = true;
    this.pollAttempts = 0;

    const poll = async () => {
      if (!this.isPolling || this.pollAttempts >= this.maxPollAttempts) {
        this.stop();
        if (this.onError) {
          this.onError(new Error('Polling timeout or max attempts reached'));
        }
        return;
      }

      try {
        const task = await api.getTask(this.taskId);
        
        const progressData: TaskProgress = {
          task_id: this.taskId,
          status: task.status || 'running',
          progress: task.progress || 0,
          message: task.message || '',
          output_path: task.result?.output_path || task.output_path,
        };

        this.onProgress(progressData);

        // 如果任务完成或失败，停止轮询
        if (['completed', 'failed', 'cancelled'].includes(progressData.status)) {
          this.stop();
          return;
        }

        this.pollAttempts++;
      } catch (error: any) {
        console.error('Polling error:', error);
        // 如果是 404，任务可能不存在，停止轮询
        if (error.response?.status === 404) {
          this.stop();
          if (this.onError) {
            this.onError(new Error('Task not found'));
          }
          return;
        }
        // 其他错误继续轮询
        this.pollAttempts++;
      }

      // 继续轮询
      if (this.isPolling) {
        this.intervalId = setTimeout(poll, this.pollInterval);
      }
    };

    // 立即执行一次
    poll();
  }

  stop(): void {
    this.isPolling = false;
    if (this.intervalId) {
      clearTimeout(this.intervalId);
      this.intervalId = null;
    }
  }

  isActive(): boolean {
    return this.isPolling;
  }
}

