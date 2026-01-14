/**
 * 步骤指示器组件
 */
import React from 'react';
import { Stepper, Step, StepLabel, Box } from '@mui/material';
import { useTranslation } from 'react-i18next';

interface StepIndicatorProps {
  activeStep: number;
  steps: string[];
}

export const StepIndicator: React.FC<StepIndicatorProps> = ({
  activeStep,
  steps,
}) => {
  const { t } = useTranslation('common');

  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      <Stepper activeStep={activeStep} alternativeLabel>
        {steps.map((label, index) => (
          <Step key={index}>
            <StepLabel>{t(label) || label}</StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

export default StepIndicator;

