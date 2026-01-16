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
  const { t, ready } = useTranslation('common');
  const [mounted, setMounted] = React.useState(false);

  // 避免 hydration 错误：只在客户端挂载后渲染可能不同的内容
  React.useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {mounted && ready ? t('app.name') : 'DiffRhythm2 Music Generator'}
            </Typography>
            {mounted && <LanguageSwitcher />}
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

