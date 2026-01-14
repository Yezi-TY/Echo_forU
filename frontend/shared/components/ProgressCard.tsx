/**
 * 生成进度卡片组件
 */
import React from 'react';
import {
  Card,
  CardContent,
  LinearProgress,
  Typography,
  Box,
  Chip,
  Button,
} from '@mui/material';
import { useTranslation } from 'react-i18next';

interface ProgressCardProps {
  taskId: string;
  status: string;
  progress: number;
  message: string;
  onCancel?: () => void;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({
  taskId,
  status,
  progress,
  message,
  onCancel,
}) => {
  const { t } = useTranslation('common');

  const getStatusColor = (status: string): 'default' | 'primary' | 'success' | 'error' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{t('generation.generating')}</Typography>
          <Chip
            label={status}
            color={getStatusColor(status)}
            size="small"
          />
        </Box>
        <LinearProgress
          variant="determinate"
          value={progress * 100}
          sx={{ mb: 1 }}
        />
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
        {onCancel && status === 'running' && (
          <Box sx={{ mt: 2 }}>
            <Button size="small" onClick={onCancel}>
              {t('common.cancel')}
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ProgressCard;

