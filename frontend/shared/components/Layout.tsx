/**
 * 主布局组件
 */
import React, { ReactNode } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  ThemeProvider,
  CssBaseline,
} from '@mui/material';
import { lightTheme } from '../theme';
import { LanguageSwitcher } from './LanguageSwitcher';
import { useTranslation } from 'react-i18next';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation('common');

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {t('app.name') || 'DiffRhythm2 Music Generator'}
            </Typography>
            <LanguageSwitcher />
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flex: 1 }}>
          {children}
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default Layout;

