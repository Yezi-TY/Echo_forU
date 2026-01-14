/**
 * 硬件优化设置组件
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Button,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { api } from '../lib';

interface OptimizationConfig {
  precision: string;
  batch_size: number;
  use_gpu: boolean;
  gradient_checkpointing: boolean;
  cpu_offload: boolean;
}

export const OptimizationSettings: React.FC = () => {
  const { t } = useTranslation('common');
  const [config, setConfig] = useState<OptimizationConfig | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const data = await api.getOptimizationConfig();
      setConfig(data);
    } catch (error) {
      console.error('Failed to load optimization config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!config) return;
    try {
      await api.updateConfig('hardware', config);
      // 显示成功消息
    } catch (error) {
      console.error('Failed to apply optimization config:', error);
    }
  };

  if (!config) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {t('hardware.optimization')}
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* 精度选择 */}
          <FormControl fullWidth>
            <InputLabel>{t('hardware.precision')}</InputLabel>
            <Select
              value={config.precision}
              onChange={(e) => setConfig({ ...config, precision: e.target.value })}
              label={t('hardware.precision')}
            >
              <MenuItem value="fp32">FP32</MenuItem>
              <MenuItem value="fp16">FP16</MenuItem>
              <MenuItem value="int8">INT8</MenuItem>
            </Select>
          </FormControl>

          {/* 批处理大小 */}
          <Box>
            <Typography gutterBottom>
              {t('hardware.batchSize')}: {config.batch_size}
            </Typography>
            <Slider
              value={config.batch_size}
              onChange={(_, value) => setConfig({ ...config, batch_size: value as number })}
              min={1}
              max={8}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Box>

          {/* 应用按钮 */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button variant="contained" onClick={handleApply}>
              {t('common.apply') || 'Apply'}
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default OptimizationSettings;

