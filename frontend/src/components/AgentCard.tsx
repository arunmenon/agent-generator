import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

type AgentProps = {
  agent: {
    name: string;
    role: string;
    goal: string;
    backstory: string;
    llm: string;
    memory: boolean;
    cache: boolean;
  };
};

const AgentCard: React.FC<AgentProps> = ({ agent }) => {
  return (
    <Card style={{minWidth: 250}}>
      <CardContent>
        <Typography variant="h6">{agent.name}</Typography>
        <Typography variant="subtitle1"><b>Role:</b> {agent.role}</Typography>
        <Typography variant="body2"><b>Goal:</b> {agent.goal}</Typography>
        <Typography variant="body2"><b>Backstory:</b> {agent.backstory}</Typography>
        <Typography variant="body2"><b>LLM:</b> {agent.llm}</Typography>
      </CardContent>
    </Card>
  );
};

export default AgentCard;
