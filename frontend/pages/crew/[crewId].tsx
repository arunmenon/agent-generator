import React from 'react';
import { useRouter } from 'next/router';
import Layout from '../../src/components/Layout';
import { Typography, Box, Paper, Grid } from '@mui/material';
import { useCrew } from '../../src/lib/queries';
import JSONViewer from '../../src/components/JSONViewer';
import AgentCard from '../../src/components/AgentCard';
import TaskTable from '../../src/components/TaskTable';

const CrewDetail: React.FC = () => {
  const router = useRouter();
  const { crewId } = router.query as { crewId: string };
  const {data: crewData, isLoading} = useCrew(crewId);

  if (isLoading) return <Layout><Typography>Loading...</Typography></Layout>;
  if (!crewData) return <Layout><Typography>No agent-task crew found.</Typography></Layout>;

  // crewData structure: { agents: [...], tasks: [...], etc. }
  const { agents, tasks } = crewData;

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>Agent-Task Crew</Typography>
      <Typography variant="body1" gutterBottom color="text.secondary">
        Below is a list of agents and tasks for this configuration. All crew-specific fields have been omitted
        for a cleaner, task-focused view.
      </Typography>

      <Typography variant="h6" gutterBottom style={{marginTop: '2rem'}}>Agents</Typography>
      <Grid container spacing={2}>
        {agents?.map((agent: any, i: number) => (
          <Grid item xs={12} sm={4} key={i}>
            <AgentCard agent={{
              name: agent.name,
              role: agent.role,
              goal: agent.goal,
              backstory: agent.backstory || '',
              llm: agent.llm || '',
              memory: agent.memory,
              cache: agent.cache
            }} />
          </Grid>
        ))}
      </Grid>

      <Typography variant="h6" gutterBottom style={{marginTop: '2rem'}}>Tasks</Typography>
      {tasks && tasks.length > 0 ? (
        <TaskTable tasks={tasks} />
      ) : (
        <Typography>No tasks found.</Typography>
      )}

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>Raw JSON (Optional)</Typography>
        <Typography variant="body2" color="text.secondary">For debugging purposes only.</Typography>
        <JSONViewer data={crewData} />
      </Box>
    </Layout>
  );
};

export default CrewDetail;
