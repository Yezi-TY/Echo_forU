/**
 * 加载遮罩组件
 */
import React from 'react';
import { Backdrop, CircularProgress, Typography, Box } from '@mui/material';

interface LoadingBackdropProps {
  open: boolean;
  message?: string;
}

export const LoadingBackdrop: React.FC<LoadingBackdropProps> = ({
  open,
  message,
}) => {
  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1,
        flexDirection: 'column',
      }}
      open={open}
    >
      <CircularProgress color="inherit" />
      {message && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body1">{message}</Typography>
        </Box>
      )}
    </Backdrop>
  );
};

export default LoadingBackdrop;

