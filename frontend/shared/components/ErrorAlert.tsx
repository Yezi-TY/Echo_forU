/**
 * 错误提示组件
 */
import React from 'react';
import { Alert, AlertTitle, Snackbar, AlertColor } from '@mui/material';

interface ErrorAlertProps {
  open: boolean;
  message: string;
  severity?: AlertColor;
  title?: string;
  onClose?: () => void;
  autoHideDuration?: number;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  open,
  message,
  severity = 'error',
  title,
  onClose,
  autoHideDuration = 6000,
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert onClose={onClose} severity={severity} sx={{ width: '100%' }}>
        {title && <AlertTitle>{title}</AlertTitle>}
        {message}
      </Alert>
    </Snackbar>
  );
};

export default ErrorAlert;

