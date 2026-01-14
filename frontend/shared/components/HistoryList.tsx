/**
 * 历史记录列表组件
 */
import React, { useEffect, useState } from 'react';
import {
  Box,
  TextField,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Chip,
  Grid,
} from '@mui/material';
import { Search, Delete, Download, PlayArrow } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { api } from '../lib';

interface HistoryRecord {
  id: string;
  song_name: string;
  created_at: string;
  duration?: number;
  output_path?: string;
}

interface HistoryListProps {
  onPlay?: (record: HistoryRecord) => void;
  onDelete?: (id: string) => void;
}

export const HistoryList: React.FC<HistoryListProps> = ({
  onPlay,
  onDelete,
}) => {
  const { t } = useTranslation('common');
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [search]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getHistory({ search: search || undefined });
      setRecords(data.records || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteHistory(id);
      await loadHistory();
      if (onDelete) {
        onDelete(id);
      }
    } catch (error) {
      console.error('Failed to delete history:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder={t('history.search')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
        />
      </Box>

      {records.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            {t('history.noHistory')}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {records.map((record) => (
            <Grid item xs={12} sm={6} md={4} key={record.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {record.song_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {formatDate(record.created_at)}
                  </Typography>
                  <Chip
                    label={formatDuration(record.duration)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </CardContent>
                <CardActions>
                  {record.output_path && onPlay && (
                    <IconButton
                      size="small"
                      onClick={() => onPlay(record)}
                      color="primary"
                    >
                      <PlayArrow />
                    </IconButton>
                  )}
                  {record.output_path && (
                    <IconButton
                      size="small"
                      component="a"
                      href={record.output_path}
                      download
                    >
                      <Download />
                    </IconButton>
                  )}
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(record.id)}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default HistoryList;

