import React from 'react';
import { useRouter } from 'next/router';
import Layout from '../../src/components/Layout';
import { Typography, Box, Paper } from '@mui/material';
import { useCrew } from '../../src/lib/queries';
import JSONViewer from '../../src/components/JSONViewer';

const CrewDetail: React.FC = () => {
  const router = useRouter();
  const { crewId } = router.query as { crewId: string };
  const {data: crewData, isLoading} = useCrew(crewId);

  if (isLoading) return <Layout><Typography>Loading...</Typography></Layout>;

  if (!crewData) return <Layout><Typography>Crew not found</Typography></Layout>;

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>{crewData.crew_name}</Typography>
      <Typography variant="body1">Process: {crewData.process}</Typography>
      <Typography variant="body1">Manager LLM: {crewData.manager_llm}</Typography>

      <Typography variant="h6" gutterBottom style={{marginTop: '2rem'}}>Agents</Typography>
      <Box display="flex" gap={2} flexWrap="wrap">
        {crewData.agents?.map((agent: any, i: number) => (
          <Paper key={i} style={{padding: '1rem', flex: '1 1 300px'}}>
            <Typography><b>Name:</b> {agent.name}</Typography>
            <Typography><b>Role:</b> {agent.role}</Typography>
            <Typography><b>Goal:</b> {agent.goal}</Typography>
            <Typography><b>LLM:</b> {agent.llm}</Typography>
          </Paper>
        ))}
      </Box>

      <Typography variant="h6" gutterBottom style={{marginTop: '2rem'}}>Tasks</Typography>
      <JSONViewer data={crewData.tasks} />
    </Layout>
  );
};

export default CrewDetail;
