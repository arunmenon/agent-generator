import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box, Button, useTheme, useMediaQuery } from '@mui/material';
import { useRouter } from 'next/router';
import Image from 'next/image';
import Link from 'next/link';

const Layout: React.FC<{children: React.ReactNode}> = ({children}) => {
  const router = useRouter();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <>
      <AppBar position="static" color="primary" elevation={0} className="gradient-bg">
        <Toolbar>
          <Box display="flex" alignItems="center">
            <Link href="/" passHref>
              <Box component="a" display="flex" alignItems="center" sx={{ textDecoration: 'none', color: 'white' }}>
                {/* Placeholder for logo */}
                <Typography variant="h5" sx={{ fontWeight: 600, marginLeft: 1 }}>
                  Agent Creator
                </Typography>
              </Box>
            </Link>
          </Box>
          
          <Box sx={{ flexGrow: 1 }} />
          
          {!isMobile && (
            <Box display="flex" gap={1}>
              <Button 
                color="inherit" 
                onClick={() => router.push('/')}
                sx={{ 
                  opacity: router.pathname === '/' ? 1 : 0.85,
                  fontWeight: router.pathname === '/' ? 600 : 400
                }}
              >
                Home
              </Button>
              <Button 
                color="inherit" 
                onClick={() => router.push('/flow')}
                sx={{ 
                  opacity: router.pathname === '/flow' ? 1 : 0.85,
                  fontWeight: router.pathname === '/flow' ? 600 : 400
                }}
              >
                Flow Creator
              </Button>
              <Button 
                color="inherit" 
                onClick={() => router.push('/dashboard')}
                sx={{ 
                  opacity: router.pathname === '/dashboard' ? 1 : 0.85,
                  fontWeight: router.pathname === '/dashboard' ? 600 : 400
                }}
              >
                Dashboard
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
        {children}
      </Container>
      
      <Box component="footer" sx={{ py: 3, bgcolor: '#f5f5f5', mt: 4 }}>
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            Agent Creator - Hierarchical Multi-Crew Flow Architecture
          </Typography>
        </Container>
      </Box>
    </>
  );
};

export default Layout;
