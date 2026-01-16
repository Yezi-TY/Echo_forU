'use client';

import React, { useState, useEffect } from 'react';
import {
  Layout,
  StepIndicator,
  LyricsEditor,
  StylePromptInput,
  GenerationParams,
  GenerateButton,
  ProgressCard,
  AudioPreview,
  ErrorAlert,
  LoadingBackdrop,
} from '@music-gen-ui/shared/components';
import { Box, Card, CardContent } from '@mui/material';
import { api, wsClient, useBackendConnection, TaskPoller, SSEClient } from '@music-gen-ui/shared/lib';
import '@music-gen-ui/shared/lib/i18n/i18n'; // Initialize i18n

const STORAGE_KEY = 'music-gen-ui-form-state';

export default function Home() {
  // 使用默认值初始化，避免服务器端和客户端不一致
  const [lyrics, setLyrics] = useState('');
  const [stylePrompt, setStylePrompt] = useState('');
  const [styleAudio, setStyleAudio] = useState<File | null>(null);
  const [precision, setPrecision] = useState<'fp32' | 'fp16' | 'int8'>('fp16');
  const [batchSize, setBatchSize] = useState(1);
  const [maxDuration, setMaxDuration] = useState(300);
  const [mounted, setMounted] = useState(false);

  // 在客户端挂载后从 localStorage 恢复状态
  useEffect(() => {
    setMounted(true);
    
    // 从 localStorage 恢复状态
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.lyrics) setLyrics(parsed.lyrics);
        if (parsed.stylePrompt) setStylePrompt(parsed.stylePrompt);
        if (parsed.precision) setPrecision(parsed.precision);
        if (parsed.batchSize) setBatchSize(parsed.batchSize);
        if (parsed.maxDuration) setMaxDuration(parsed.maxDuration);
      }
    } catch (error) {
      console.error('Failed to load saved state:', error);
    }
  }, []);

  // 保存状态到 localStorage（只在客户端挂载后保存）
  useEffect(() => {
    if (mounted && typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          lyrics,
          stylePrompt,
          precision,
          batchSize,
          maxDuration,
        }));
      } catch (error) {
        console.error('Failed to save state:', error);
      }
    }
  }, [mounted, lyrics, stylePrompt, precision, batchSize, maxDuration]);
  
  const [generating, setGenerating] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('pending');
  const [message, setMessage] = useState('');
  const [outputUrl, setOutputUrl] = useState<string | null>(null);
  
  const [error, setError] = useState<string | null>(null);
  const [showError, setShowError] = useState(false);

  const backendStatus = useBackendConnection();
  const steps = ['generation.step1', 'generation.step2', 'generation.step3'];

  useEffect(() => {
    if (!taskId) {
      return;
    }

    console.log(`[Progress] Starting progress tracking for task: ${taskId}`);
    
    let poller: TaskPoller | null = null;
    let sseClient: SSEClient | null = null;
    let wsClientInstance: ReturnType<typeof wsClient.connect> | null = null;
    let activeMethod: 'sse' | 'ws' | 'poll' | null = null;

    const updateProgress = (data: { progress?: number; status?: string; message?: string; output_path?: string }) => {
      console.log(`[Progress] Update:`, data);
      
      if (data.progress !== undefined) {
        setProgress(data.progress);
      }
      if (data.status) {
        setStatus(data.status);
      }
      if (data.message !== undefined) {
        setMessage(data.message);
      }
      
      if (data.status === 'completed') {
        console.log(`[Progress] Task completed: ${taskId}`);
        setGenerating(false);
        
        // 3. 任务完成时，通过 output_path 获取成品音乐
        if (data.output_path) {
          console.log(`[Progress] Output file path: ${data.output_path}`);
          // 将后端绝对路径转换为前端 API 路由 URL
          setOutputUrl(`/api/audio?path=${encodeURIComponent(data.output_path)}`);
        } else {
          console.warn(`[Progress] Task completed but no output_path provided`);
        }
        
        // 清理所有连接
        if (sseClient) sseClient.disconnect();
        if (wsClientInstance) wsClientInstance.disconnect();
        if (poller) poller.stop();
      } else if (data.status === 'failed') {
        console.error(`[Progress] Task failed: ${taskId}`, data.message);
        setGenerating(false);
        setError(data.message || 'Generation failed');
        setShowError(true);
        // 清理所有连接
        if (sseClient) sseClient.disconnect();
        if (wsClientInstance) wsClientInstance.disconnect();
        if (poller) poller.stop();
      }
    };

    // 策略：优先使用轮询（最可靠），同时尝试 SSE 和 WebSocket
    // 如果 SSE/WebSocket 成功，停止轮询；如果失败，继续使用轮询
    
    // 1. 立即启动轮询（作为主要方法）
    poller = new TaskPoller(
      taskId,
      (data) => {
        if (activeMethod !== 'poll') {
          console.log(`[Progress] Switching to polling for task: ${taskId}`);
          activeMethod = 'poll';
        }
        updateProgress(data);
      },
      (error) => {
        console.error(`[Progress] Polling error for task ${taskId}:`, error);
      },
      2000 // 2秒轮询一次
    );
    poller.start();
    activeMethod = 'poll';

    // 2. 尝试 SSE（如果成功，可以停止轮询）
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      sseClient = new SSEClient(
        taskId,
        (data) => {
          if (activeMethod !== 'sse') {
            console.log(`[Progress] SSE connected, switching from ${activeMethod} to SSE`);
            if (poller) {
              poller.stop();
              poller = null;
            }
            activeMethod = 'sse';
          }
          updateProgress(data);
        },
        (error) => {
          console.warn(`[Progress] SSE error for task ${taskId}:`, error);
          // SSE 失败，继续使用轮询
        },
        API_BASE_URL
      );
      sseClient.connect();
      
      // 检查 SSE 是否成功连接（延迟检查）
      setTimeout(() => {
        if (sseClient && sseClient.isConnected()) {
          console.log(`[Progress] SSE successfully connected for task: ${taskId}`);
          if (poller) {
            poller.stop();
            poller = null;
          }
          activeMethod = 'sse';
        }
      }, 1000);
    } catch (sseError) {
      console.warn(`[Progress] SSE not available for task ${taskId}:`, sseError);
    }

    // 3. 尝试 WebSocket（如果 SSE 失败）
    try {
      wsClientInstance = wsClient.connect(
        taskId,
        (data) => {
          if (activeMethod !== 'ws') {
            console.log(`[Progress] WebSocket connected, switching from ${activeMethod} to WebSocket`);
            if (poller) {
              poller.stop();
              poller = null;
            }
            activeMethod = 'ws';
          }
          updateProgress(data);
        },
        (err) => {
          console.warn(`[Progress] WebSocket error for task ${taskId}:`, err);
          // WebSocket 失败，继续使用轮询
        }
      );
      
      // 检查 WebSocket 是否成功连接（延迟检查）
      setTimeout(() => {
        if (wsClientInstance && wsClientInstance.isConnected()) {
          console.log(`[Progress] WebSocket successfully connected for task: ${taskId}`);
          if (poller && activeMethod === 'poll') {
            poller.stop();
            poller = null;
          }
          activeMethod = 'ws';
        }
      }, 1000);
    } catch (wsError) {
      console.warn(`[Progress] WebSocket not available for task ${taskId}:`, wsError);
    }

    return () => {
      console.log(`[Progress] Cleaning up progress tracking for task: ${taskId}`);
      if (sseClient) {
        sseClient.disconnect();
      }
      if (wsClientInstance) {
        wsClientInstance.disconnect();
      }
      if (poller) {
        poller.stop();
      }
    };
  }, [taskId]);

  const handleGenerate = async () => {
    if (!backendStatus.connected) {
      setError('Backend not connected. Please start the backend service.');
      setShowError(true);
      return;
    }

    try {
      setGenerating(true);
      setStatus('running');
      setProgress(0);
      setMessage('Starting generation...');
      setError(null);
      
      // 1. 发送请求并等待响应获取 task_id（后端会立即返回，不等待任务执行）
      const response = await api.generateMusic({
        song_name: 'generated',
        lyrics,
        style_prompt: stylePrompt || undefined,
        style_audio: styleAudio || undefined,
        precision,
        batch_size: batchSize,
      });
      
      if (!response || !response.task_id) {
        throw new Error('Invalid response: missing task_id');
      }
      
      // 2. 设置 task_id，开始通过轮询/SSE/WebSocket 获取进度
      // 进度查询逻辑在 useEffect 中，会自动开始轮询
      setTaskId(response.task_id);
    } catch (err: any) {
      setGenerating(false);
      setError(err.message || 'Failed to start generation');
      setShowError(true);
    }
  };

  const handleCancel = async () => {
    if (taskId) {
      try {
        await api.cancelTask(taskId);
        setGenerating(false);
        setStatus('cancelled');
      } catch (err) {
        console.error('Failed to cancel task:', err);
      }
    }
  };

  return (
    <Layout>
      {!backendStatus.connected && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
          Backend not connected. Please start the backend service.
        </Box>
      )}

      <StepIndicator activeStep={0} steps={steps} />
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <LyricsEditor
            value={lyrics}
            onChange={(value) => {
              setLyrics(value);
            }}
          />
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <StylePromptInput
            textValue={stylePrompt}
            onTextChange={(value) => {
              setStylePrompt(value);
            }}
            audioFile={styleAudio}
            onAudioChange={setStyleAudio}
          />
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <GenerationParams
            precision={precision}
            onPrecisionChange={(value) => {
              setPrecision(value);
            }}
            batchSize={batchSize}
            onBatchSizeChange={(value) => {
              setBatchSize(value);
            }}
            maxDuration={maxDuration}
            onMaxDurationChange={(value) => {
              setMaxDuration(value);
            }}
          />
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <GenerateButton
          onClick={handleGenerate}
          disabled={!lyrics.trim() || (!stylePrompt && !styleAudio) || !backendStatus.connected}
          loading={generating}
          fullWidth
        />
      </Box>

      {generating && taskId && (
        <ProgressCard
          taskId={taskId}
          status={status}
          progress={progress}
          message={message}
          onCancel={handleCancel}
        />
      )}

      {outputUrl && !generating && (
        <Box sx={{ mt: 3 }}>
          <AudioPreview
            audioUrl={outputUrl}
            title="Generated Music"
          />
        </Box>
      )}

      <ErrorAlert
        open={showError}
        message={error || ''}
        onClose={() => setShowError(false)}
      />

      <LoadingBackdrop open={generating && !taskId} message="Preparing generation..." />
    </Layout>
  );
}
