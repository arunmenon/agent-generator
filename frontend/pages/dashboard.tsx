import React from 'react';
import Layout from '../src/components/Layout';
import { Typography, Table, TableHead, TableRow, TableCell, TableBody, Paper, TableContainer } from '@mui/material';
import Link from 'next/link';
import { useCrews } from '../src/lib/queries';

const Dashboard: React.FC = () => {
  const {data: crews, isLoading} = useCrews();

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      {isLoading && <Typography>Loading...</Typography>}
      {crews && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Crew Name</TableCell>
                <TableCell>Process</TableCell>
                <TableCell>Manager LLM</TableCell>
                <TableCell>Active</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {crews.map((crew: any) => (
                <TableRow key={crew.crew_id} hover>
                  <TableCell>
                    <Link href={`/crew/${crew.crew_id}`} style={{textDecoration: 'none', color: 'blue'}}>
                      {crew.crew_name}
                    </Link>
                  </TableCell>
                  <TableCell>{crew.process}</TableCell>
                  <TableCell>{crew.manager_llm}</TableCell>
                  <TableCell>{crew.is_active ? "Yes" : "No"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Layout>
  );
};

export default Dashboard;
