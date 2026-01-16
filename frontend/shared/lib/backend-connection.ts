/**
 * 后端连接状态管理
 */
import { useState, useEffect } from 'react';
import { api } from './api-client';

export interface BackendStatus {
  connected: boolean;
  loading: boolean;
  error: string | null;
}

export function useBackendConnection(): BackendStatus {
  // 暂时禁用 health check，直接假设后端已连接
  const [status] = useState<BackendStatus>({
    connected: true,  // 暂时假设后端已连接
    loading: false,
    error: null,
  });

  // 暂时注释掉所有 health check 逻辑
  // useEffect(() => {
  //   let mounted = true;
  //   let intervalId: NodeJS.Timeout;

  //   const checkConnection = async () => {
  //     try {
  //       await api.health();
  //       if (mounted) {
  //         setStatus({
  //           connected: true,
  //           loading: false,
  //           error: null,
  //         });
  //       }
  //     } catch (error: any) {
  //       if (mounted) {
  //         setStatus({
  //           connected: false,
  //           loading: false,
  //           error: error.message || 'Backend not available',
  //         });
  //       }
  //     }
  //   };

  //   // 立即检查一次
  //   checkConnection();

  //   // 每 30 秒检查一次（减少检查频率以降低输出）
  //   intervalId = setInterval(checkConnection, 30000);

  //   return () => {
  //     mounted = false;
  //     if (intervalId) {
  //       clearInterval(intervalId);
  //     }
  //   };
  // }, []);

  return status;
}

export default useBackendConnection;
