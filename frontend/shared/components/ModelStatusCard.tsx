/**
 * 模型状态卡片组件
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  LinearProgress,
} from '@mui/material';
import { Download, CheckCircle, Error } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { api } from '../lib';

interface ModelStatus {
  diffrhythm2: {
    downloaded: boolean;
    path?: string;
    size?: number;
  };
  mulan: {
    downloaded: boolean;
    path?: string;
    size?: number;
  };
}

export const ModelStatusCard: React.FC = () => {
  const { t } = useTranslation('common');
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const data = await api.getModelStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to load model status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (modelType: string) => {
    try {
      setDownloading(modelType);
      await api.downloadModel(modelType);
      await loadStatus();
    } catch (error) {
      console.error('Failed to download model:', error);
    } finally {
      setDownloading(null);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress />
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {t('settings.model')}
        </Typography>

        {/* DiffRhythm2 模型 */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2">DiffRhythm2</Typography>
            {status.diffrhythm2.downloaded ? (
              <Chip
                icon={<CheckCircle />}
                label={t('common.downloaded') || 'Downloaded'}
                color="success"
                size="small"
              />
            ) : (
              <Chip
                icon={<Error />}
                label={t('common.notDownloaded') || 'Not Downloaded'}
                color="default"
                size="small"
              />
            )}
          </Box>
          {status.diffrhythm2.downloaded && status.diffrhythm2.size && (
            <Typography variant="caption" color="text.secondary">
              {status.diffrhythm2.size.toFixed(2)} GB
            </Typography>
          )}
          {!status.diffrhythm2.downloaded && (
            <Button
              startIcon={<Download />}
              onClick={() => handleDownload('diffrhythm2')}
              disabled={downloading === 'diffrhythm2'}
              size="small"
              variant="outlined"
            >
              {downloading === 'diffrhythm2' ? t('common.downloading') || 'Downloading...' : t('common.download') || 'Download'}
            </Button>
          )}
        </Box>

        {/* MuQ-MuLan 模型 */}
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2">MuQ-MuLan</Typography>
            {status.mulan.downloaded ? (
              <Chip
                icon={<CheckCircle />}
                label={t('common.downloaded') || 'Downloaded'}
                color="success"
                size="small"
              />
            ) : (
              <Chip
                icon={<Error />}
                label={t('common.notDownloaded') || 'Not Downloaded'}
                color="default"
                size="small"
              />
            )}
          </Box>
          {status.mulan.downloaded && status.mulan.size && (
            <Typography variant="caption" color="text.secondary">
              {status.mulan.size.toFixed(2)} GB
            </Typography>
          )}
          {!status.mulan.downloaded && (
            <Button
              startIcon={<Download />}
              onClick={() => handleDownload('mulan')}
              disabled={downloading === 'mulan'}
              size="small"
              variant="outlined"
            >
              {downloading === 'mulan' ? t('common.downloading') || 'Downloading...' : t('common.download') || 'Download'}
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ModelStatusCard;

