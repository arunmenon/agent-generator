import React, { useState, useEffect } from 'react';
import {
  TextField,
  Button,
  Typography,
  Box,
  Grid,
  Paper,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  Card,
  CardContent,
  useTheme,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import Layout from '../src/components/Layout';
import { useRouter } from 'next/router';
import { postCreateCrewFlow, postDebugCrewFlow } from '../src/lib/api';

// Timeline component for showing the flow process
const FlowTimeline = ({ activeStep }: { activeStep: number }) => {
  const steps = [
    'Analysis Crew',
    'Planning Crew',
    'Implementation Crew',
    'Evaluation Crew',
    'Final Crew Plan'
  ];

  return (
    <Box className="timeline-container" sx={{ my: 4, px: 2 }}>
      <div className="timeline-connector"></div>
      {steps.map((step, index) => (
        <Box 
          key={index} 
          sx={{ 
            mb: 3, 
            position: 'relative',
            opacity: index <= activeStep ? 1 : 0.5,
            transition: 'opacity 0.3s ease'
          }}
        >
          <div className="timeline-dot" style={{ top: '50%', transform: 'translateY(-50%)' }}></div>
          <Paper 
            elevation={index <= activeStep ? 2 : 0}
            sx={{ 
              p: 2, 
              ml: 2, 
              borderRadius: 2,
              bgcolor: index <= activeStep ? 'white' : '#f5f5f5',
              transition: 'all 0.3s ease'
            }}
          >
            <Typography variant="h6" fontWeight={500}>
              {step}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {index === 0 && 'Analyzing requirements, determining complexity...'}
              {index === 1 && 'Selecting algorithms, generating candidate plans...'}
              {index === 2 && 'Creating agent definitions, designing tasks...'}
              {index === 3 && 'Evaluating quality, identifying improvements...'}
              {index === 4 && 'Finalizing crew configuration...'}
            </Typography>
          </Paper>
        </Box>
      ))}
    </Box>
  );
};

const FlowCreator: React.FC = () => {
  const router = useRouter();
  const theme = useTheme();
  
  // State management
  const [task, setTask] = useState('');
  const [model, setModel] = useState('gpt-4o');
  const [temperature, setTemperature] = useState(0.7);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(-1);
  const [debugMode, setDebugMode] = useState(false);
  const [statusMessages, setStatusMessages] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  
  // Set isClient to true once component mounts on the client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Simulate the flow process and update the active step
  const simulateFlowProcess = () => {
    setStatusMessages(['Starting flow process...']);
    
    // Simulate the flow process with timeouts
    const steps = [
      { message: 'Analysis Crew: Analyzing requirements...', delay: 2000 },
      { message: 'Analysis Crew: Determining task complexity and process type...', delay: 3000 },
      { message: 'Planning Crew: Selecting optimal algorithm...', delay: 2000 },
      { message: 'Planning Crew: Generating candidate plans...', delay: 3000 },
      { message: 'Planning Crew: Evaluating and selecting best plan...', delay: 2000 },
      { message: 'Implementation Crew: Defining specialized agents...', delay: 2000 },
      { message: 'Implementation Crew: Creating task definitions...', delay: 2000 },
      { message: 'Implementation Crew: Structuring workflow...', delay: 2000 },
      { message: 'Evaluation Crew: Assessing crew quality...', delay: 2000 },
      { message: 'Evaluation Crew: Making improvement recommendations...', delay: 2000 },
      { message: 'Finalizing crew configuration...', delay: 1000 },
      { message: 'Crew creation complete!', delay: 1000 }
    ];

    let currentStep = 0;
    let currentTime = 0;
    
    steps.forEach((step, index) => {
      currentTime += step.delay;
      
      setTimeout(() => {
        setStatusMessages(prev => [...prev, step.message]);
        
        // Increment the stepper based on the crew stage
        if (index < 2) setActiveStep(0);
        else if (index < 5) setActiveStep(1);
        else if (index < 8) setActiveStep(2);
        else if (index < 10) setActiveStep(3);
        else setActiveStep(4);
        
      }, currentTime);
    });
    
    // Final completion - navigate to dashboard after a delay
    setTimeout(() => {
      setLoading(false);
      router.push('/dashboard');
    }, currentTime + 2000);
  };

  const handleSubmit = async () => {
    if (!task.trim()) {
      setError('Please provide a task description');
      return;
    }
    
    setLoading(true);
    setActiveStep(0);
    setError(null);
    
    // Start simulation immediately for visual feedback
    simulateFlowProcess();
    
    try {
      // Create a payload with the task and model parameters
      const payload = { 
        task, 
        model_name: model, 
        temperature 
      };
      
      console.log("Sending API request with payload:", payload);
      
      // Choose which API method to use based on debug mode
      const apiMethod = debugMode ? postDebugCrewFlow : postCreateCrewFlow;
      const response = await apiMethod(payload);
      
      console.log("API response:", response);
      
      if (response.status !== 200) {
        setError('Failed to create crew. Please try again.');
        setLoading(false);
      } else {
        console.log("Crew created successfully:", response.data);
        // We don't stop the animation here because the simulateFlowProcess
        // handles the success case including redirecting to the dashboard
      }
      
    } catch (err: any) {
      console.error("API error:", err);
      setError(`Error: ${err.message || 'Failed to create crew'}`);
      setLoading(false);
      setActiveStep(-1);
      setStatusMessages([]);
    }
  };

  return (
    <Layout>
      <Box className={isClient ? "animate-fadeIn" : ""}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" fontWeight={600} gutterBottom>
                Hierarchical Flow Creator
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Create an optimized agent crew using our hierarchical multi-crew flow architecture.
                This system orchestrates four specialized crews to analyze, plan, implement, and evaluate
                the perfect configuration for your task.
              </Typography>
            </Box>
            
            <Card className={`card ${isClient ? "animate-slideInUp" : ""}`} variant="outlined">
              <CardContent sx={{ p: 3 }}>
                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}
                
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <TextField
                    label="Task Description"
                    multiline
                    rows={4}
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    placeholder="Describe what you want your agent crew to accomplish..."
                    variant="outlined"
                    disabled={loading}
                    required
                    fullWidth
                  />
                </FormControl>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth variant="outlined">
                      <InputLabel>Model</InputLabel>
                      <Select
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        label="Model"
                        disabled={loading}
                      >
                        <MenuItem value="gpt-4o">GPT-4o</MenuItem>
                        <MenuItem value="gpt-4o-mini">GPT-4o Mini</MenuItem>
                        <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                        <MenuItem value="claude-3-opus">Claude 3 Opus</MenuItem>
                        <MenuItem value="claude-3-sonnet">Claude 3 Sonnet</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box>
                      <Typography gutterBottom>Temperature: {temperature}</Typography>
                      <Slider
                        value={temperature}
                        onChange={(_, value) => setTemperature(value as number)}
                        step={0.1}
                        marks
                        min={0}
                        max={1}
                        disabled={loading}
                        valueLabelDisplay="auto"
                      />
                    </Box>
                  </Grid>
                </Grid>

                <Box sx={{ my: 2 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={debugMode}
                        onChange={(e) => setDebugMode(e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Debug Mode (return detailed analysis)"
                  />
                </Box>
                
                <Box display="flex" alignItems="center" mt={2}>
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    onClick={handleSubmit}
                    disabled={loading || !task.trim()}
                    fullWidth
                    sx={{ py: 1.5 }}
                  >
                    {loading ? (
                      <Box display="flex" alignItems="center">
                        <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                        Processing...
                      </Box>
                    ) : (
                      'Create Crew with Flow'
                    )}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              {activeStep >= 0 ? (
                <>
                  <Typography variant="h6" fontWeight={500} gutterBottom>
                    Flow Progress
                  </Typography>
                  <Paper 
                    sx={{ 
                      p: 3, 
                      flexGrow: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      bgcolor: '#fff',
                    }}
                    elevation={0}
                    variant="outlined"
                  >
                    <FlowTimeline activeStep={activeStep} />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Status Log:
                    </Typography>
                    <Box 
                      sx={{ 
                        flexGrow: 1, 
                        overflow: 'auto',
                        bgcolor: '#f9f9f9',
                        p: 2,
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        fontSize: '0.85rem',
                        maxHeight: 200
                      }}
                    >
                      {isClient && statusMessages.map((message, index) => (
                        <Box key={index} sx={{ mb: 1 }}>
                          {message}
                        </Box>
                      ))}
                    </Box>
                  </Paper>
                </>
              ) : (
                <Card 
                  className="card" 
                  variant="outlined"
                  sx={{ 
                    p: 3, 
                    bgcolor: theme.palette.primary.main,
                    color: 'white'
                  }}
                >
                  <CardContent>
                    <Typography variant="h5" fontWeight={600} gutterBottom>
                      Hierarchical Multi-Crew Flow
                    </Typography>
                    <Typography variant="body1" paragraph>
                      Our advanced flow architecture orchestrates four specialized crews to generate 
                      the optimal agent configuration for your specific needs:
                    </Typography>
                    
                    <Box sx={{ mb: 2, mt: 3 }}>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Analysis Crew
                      </Typography>
                      <Typography variant="body2">
                        Analyzes requirements, determines complexity and process type
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Planning Crew
                      </Typography>
                      <Typography variant="body2">
                        Selects algorithms, generates plans, verifies approach
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Implementation Crew
                      </Typography>
                      <Typography variant="body2">
                        Defines agents, tasks, and workflow structure
                      </Typography>
                    </Box>
                    
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Evaluation Crew
                      </Typography>
                      <Typography variant="body2">
                        Assesses quality, suggests improvements
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};

export default FlowCreator;