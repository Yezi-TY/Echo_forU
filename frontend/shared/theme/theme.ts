import { createTheme, ThemeOptions } from '@mui/material/styles';

// 定义主题配置
const themeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1', // 紫色 - 音乐主题
      light: '#818cf8',
      dark: '#4f46e5',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#8b5cf6', // 紫色变体
      light: '#a78bfa',
      dark: '#7c3aed',
    },
    success: {
      main: '#10b981', // 绿色 - 生成完成
    },
    warning: {
      main: '#f59e0b', // 橙色 - 需要用户注意
    },
    error: {
      main: '#ef4444', // 红色 - 错误提示
    },
    background: {
      default: '#f9fafb',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
        },
        contained: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
};

// 创建主题
export const lightTheme = createTheme(themeOptions);

// 深色主题
const darkThemeOptions: ThemeOptions = {
  ...themeOptions,
  palette: {
    ...themeOptions.palette,
    mode: 'dark',
    background: {
      default: '#111827',
      paper: '#1f2937',
    },
  },
};

export const darkTheme = createTheme(darkThemeOptions);

// 默认导出浅色主题
export default lightTheme;

