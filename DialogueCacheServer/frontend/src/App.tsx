import { ArrowForwardIos } from '@mui/icons-material';
import { Grid } from '@mui/material';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import { KeyboardEvent, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import DataStore from './datastore';
import logo from './logo.svg'; // Tell webpack this JS file uses this image

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const App = ({ datastore }: { datastore: DataStore }) => {
  const valueRef: React.MutableRefObject<any> = useRef('') //creating a refernce for TextField Component

  function submit() {
    console.log("SUBMITTING");
    console.log(valueRef.current.value);
  }

  function submitIfEnter(e: KeyboardEvent) {
    if (e.key === "Enter") {
      submit();
    }
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="App">
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <ReactMarkdown>Hello, **world**!</ReactMarkdown>
            <ReactMarkdown>Hello, **world**!</ReactMarkdown>
            <ReactMarkdown>Hello, **world**!</ReactMarkdown>
            <Box sx={{ display: 'flex', p: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-end', flexGrow: 1 }}>
                <ArrowForwardIos sx={{ color: 'action.active', mr: 1, my: 0.5 }} />
                <TextField id="input-with-sx" label="Tap/Click here" variant="standard" fullWidth onKeyDown={submitIfEnter} inputRef={valueRef} />
              </Box>
              <Button variant="contained" onClick={submit}>Submit</Button>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <img src={logo} alt="Logo" />
          </Grid>
          <Grid item xs={12}>
            <div>
              <Button variant="contained">{datastore.blocks.length === 0 ? "Start Game" : "Restart Game"}</Button>
            </div>
          </Grid>
        </Grid>
      </div>
    </ThemeProvider>

  );
}

export default App;
