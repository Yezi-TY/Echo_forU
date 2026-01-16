import React, { useState, useEffect } from "react";
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
} from "@music-gen-ui/shared/components";
import { Box, Card, CardContent } from "@mui/material";
import { api, wsClient, useBackendConnection } from "@music-gen-ui/shared/lib";
import "@music-gen-ui/shared/lib/i18n/i18n"; // Initialize i18n

const STORAGE_KEY = 'music-gen-ui-form-state';

function App() {
  // 使用默认值初始化
  const [lyrics, setLyrics] = useState("");
  const [stylePrompt, setStylePrompt] = useState("");
  const [styleAudio, setStyleAudio] = useState<File | null>(null);
  const [precision, setPrecision] = useState<"fp32" | "fp16" | "int8">("fp16");
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
    if (mounted) {
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
  const [status, setStatus] = useState("pending");
  const [message, setMessage] = useState("");
  const [outputUrl, setOutputUrl] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [showError, setShowError] = useState(false);

  const backendStatus = useBackendConnection();
  const steps = ["generation.step1", "generation.step2", "generation.step3"];

  useEffect(() => {
    if (taskId) {
      const client = wsClient.connect(
        taskId,
        (data) => {
          setProgress(data.progress || 0);
          setStatus(data.status || "running");
          setMessage(data.message || "");

          if (data.status === "completed") {
            setGenerating(false);
            if (data.output_path) {
              setOutputUrl(data.output_path);
            }
          } else if (data.status === "failed") {
            setGenerating(false);
            setError(data.message || "Generation failed");
            setShowError(true);
          }
        },
        (err) => {
          setError(err.message);
          setShowError(true);
        }
      );

      return () => {
        client.disconnect();
      };
    }
  }, [taskId]);

  const handleGenerate = async () => {
    if (!backendStatus.connected) {
      setError("Backend not connected. Please start the backend service.");
      setShowError(true);
      return;
    }

    try {
      setGenerating(true);
      setStatus("running");
      setProgress(0);
      setMessage("Starting generation...");
      setError(null);

      const response = await api.generateMusic({
        song_name: "generated",
        lyrics,
        style_prompt: stylePrompt || undefined,
        style_audio: styleAudio || undefined,
        precision,
        batch_size: batchSize,
      });

      setTaskId(response.task_id);
    } catch (err: any) {
      setGenerating(false);
      setError(err.message || "Failed to start generation");
      setShowError(true);
    }
  };

  const handleCancel = async () => {
    if (taskId) {
      try {
        await api.cancelTask(taskId);
        setGenerating(false);
        setStatus("cancelled");
      } catch (err) {
        console.error("Failed to cancel task:", err);
      }
    }
  };

  return (
    <Layout>
      {!backendStatus.connected && (
        <Box sx={{ mb: 2, p: 2, bgcolor: "warning.light", borderRadius: 1 }}>
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

      <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
        <GenerateButton
          onClick={handleGenerate}
          disabled={
            !lyrics.trim() ||
            (!stylePrompt && !styleAudio) ||
            !backendStatus.connected
          }
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
          <AudioPreview audioUrl={outputUrl} title="Generated Music" />
        </Box>
      )}

      <ErrorAlert
        open={showError}
        message={error || ""}
        onClose={() => setShowError(false)}
      />

      <LoadingBackdrop
        open={generating && !taskId}
        message="Preparing generation..."
      />
    </Layout>
  );
}

export default App;
