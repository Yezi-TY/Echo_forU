/**
 * 设置页面组件
 */
import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Container,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { HardwareInfoCard } from './HardwareInfoCard';
import { HardwareEstimateCard } from './HardwareEstimateCard';
import { OptimizationSettings } from './OptimizationSettings';
import { ModelStatusCard } from './ModelStatusCard';
import { LanguageSwitcher } from './LanguageSwitcher';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export const SettingsPage: React.FC = () => {
  const { t } = useTranslation('common');
  const [value, setValue] = useState(0);

  const handleChange = (_: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        {t('settings.title')}
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={value} onChange={handleChange}>
          <Tab label={t('settings.general')} />
          <Tab label={t('settings.model')} />
          <Tab label={t('settings.hardware')} />
          <Tab label={t('settings.language')} />
        </Tabs>
      </Box>

      <TabPanel value={value} index={0}>
        <Typography variant="h6" gutterBottom>
          {t('settings.general')}
        </Typography>
        {/* 常规设置内容 */}
      </TabPanel>

      <TabPanel value={value} index={1}>
        <ModelStatusCard />
      </TabPanel>

      <TabPanel value={value} index={2}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <HardwareInfoCard hardwareInfo={{}} />
          <HardwareEstimateCard />
          <OptimizationSettings />
        </Box>
      </TabPanel>

      <TabPanel value={value} index={3}>
        <Typography variant="h6" gutterBottom>
          {t('settings.language')}
        </Typography>
        <LanguageSwitcher />
      </TabPanel>
    </Container>
  );
};

export default SettingsPage;

