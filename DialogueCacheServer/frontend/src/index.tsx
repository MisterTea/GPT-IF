import Bugsnag from '@bugsnag/js';
import BugsnagPluginReact from '@bugsnag/plugin-react';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';
import { AppBar, Box, CssBaseline, Link as MaterialLink, MenuItem, ThemeProvider, Toolbar, Typography, createTheme } from '@mui/material';
import { observer } from 'mobx-react';
import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  Outlet,
  Route,
  RouterProvider,
  createBrowserRouter,
  createRoutesFromElements,
  useNavigate
} from "react-router-dom";
import About from './About';
import App from './App';
import DataStore from './datastore';
import './index.css';
import reportWebVitals from './reportWebVitals';

Bugsnag.start({
  apiKey: 'e2092073c1186a2ea272e9a8ee40a2e4',
  plugins: [new BugsnagPluginReact()]
})

const ErrorBoundary = Bugsnag.getPlugin('react')!.createErrorBoundary(React);

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

const datastore = new DataStore();

const Root = observer(({ datastore }: { datastore: DataStore }) => {
  const navigate = useNavigate();

  return (<div>
    <div className="Header">
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <MenuItem key="/" onClick={() => { navigate("/"); }}>
              <Typography textAlign="center">Play</Typography>
            </MenuItem>
            <MenuItem key="about" onClick={() => { navigate("about"); }}>
              <Typography textAlign="center">Learn</Typography>
            </MenuItem>
          </Toolbar>
        </AppBar>
      </Box>
    </div>
    <Outlet />
    <div className="Footer">
      Made by Jason Gauci
      <MaterialLink href="https://twitter.com/neuralnets4life" target="_blank" rel="noopener"><TwitterIcon /></MaterialLink>
      <MaterialLink href="https://www.linkedin.com/in/jasongauci" target="_blank" rel="noopener"><LinkedInIcon /></MaterialLink>
    </div>
  </div>);
});

const router = createBrowserRouter(
  createRoutesFromElements(
    ["/index.html", "/"].map((path, index) => {
      return <Route path={path} key={index} element={<Root datastore={datastore} />}>
        <Route index element={<App datastore={datastore} />}></Route>
        <Route path="about" element={<About datastore={datastore} />}></Route>
      </Route>
    })
  ));

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <RouterProvider router={router} />
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
