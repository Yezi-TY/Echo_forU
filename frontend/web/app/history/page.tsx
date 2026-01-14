'use client';

import React from 'react';
import { Layout, HistoryList, AudioPreview } from '@music-gen-ui/shared/components';
import { useState } from 'react';
import '../../shared/lib/i18n/i18n';

export default function HistoryPage() {
  const [playingRecord, setPlayingRecord] = useState<any>(null);

  const handlePlay = (record: any) => {
    setPlayingRecord(record);
  };

  return (
    <Layout>
      <HistoryList
        onPlay={handlePlay}
        onDelete={(id) => {
          console.log('Delete:', id);
        }}
      />
      
      {playingRecord && playingRecord.output_path && (
        <AudioPreview
          audioUrl={playingRecord.output_path}
          title={playingRecord.song_name}
        />
      )}
    </Layout>
  );
}

