import React, { useState } from 'react';
import {TextField, Button, Typography, Checkbox, FormControlLabel, Box, Chip} from '@mui/material';
import Layout from '../src/components/Layout';
import { useRouter } from 'next/router';
import { postCreateCrew } from '../src/lib/api';

const Home: React.FC = () => {
  const router = useRouter();
  const [description, setDescription] = useState('');
  const [inputDescription, setInputDescription] = useState('');
  const [outputDescription, setOutputDescription] = useState('');
  const [process, setProcess] = useState('');
  const [managerLLM, setManagerLLM] = useState('');
  const [tools, setTools] = useState<string[]>([]);
  const [planning, setPlanning] = useState(false);
  const [knowledge, setKnowledge] = useState(false);
  const [humanInputTasks, setHumanInputTasks] = useState(false);
  const [memory, setMemory] = useState(false);
  const [cache, setCache] = useState(false);
  const [toolInput, setToolInput] = useState('');

  const handleAddTool = () => {
    if (toolInput && !tools.includes(toolInput)) {
      setTools([...tools, toolInput]);
      setToolInput('');
    }
  };

  const handleSubmit = async () => {
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
  
    const res = await postCreateCrew(payload);
    const finalConfig = res.data.config;
    
    // Now you have the final configuration. You can:
    // 1. Display it directly on the same page,
    // 2. Navigate to a new page showing the final configuration, or
    // 3. Show a success message and link to the crew dashboard.
  
    // For example, navigate to dashboard:
    router.push('/dashboard');
  };
  

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>Define Your Project Requirements</Typography>
      <Box display="flex" flexDirection="column" gap={2}>
        <TextField label="Project Description" fullWidth value={description} onChange={e => setDescription(e.target.value)} />
        <TextField label="Input Description" fullWidth value={inputDescription} onChange={e => setInputDescription(e.target.value)} />
        <TextField label="Output Description" fullWidth value={outputDescription} onChange={e => setOutputDescription(e.target.value)} />
        <TextField label="Process (e.g., sequential)" fullWidth value={process} onChange={e => setProcess(e.target.value)} />
        <TextField label="Manager LLM (optional)" fullWidth value={managerLLM} onChange={e => setManagerLLM(e.target.value)} />

        <Box>
          <TextField label="Add a Tool" value={toolInput} onChange={e => setToolInput(e.target.value)} />
          <Button onClick={handleAddTool}>Add Tool</Button>
          <Box mt={1}>
            {tools.map((t, idx) => <Chip key={idx} label={t} onDelete={() => setTools(tools.filter(x => x!==t))} style={{marginRight: '5px'}} />)}
          </Box>
        </Box>

        <FormControlLabel control={<Checkbox checked={planning} onChange={e => setPlanning(e.target.checked)} />} label="Planning?" />
        <FormControlLabel control={<Checkbox checked={knowledge} onChange={e => setKnowledge(e.target.checked)} />} label="Knowledge?" />
        <FormControlLabel control={<Checkbox checked={humanInputTasks} onChange={e => setHumanInputTasks(e.target.checked)} />} label="Human Input Tasks?" />
        <FormControlLabel control={<Checkbox checked={memory} onChange={e => setMemory(e.target.checked)} />} label="Memory?" />
        <FormControlLabel control={<Checkbox checked={cache} onChange={e => setCache(e.target.checked)} />} label="Cache?" />

        <Button variant="contained" onClick={handleSubmit}>Next</Button>
      </Box>
    </Layout>
  );
};

export default Home;
