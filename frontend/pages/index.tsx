// pages/index.tsx
import React, { useState, useEffect } from 'react';
import {
  TextField,
  Button,
  Typography,
  Checkbox,
  FormControlLabel,
  Box,
  Chip,
  Grid,
  FormControl,
  FormLabel,
  Dialog,
  DialogContent,
  CircularProgress,
  DialogTitle,
  DialogActions
} from '@mui/material';
import Layout from '../src/components/Layout';
import { useRouter } from 'next/router';
import { postCreateCrew } from '../src/lib/api';

const Home: React.FC = () => {
  const router = useRouter();
  const [description, setDescription] = useState('');
  const [inputDescription, setInputDescription] = useState('');
  const [outputDescription, setOutputDescription] = useState('');
  const [process, setProcess] = useState('sequential');
  const [managerLLM, setManagerLLM] = useState('');
  const [tools, setTools] = useState<string[]>([]);
  const [planning, setPlanning] = useState(false);
  const [knowledge, setKnowledge] = useState(false);
  const [humanInputTasks, setHumanInputTasks] = useState(false);
  const [memory, setMemory] = useState(false);
  const [cache, setCache] = useState(false);
  const [toolInput, setToolInput] = useState('');

  const [loading, setLoading] = useState(false);
  const [thoughts, setThoughts] = useState<string[]>([]);

  const handleAddTool = () => {
    if (toolInput.trim() && !tools.includes(toolInput.trim())) {
      setTools([...tools, toolInput.trim()]);
      setToolInput('');
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setThoughts([]);
    simulateAgentThoughts();

    const payload = {
      user_description: description,
      user_input_description: inputDescription,
      user_output_description: outputDescription,
      user_tools: tools,
      user_process: process,
      user_planning: planning,
      user_knowledge: knowledge,
      user_human_input_tasks: humanInputTasks,
      user_memory: memory,
      user_cache: cache,
      user_manager_llm: managerLLM || null
    };

    try {
      const res = await postCreateCrew(payload);
      if (res.status === 200) {
        setTimeout(() => {
          setLoading(false);
          router.push('/dashboard');
        }, 2000);
      } else {
        alert('Failed to create crew configuration.');
        setLoading(false);
      }
    } catch (err: any) {
      console.error(err);
      alert('An error occurred while creating the crew.');
      setLoading(false);
    }
  };

  const simulateAgentThoughts = () => {
    const messages = [
      "Planning Architect: Analyzing your requirements... distilling conceptual tasks.",
      "Planning Architect: Identifying key steps and selecting the right agents for each role.",
      "Planning Architect: Ensuring tasks are minimal, actionable, and logically sequenced.",
      "Schema Converter: Translating the conceptual plan into a structured Agent-Task Crew schema...",
      "Schema Converter: Validating that each agent and task aligns with your goals.",
      "Schema Converter: Refining and finalizing the schema... almost ready!",
      "Agents are preparing to execute the plan—your customized crew is nearly formed."
    ];

    let index = 0;
    const interval = setInterval(() => {
      if (index < messages.length) {
        setThoughts(prev => [...prev, messages[index]]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 10000); // 10-second delay per message
  };

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>Define Your Project Requirements</Typography>
      <Typography variant="body1" gutterBottom color="text.secondary">
        Provide the details below to create an Agent-Task Crew configuration. After clicking "Create Crew," 
        our Planning Architect and Schema Converter will transform your instructions into a well-defined 
        set of tasks and specialized agents. Once completed, you can review your new crew on the dashboard.
      </Typography>

      <Grid container spacing={3} style={{ marginTop: '1rem' }}>
        <Grid item xs={12}>
          <FormControl fullWidth>
            <FormLabel>Description</FormLabel>
            <TextField
              placeholder="High-level description of your project"
              value={description}
              onChange={e => setDescription(e.target.value)}
              variant="outlined"
            />
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <FormLabel>Input Description</FormLabel>
            <TextField
              placeholder="Describe the input data sources"
              value={inputDescription}
              onChange={e => setInputDescription(e.target.value)}
              variant="outlined"
            />
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <FormLabel>Output Description</FormLabel>
            <TextField
              placeholder="Describe the desired output format"
              value={outputDescription}
              onChange={e => setOutputDescription(e.target.value)}
              variant="outlined"
            />
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <FormLabel>Process</FormLabel>
            <TextField
              placeholder="e.g., sequential"
              value={process}
              onChange={e => setProcess(e.target.value)}
              variant="outlined"
            />
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <FormLabel>Manager LLM (optional)</FormLabel>
            <TextField
              placeholder="e.g., openai/gpt-4"
              value={managerLLM}
              onChange={e => setManagerLLM(e.target.value)}
              variant="outlined"
            />
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <FormControl fullWidth>
            <FormLabel>
              Tools <Typography variant="caption" color="text.secondary">(Add as many as needed)</Typography>
            </FormLabel>
            <Box display="flex" alignItems="center" gap={1} mt={1}>
              <TextField
                placeholder="Enter a tool name"
                value={toolInput}
                onChange={e => setToolInput(e.target.value)}
                variant="outlined"
                style={{flex:1}}
              />
              <Button variant="contained" onClick={handleAddTool}>Add Tool</Button>
            </Box>
            <Box mt={2}>
              {tools.map((t, idx) => (
                <Chip
                  key={idx}
                  label={t}
                  onDelete={() => setTools(tools.filter(x => x!==t))}
                  style={{marginRight: '5px', marginBottom: '5px'}}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>Additional Options</Typography>
          <Box display="flex" flexWrap="wrap" gap={2}>
            <FormControlLabel
              control={<Checkbox checked={planning} onChange={e => setPlanning(e.target.checked)} />}
              label="Planning?"
            />
            <FormControlLabel
              control={<Checkbox checked={knowledge} onChange={e => setKnowledge(e.target.checked)} />}
              label="Knowledge?"
            />
            <FormControlLabel
              control={<Checkbox checked={humanInputTasks} onChange={e => setHumanInputTasks(e.target.checked)} />}
              label="Human Input Tasks?"
            />
            <FormControlLabel
              control={<Checkbox checked={memory} onChange={e => setMemory(e.target.checked)} />}
              label="Memory?"
            />
            <FormControlLabel
              control={<Checkbox checked={cache} onChange={e => setCache(e.target.checked)} />}
              label="Cache?"
            />
          </Box>
        </Grid>

        <Grid item xs={12}>
          <Box mt={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={loading}
              style={{width:'100%', padding:'1rem'}}
            >
              {loading ? 'CREATING...' : 'CREATE CREW'}
            </Button>
          </Box>
        </Grid>
      </Grid>

      <Dialog open={loading} fullWidth maxWidth="sm">
        <DialogTitle>Forming Your Agent-Task Crew</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
            <CircularProgress />
            <Typography variant="body1" align="center">
              The Planning Architect is extracting conceptual tasks from your requirements, while the Schema Converter refines the final schema.
              Soon, your agents will be ready to tackle their assigned tasks.
            </Typography>
            <Typography variant="subtitle2" color="text.secondary" align="center">
              Please wait as we carefully structure each step and assign agents accordingly. Your instructions are being transformed into a custom crew configuration.
            </Typography>

            <Box
              mt={2}
              p={2}
              bgcolor="#f5f5f5"
              width="100%"
              borderRadius={2}
              sx={{maxHeight: 150, overflowY: 'auto'}}
            >
              {thoughts.map((t, i) => (
                <Typography variant="body2" key={i}>{t}</Typography>
              ))}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          {/* No explicit actions needed */}
        </DialogActions>
      </Dialog>
    </Layout>
  );
};

export default Home;
