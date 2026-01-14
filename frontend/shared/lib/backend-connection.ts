/**
 * 后端连接状态管理
 */
import { useState, useEffect } from 'react';
import { api } from './api-client';

interface BackendStatus {
  connected: boolean;
  loading: boolean;
  error: string | null;
}

export function useBackendConnection(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>({
    connected: false,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;
    let intervalId: NodeJS.Timeout;

    const checkConnection = async () => {
      try {
        await api.health();
        if (mounted) {
          setStatus({
            connected: true,
            loading: false,
            error: null,
          });
        }
      } catch (error: any) {
        if (mounted) {
          setStatus({
            connected: false,
            loading: false,
            error: error.message || 'Backend not available',
          });
        }
      }
    };

    // 立即检查一次
    checkConnection();

    // 每 10 秒检查一次（增加检查间隔）
    intervalId = setInterval(checkConnection, 10000);

    return () => {
      mounted = false;
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, []);

  return status;
}

export default useBackendConnection;
