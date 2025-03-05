import React from 'react';
import { Card, CardContent, Typography, Box, Divider, Avatar, Chip } from '@mui/material';

type AgentProps = {
  agent: {
    name: string;
    role: string;
    goal: string;
    backstory: string;
    llm: string;
    memory?: boolean;
    cache?: boolean;
  };
};

const AgentCard: React.FC<AgentProps> = ({ agent }) => {
  // Generate a stable avatar color based on the agent name
  const generateColor = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 45%)`;
  };

  const avatarColor = generateColor(agent.name);
  const nameInitial = agent.name.charAt(0).toUpperCase();

  return (
    <Card 
      className="agent-card card" 
      variant="outlined" 
      sx={{ 
        minWidth: 250,
        height: '100%',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box 
        className="agent-card-header"
        sx={{ 
          p: 2,
          bgcolor: avatarColor,
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}
      >
        <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}>
          {nameInitial}
        </Avatar>
        <Box>
          <Typography variant="h6" fontWeight={600}>{agent.name}</Typography>
          <Typography variant="subtitle2" sx={{ opacity: 0.85 }}>
            {agent.role}
          </Typography>
        </Box>
      </Box>
      
      <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
        <Typography variant="subtitle1" fontWeight={500} gutterBottom>
          Goal
        </Typography>
        <Typography variant="body2" paragraph color="text.secondary">
          {agent.goal}
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle1" fontWeight={500} gutterBottom>
          Details
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Chip 
            label={`LLM: ${agent.llm}`} 
            size="small" 
            sx={{ mr: 1, mb: 1 }} 
          />
          
          {agent.memory && (
            <Chip 
              label="Memory" 
              size="small" 
              color="primary" 
              variant="outlined" 
              sx={{ mr: 1, mb: 1 }} 
            />
          )}
          
          {agent.cache && (
            <Chip 
              label="Cache" 
              size="small" 
              color="secondary" 
              variant="outlined" 
              sx={{ mr: 1, mb: 1 }} 
            />
          )}
        </Box>
        
        <Typography variant="subtitle1" fontWeight={500} gutterBottom>
          Backstory
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {agent.backstory}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default AgentCard;
