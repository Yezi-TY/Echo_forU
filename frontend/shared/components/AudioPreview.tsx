/**
 * 音频预览播放器组件
 */
import React, { useRef, useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Box,
  IconButton,
  Slider,
  Typography,
  Button,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  VolumeUp,
  Download,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface AudioPreviewProps {
  audioUrl: string;
  title?: string;
  onDownload?: () => void;
}

export const AudioPreview: React.FC<AudioPreviewProps> = ({
  audioUrl,
  title,
  onDownload,
}) => {
  const { t } = useTranslation('common');
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => setPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (playing) {
      audio.pause();
    } else {
      audio.play();
    }
    setPlaying(!playing);
  };

  const handleSeek = (_: Event, value: number | number[]) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = value as number;
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (_: Event, value: number | number[]) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newVolume = value as number;
    audio.volume = newVolume;
    setVolume(newVolume);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card>
      <CardContent>
        {title && (
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
        )}

        <audio ref={audioRef} src={audioUrl} />

        {/* 播放控制 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <IconButton onClick={togglePlay} color="primary" size="large">
            {playing ? <Pause /> : <PlayArrow />}
          </IconButton>

          <Box sx={{ flexGrow: 1 }}>
            <Slider
              value={currentTime}
              max={duration || 100}
              onChange={handleSeek}
              size="small"
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
              <Typography variant="caption">
                {formatTime(currentTime)}
              </Typography>
              <Typography variant="caption">
                {formatTime(duration)}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', width: 100 }}>
            <VolumeUp fontSize="small" />
            <Slider
              value={volume}
              min={0}
              max={1}
              step={0.1}
              onChange={handleVolumeChange}
              size="small"
            />
          </Box>

          {onDownload && (
            <Button
              startIcon={<Download />}
              onClick={onDownload}
              variant="outlined"
              size="small"
            >
              {t('common.download') || 'Download'}
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AudioPreview;

