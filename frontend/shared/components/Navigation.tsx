/**
 * 导航组件
 */
import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import { Home, History, Settings } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface NavigationProps {
  value: string;
  onChange: (value: string) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ value, onChange }) => {
  const { t } = useTranslation('common');

  return (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
      <BottomNavigation
        value={value}
        onChange={(event, newValue) => onChange(newValue)}
        showLabels
      >
        <BottomNavigationAction
          label={t('common.home') || 'Home'}
          value="home"
          icon={<Home />}
        />
        <BottomNavigationAction
          label={t('history.title')}
          value="history"
          icon={<History />}
        />
        <BottomNavigationAction
          label={t('settings.title')}
          value="settings"
          icon={<Settings />}
        />
      </BottomNavigation>
    </Paper>
  );
};

export default Navigation;

