/**
 * 硬件压力预估卡片组件
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  Chip,
} from '@mui/material';
import { Warning, CheckCircle } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { api } from '../lib';

interface EstimateResult {
  feasible: boolean;
  estimated_vram_gb: number;
  estimated_time_seconds: number;
  warnings: string[];
  recommendations: string[];
}

interface HardwareEstimateCardProps {
  modelSizeGb?: number;
  batchSize?: number;
  precision?: string;
}

export const HardwareEstimateCard: React.FC<HardwareEstimateCardProps> = ({
  modelSizeGb = 2.0,
  batchSize = 1,
  precision = 'fp16',
}) => {
  const { t } = useTranslation('common');
  const [estimate, setEstimate] = useState<EstimateResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEstimate();
  }, [modelSizeGb, batchSize, precision]);

  const loadEstimate = async () => {
    try {
      setLoading(true);
      const data = await api.estimateHardwarePressure({
        model_size_gb: modelSizeGb,
        batch_size: batchSize,
        precision,
      });
      setEstimate(data);
    } catch (error) {
      console.error('Failed to estimate hardware pressure:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!estimate) {
    return null;
  }

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds.toFixed(0)}s`;
    } else if (seconds < 3600) {
      return `${(seconds / 60).toFixed(1)}min`;
    } else {
      return `${(seconds / 3600).toFixed(1)}h`;
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {t('hardware.estimate') || 'Hardware Estimate'}
          </Typography>
          {estimate.feasible ? (
            <Chip
              icon={<CheckCircle />}
              label={t('hardware.feasible') || 'Feasible'}
              color="success"
              size="small"
            />
          ) : (
            <Chip
              icon={<Warning />}
              label={t('hardware.notFeasible') || 'Not Feasible'}
              color="warning"
              size="small"
            />
          )}
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {t('hardware.estimatedVRAM') || 'Estimated VRAM'}:{' '}
            <strong>{estimate.estimated_vram_gb.toFixed(1)} GB</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t('hardware.estimatedTime') || 'Estimated Time'}:{' '}
            <strong>{formatTime(estimate.estimated_time_seconds)}</strong>
          </Typography>
        </Box>

        {estimate.warnings.length > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {estimate.warnings.map((warning, index) => (
              <Typography key={index} variant="body2">
                {warning}
              </Typography>
            ))}
          </Alert>
        )}

        {estimate.recommendations.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              {t('hardware.recommendations') || 'Recommendations'}:
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2 }}>
              {estimate.recommendations.map((rec, index) => (
                <Typography key={index} component="li" variant="body2">
                  {rec}
                </Typography>
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default HardwareEstimateCard;

