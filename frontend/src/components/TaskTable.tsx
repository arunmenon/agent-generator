import React from 'react';
import { Table, TableHead, TableRow, TableCell, TableBody, Paper, TableContainer, Chip, Box, Typography, Tooltip } from '@mui/material';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import PersonIcon from '@mui/icons-material/Person';

type Task = {
  name: string;
  description: string;
  expected_output: string;
  agent: string;
  human_input: boolean;
  context_tasks: string[];
};

type TaskTableProps = {
  tasks: Task[];
};

const TaskTable: React.FC<TaskTableProps> = ({ tasks }) => {
  return (
    <TableContainer component={Paper} sx={{ borderRadius: 2, overflow: 'hidden', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: '#f5f7fa' }}>
            <TableCell sx={{ fontWeight: 600 }}>Task</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Expected Output</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Agent</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Dependencies</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tasks.map((t, i) => (
            <TableRow 
              key={i}
              sx={{ 
                '&:hover': { bgcolor: '#f9fafc' },
                transition: 'background-color 0.2s'
              }}
            >
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography fontWeight={500}>{t.name}</Typography>
                  {t.human_input && (
                    <Tooltip title="Requires human input">
                      <Chip 
                        icon={<PersonIcon fontSize="small" />} 
                        label="Human Input" 
                        size="small" 
                        color="secondary" 
                        sx={{ height: 24 }}
                      />
                    </Tooltip>
                  )}
                </Box>
              </TableCell>
              <TableCell sx={{ color: 'text.secondary' }}>{t.description}</TableCell>
              <TableCell sx={{ color: 'text.secondary' }}>{t.expected_output}</TableCell>
              <TableCell>
                <Chip 
                  label={t.agent} 
                  size="small" 
                  sx={{ 
                    bgcolor: generateAgentColor(t.agent),
                    color: 'white',
                    fontWeight: 500
                  }} 
                />
              </TableCell>
              <TableCell>
                {t.context_tasks.length > 0 ? (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {t.context_tasks.map((dep, idx) => (
                      <Chip 
                        key={idx}
                        label={dep}
                        size="small"
                        variant="outlined"
                        sx={{ borderRadius: 1 }}
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.disabled">None</Typography>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

// Generate a stable color based on agent name for visual consistency
const generateAgentColor = (str: string) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 45%)`;
};

export default TaskTable;
