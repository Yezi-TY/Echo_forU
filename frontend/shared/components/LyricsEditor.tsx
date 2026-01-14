/**
 * 歌词编辑器组件
 */
import React, { useState } from 'react';
import {
  TextField,
  Box,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';
import { HelpOutline } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface LyricsEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const LyricsEditor: React.FC<LyricsEditorProps> = ({
  value,
  onChange,
  placeholder,
}) => {
  const { t } = useTranslation('common');
  const [helpOpen, setHelpOpen] = useState(false);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  const wordCount = value.trim().length;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
          {t('generation.lyrics')}
        </Typography>
        <IconButton size="small" onClick={() => setHelpOpen(true)}>
          <HelpOutline fontSize="small" />
        </IconButton>
        <Typography variant="caption" color="text.secondary">
          {wordCount} {t('common.characters') || 'characters'}
        </Typography>
      </Box>
      <TextField
        fullWidth
        multiline
        rows={8}
        value={value}
        onChange={handleChange}
        placeholder={placeholder || t('generation.lyricsPlaceholder')}
        variant="outlined"
      />
      <Dialog open={helpOpen} onClose={() => setHelpOpen(false)}>
        <DialogTitle>{t('generation.lyrics')} {t('common.help') || 'Help'}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('generation.lyricsHelp') || '支持 LRC 格式歌词，可以包含时间标签和段落标记。'}
            <br />
            <br />
            <strong>示例格式：</strong>
            <br />
            [00:00.00]第一行歌词
            <br />
            [00:05.00]第二行歌词
            <br />
            [verse]
            <br />
            段落内容
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHelpOpen(false)}>{t('common.close')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LyricsEditor;

