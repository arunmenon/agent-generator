import React from 'react';
import { Table, TableHead, TableRow, TableCell, TableBody, Paper, TableContainer } from '@mui/material';

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
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Expected Output</TableCell>
            <TableCell>Agent</TableCell>
            <TableCell>Human Input</TableCell>
            <TableCell>Context Tasks</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tasks.map((t, i) => (
            <TableRow key={i}>
              <TableCell>{t.name}</TableCell>
              <TableCell>{t.description}</TableCell>
              <TableCell>{t.expected_output}</TableCell>
              <TableCell>{t.agent}</TableCell>
              <TableCell>{t.human_input ? 'Yes' : 'No'}</TableCell>
              <TableCell>{t.context_tasks.join(', ')}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TaskTable;
