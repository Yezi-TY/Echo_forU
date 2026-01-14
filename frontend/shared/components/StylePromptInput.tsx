/**
 * 风格提示输入组件
 */
import React, { useState } from 'react';
import {
  Box,
  ToggleButton,
  ToggleButtonGroup,
  TextField,
  Button,
  Typography,
  Paper,
  IconButton,
} from '@mui/material';
import { Upload, Delete, MusicNote } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

type StyleMode = 'text' | 'audio';

interface StylePromptInputProps {
  textValue: string;
  onTextChange: (value: string) => void;
  audioFile: File | null;
  onAudioChange: (file: File | null) => void;
}

export const StylePromptInput: React.FC<StylePromptInputProps> = ({
  textValue,
  onTextChange,
  audioFile,
  onAudioChange,
}) => {
  const { t } = useTranslation('common');
  const [mode, setMode] = useState<StyleMode>('text');

  const handleModeChange = (
    event: React.MouseEvent<HTMLElement>,
    newMode: StyleMode | null
  ) => {
    if (newMode !== null) {
      setMode(newMode);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onAudioChange(file);
    }
  };

  const handleFileRemove = () => {
    onAudioChange(null);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
          {t('generation.step2')}
        </Typography>
        <ToggleButtonGroup
          value={mode}
          exclusive
          onChange={handleModeChange}
          size="small"
        >
          <ToggleButton value="text">
            {t('generation.stylePrompt')}
          </ToggleButton>
          <ToggleButton value="audio">
            {t('generation.styleAudio')}
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {mode === 'text' ? (
        <TextField
          fullWidth
          multiline
          rows={3}
          value={textValue}
          onChange={(e) => onTextChange(e.target.value)}
          placeholder={t('generation.stylePromptPlaceholder')}
          variant="outlined"
        />
      ) : (
        <Paper
          variant="outlined"
          sx={{
            p: 3,
            textAlign: 'center',
            borderStyle: 'dashed',
            borderWidth: 2,
            borderColor: 'divider',
          }}
        >
          {audioFile ? (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MusicNote sx={{ mr: 1 }} />
                <Typography variant="body1" sx={{ flexGrow: 1 }}>
                  {audioFile.name}
                </Typography>
                <IconButton onClick={handleFileRemove} color="error">
                  <Delete />
                </IconButton>
              </Box>
              <Typography variant="caption" color="text.secondary">
                {(audioFile.size / 1024 / 1024).toFixed(2)} MB
              </Typography>
            </Box>
          ) : (
            <Box>
              <Upload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" gutterBottom>
                {t('generation.uploadAudio')}
              </Typography>
              <input
                accept="audio/*"
                style={{ display: 'none' }}
                id="audio-upload-input"
                type="file"
                onChange={handleFileSelect}
              />
              <label htmlFor="audio-upload-input">
                <Button variant="contained" component="span" startIcon={<Upload />}>
                  {t('generation.uploadAudio')}
                </Button>
              </label>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default StylePromptInput;

