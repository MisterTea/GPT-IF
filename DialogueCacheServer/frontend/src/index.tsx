import Bugsnag from '@bugsnag/js';
import BugsnagPluginReact from '@bugsnag/plugin-react';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import BugReportIcon from '@mui/icons-material/BugReport';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';
import { AppBar, Box, CssBaseline, Link as MaterialLink, MenuItem, Paper, ThemeProvider, Toolbar, Typography, createTheme } from '@mui/material';
import { observer } from 'mobx-react';
import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  Outlet,
  Route,
  RouterProvider,
  createBrowserRouter,
  createRoutesFromElements,
  useLocation,
  useNavigate
} from "react-router-dom";
import About from './About';
import App from './App';
import Feedback from './Feedback';
import DataStore, { GptifAlert } from './datastore';
import { APP_VERSION } from './globals';
import './index.css';
import reportWebVitals from './reportWebVitals';

var ErrorBoundary: any = React.Fragment;
if (process.env.NODE_ENV !== 'development') {
  Bugsnag.start({
    apiKey: 'e2092073c1186a2ea272e9a8ee40a2e4',
    plugins: [new BugsnagPluginReact()],
    appVersion: APP_VERSION
  })

  ErrorBoundary = Bugsnag.getPlugin('react')!.createErrorBoundary(React);
}


const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

const datastore = new DataStore();

const Root = observer(({ datastore }: { datastore: DataStore }) => {
  const navigate = useNavigate();
  const location = useLocation();

  var playOrRestart = (
    <MenuItem key="/" onClick={() => { navigate("/"); }}>
      <Typography textAlign="center" variant="h6" component="div" sx={{ flexGrow: 1 }}>Play</Typography>
    </MenuItem>
  );

  if (location.pathname === "/" || location.pathname === "/index.html") {
    playOrRestart = (
      <MenuItem key="/" onClick={() => {
        datastore.submitNewGame().then(() => {
          window.scrollTo(0, 0);
        }).catch((reason: any) => {
          console.log("FETCH FAILED");
          console.log(reason);
          const newAlert: GptifAlert = { message: "Could not start the game: " + reason, duration: 5, title: "Can't start game", severity: "error" };
          datastore.addAlert(newAlert);
        });
      }}>
        <Typography textAlign="center" variant="h6" component="div" sx={{ flexGrow: 1 }}>Restart</Typography>
      </MenuItem>
    );
  }

  return (<div>
    <Feedback datastore={datastore} />
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          {playOrRestart}
          {/*<MenuItem key="about" onClick={() => { navigate("about"); }}>
              <Typography textAlign="center">Learn</Typography>
  </MenuItem>*/}
        </Toolbar>
      </AppBar>
    </Box>
    <Outlet />
    <Paper sx={{
      marginTop: 'calc(10% + 60px)',
      width: '100%',
      position: 'fixed',
      bottom: 0,
    }} component="footer" square variant="outlined">
      Made by Jason Gauci
      <MaterialLink href="https://twitter.com/neuralnets4life" target="_blank" rel="noopener"><TwitterIcon /></MaterialLink>
      <MaterialLink href="https://www.linkedin.com/in/jasongauci" target="_blank" rel="noopener"><LinkedInIcon /></MaterialLink>
      <MaterialLink href="#" onClick={() => { datastore.openFeedback(); }}><BugReportIcon /></MaterialLink>
      <br />
      Version {APP_VERSION}
    </Paper>
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
