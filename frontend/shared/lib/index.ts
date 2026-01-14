// Export all shared libraries
export { apiClient, api, default as ApiClient } from './api-client';
export type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from './api-client';
export { wsClient, default as WebSocketClient } from './websocket-client';
export { backendConnection, useBackendConnection } from './backend-connection';
export type { BackendConnectionStatus } from './backend-connection';


