import React from 'react';
import {Box} from '@mui/material';

type JSONViewerProps = {
  data: any;
};

const JSONViewer: React.FC<JSONViewerProps> = ({ data }) => {
  return (
    <Box component="pre" sx={{
      backgroundColor: '#f5f5f5',
      padding: 2,
      borderRadius: 2,
      overflowX: 'auto'
    }}>
      {JSON.stringify(data, null, 2)}
    </Box>
  );
};

export default JSONViewer;
