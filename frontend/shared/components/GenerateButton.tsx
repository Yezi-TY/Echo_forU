/**
 * 生成按钮组件
 */
import React from 'react';
import { Button, CircularProgress, Box } from '@mui/material';
import { MusicNote } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface GenerateButtonProps {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({
  onClick,
  disabled = false,
  loading = false,
  fullWidth = false,
}) => {
  const { t } = useTranslation('common');

  return (
    <Button
      variant="contained"
      size="large"
      fullWidth={fullWidth}
      onClick={onClick}
      disabled={disabled || loading}
      startIcon={
        loading ? (
          <CircularProgress size={20} color="inherit" />
        ) : (
          <MusicNote />
        )
      }
      sx={{
        py: 1.5,
        fontSize: '1.1rem',
        fontWeight: 600,
      }}
    >
      {loading ? t('generation.generating') : t('generation.generateButton')}
    </Button>
  );
};

export default GenerateButton;

