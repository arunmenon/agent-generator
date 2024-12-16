import React from 'react';
import { AppBar, Toolbar, Typography, Container } from '@mui/material';

const Layout: React.FC<{children: React.ReactNode}> = ({children}) => {
  return (
    <>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{flexGrow: 1}}>Agent Creator</Typography>
          {/* Could add nav links or user info here */}
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" style={{marginTop: '2rem', marginBottom: '2rem'}}>
        {children}
      </Container>
    </>
  );
};

export default Layout;
