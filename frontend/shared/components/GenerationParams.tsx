/**
 * 高级参数配置面板
 */
import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Slider,
  Switch,
  FormControlLabel,
  Box,
  Button,
} from '@mui/material';
import { ExpandMore, RestartAlt } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface GenerationParamsProps {
  precision: 'fp32' | 'fp16' | 'int8';
  onPrecisionChange: (value: 'fp32' | 'fp16' | 'int8') => void;
  batchSize: number;
  onBatchSizeChange: (value: number) => void;
  maxDuration: number;
  onMaxDurationChange: (value: number) => void;
}

export const GenerationParams: React.FC<GenerationParamsProps> = ({
  precision,
  onPrecisionChange,
  batchSize,
  onBatchSizeChange,
  maxDuration,
  onMaxDurationChange,
}) => {
  const { t } = useTranslation('common');

  const handleReset = () => {
    onPrecisionChange('fp16');
    onBatchSizeChange(1);
    onMaxDurationChange(300);
  };

  return (
    <Accordion defaultExpanded={false}>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Typography variant="subtitle1">
          {t('generation.step3')}
        </Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* 精度选择 */}
          <Box>
            <Typography gutterBottom>
              {t('hardware.precision')}: {precision.toUpperCase()}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              {(['fp32', 'fp16', 'int8'] as const).map((p) => (
                <Button
                  key={p}
                  variant={precision === p ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => onPrecisionChange(p)}
                >
                  {p.toUpperCase()}
                </Button>
              ))}
            </Box>
          </Box>

          {/* 批处理大小 */}
          <Box>
            <Typography gutterBottom>
              {t('hardware.batchSize')}: {batchSize}
            </Typography>
            <Slider
              value={batchSize}
              onChange={(_, value) => onBatchSizeChange(value as number)}
              min={1}
              max={8}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Box>

          {/* 最大时长 */}
          <Box>
            <Typography gutterBottom>
              {t('generation.maxDuration') || 'Max Duration'}: {maxDuration}s
            </Typography>
            <Slider
              value={maxDuration}
              onChange={(_, value) => onMaxDurationChange(value as number)}
              min={30}
              max={600}
              step={30}
              marks={[
                { value: 30, label: '30s' },
                { value: 300, label: '5min' },
                { value: 600, label: '10min' },
              ]}
              valueLabelDisplay="auto"
            />
          </Box>

          {/* 恢复默认 */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              startIcon={<RestartAlt />}
              onClick={handleReset}
              size="small"
            >
              {t('common.reset') || 'Reset to Default'}
            </Button>
          </Box>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default GenerationParams;

