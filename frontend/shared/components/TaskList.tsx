/**
 * 任务列表组件
 */
import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  IconButton,
  Box,
  Typography,
} from '@mui/material';
import { Cancel, CheckCircle, Error, HourglassEmpty } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface Task {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  message: string;
  created_at: string;
}

interface TaskListProps {
  tasks: Task[];
  onCancel?: (taskId: string) => void;
}

export const TaskList: React.FC<TaskListProps> = ({ tasks, onCancel }) => {
  const { t } = useTranslation('common');

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
        return <Error color="error" />;
      case 'running':
        return <HourglassEmpty color="primary" />;
      default:
        return <HourglassEmpty color="disabled" />;
    }
  };

  const getStatusColor = (status: Task['status']): 'default' | 'primary' | 'success' | 'error' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'primary';
      default:
        return 'default';
    }
  };

  if (tasks.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body2" color="text.secondary">
          {t('common.noTasks') || 'No tasks'}
        </Typography>
      </Box>
    );
  }

  return (
    <List>
      {tasks.map((task) => (
        <ListItem key={task.id}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
            {getStatusIcon(task.status)}
            <ListItemText
              primary={task.message || `Task ${task.id.slice(0, 8)}`}
              secondary={`${(task.progress * 100).toFixed(0)}% - ${new Date(task.created_at).toLocaleString()}`}
            />
            <Chip
              label={task.status}
              color={getStatusColor(task.status)}
              size="small"
            />
          </Box>
          <ListItemSecondaryAction>
            {task.status === 'running' && onCancel && (
              <IconButton
                edge="end"
                onClick={() => onCancel(task.id)}
                size="small"
              >
                <Cancel />
              </IconButton>
            )}
          </ListItemSecondaryAction>
        </ListItem>
      ))}
    </List>
  );
};

export default TaskList;

