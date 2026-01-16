/**
 * 硬件信息卡片组件
 */
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
} from '@mui/material';
import { Memory, Computer, Storage } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface HardwareInfo {
  gpu?: {
    available: boolean;
    name?: string;
    memory_total?: number;
    memory_free?: number;
  };
  cpu?: {
    cores?: number;
    usage?: number;
  };
  memory?: {
    total?: number;
    used?: number;
    percent?: number;
  };
}

interface HardwareInfoCardProps {
  hardwareInfo: HardwareInfo;
}

export const HardwareInfoCard: React.FC<HardwareInfoCardProps> = ({
  hardwareInfo,
}) => {
  const { t } = useTranslation('common');

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {t('hardware.title')}
        </Typography>

        <Grid container spacing={2}>
          {/* GPU 信息 */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Storage sx={{ mr: 1 }} />
              <Typography variant="subtitle2">
                {t('hardware.gpu')}
              </Typography>
            </Box>
            {hardwareInfo.gpu?.available ? (
              <Box>
                <Typography variant="body2">
                  {hardwareInfo.gpu.name || 'NVIDIA GPU'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {hardwareInfo.gpu.memory_total?.toFixed(1)} GB Total
                  {hardwareInfo.gpu.memory_free !== undefined && (
                    <> / {hardwareInfo.gpu.memory_free.toFixed(1)} GB Free</>
                  )}
                </Typography>
                <Chip
                  label={t('hardware.available')}
                  color="success"
                  size="small"
                  sx={{ mt: 1 }}
                />
              </Box>
            ) : (
              <Chip
                label={t('hardware.notAvailable')}
                color="default"
                size="small"
              />
            )}
          </Grid>

          {/* CPU 信息 */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Computer sx={{ mr: 1 }} />
              <Typography variant="subtitle2">
                {t('hardware.cpu')}
              </Typography>
            </Box>
            <Typography variant="body2">
              {hardwareInfo.cpu?.cores || 'N/A'} {t('hardware.cores') || 'Cores'}
            </Typography>
            {hardwareInfo.cpu?.usage !== undefined && (
              <Typography variant="caption" color="text.secondary">
                {hardwareInfo.cpu.usage.toFixed(1)}% {t('hardware.usage') || 'Usage'}
              </Typography>
            )}
          </Grid>

          {/* 内存信息 */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Memory sx={{ mr: 1 }} />
              <Typography variant="subtitle2">
                {t('hardware.memory')}
              </Typography>
            </Box>
            {hardwareInfo.memory?.total ? (
              <Box>
                <Typography variant="body2">
                  {hardwareInfo.memory.total.toFixed(1)} GB Total
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {hardwareInfo.memory.used?.toFixed(1)} GB Used
                  {hardwareInfo.memory.percent !== undefined && (
                    <> ({hardwareInfo.memory.percent.toFixed(1)}%)</>
                  )}
                </Typography>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                N/A
              </Typography>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default HardwareInfoCard;

