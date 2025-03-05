import React, { useState, useEffect } from 'react';
import Layout from '../src/components/Layout';
import { Typography, Table, TableHead, TableRow, TableCell, TableBody, Paper, TableContainer } from '@mui/material';
import Link from 'next/link';
import { useCrews } from '../src/lib/queries';

const Dashboard: React.FC = () => {
  const [isClient, setIsClient] = useState(false);
  const {data: crews, isLoading} = useCrews();
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      {isLoading && <Typography>Loading...</Typography>}
      {isClient && crews && crews.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Crew Name</TableCell>
                <TableCell>Process</TableCell>
                <TableCell>Manager LLM</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {crews.map((crew: any) => (
                <TableRow key={crew.crew_id} hover>
                  <TableCell>
                    <Link href={`/crew/${crew.crew_id}`} passHref legacyBehavior>
                      <a style={{textDecoration: 'none', color: 'blue'}}>
                        {crew.crew_name}
                      </a>
                    </Link>
                  </TableCell>
                  <TableCell>{crew.process}</TableCell>
                  <TableCell>{crew.manager_llm}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography>No crews found.</Typography>
      )}
    </Layout>
  );
};

export default Dashboard;
