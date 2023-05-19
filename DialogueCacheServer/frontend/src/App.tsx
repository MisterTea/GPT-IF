import { ArrowForwardIos } from '@mui/icons-material';
import { Alert, AlertColor, AlertTitle, Grid, Pagination } from '@mui/material';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { observer } from "mobx-react";
import { KeyboardEvent, useCallback, useEffect, useRef, useState } from 'react';
//import rehypeRaw from 'rehype-raw';
//import remarkDirective from 'remark-directive';
//import remarkGfm from 'remark-gfm';
import './App.css';
import ReactAnimatedEllipsis from './ReactAnimatedEllipses';
import DataStore from './datastore';

interface GptifAlert {
  message: string;
  title: string;
  severity: AlertColor;
  duration: number;
}

const App = observer(({ datastore }: { datastore: DataStore }) => {
  const commandValueRef: React.MutableRefObject<any> = useRef(''); //creating a refernce for TextField Component
  const commandRef: React.MutableRefObject<any> = useRef(null); //creating a refernce for TextField Component

  const [waitingForAnswer, setWaitingForAnswer] = useState<boolean>(false);
  const [alerts, setAlerts] = useState<GptifAlert[]>([]);

  function getFocusSoon() {
    setTimeout(() => {
      commandValueRef.current.focus();
      window.scrollTo(0, 0);
    }, 50);
  }

  function submitCommand(command: string) {
    setWaitingForAnswer(true);
    datastore.submitCommand(command).then(() => {
      console.log("CLEARING");
      commandValueRef.current.value = "";
      setWaitingForAnswer(false);
      getFocusSoon();
    }).catch((reason: any) => {
      console.log("FETCH FAILED");
      console.log(reason);
      setWaitingForAnswer(false);
      console.log(commandValueRef.current);
      getFocusSoon();
      const newAlert: GptifAlert = { message: "Could not send command: " + reason, duration: 5, title: "Command failed", severity: "error" };
      setAlerts([...alerts, newAlert]);
    })
  }

  function submitIfEnter(e: KeyboardEvent) {
    if (e.key === "Enter") {
      const command = commandValueRef.current.value;
      //if (command.length === 0)
      //return;
      console.log("SUBMITTING");
      console.log(commandValueRef.current.value);
      submitCommand(command);
    }
  }

  const submitNewGame = useCallback(() => {
    console.log("STARTING NEW GAME");
    setWaitingForAnswer(true);
    datastore.submitNewGame().then(() => {
      setWaitingForAnswer(false);
      window.scrollTo(0, 0);
      getFocusSoon();
    }).catch((reason: any) => {
      console.log("FETCH FAILED");
      console.log(reason);
      setWaitingForAnswer(false);
      const newAlert: GptifAlert = { message: "Could not start the game: " + reason, duration: 5, title: "Can't start game", severity: "error" };
      setAlerts([...alerts, newAlert]);
    });
  }, [datastore, alerts]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (alerts.length === 0) {
        return;
      }

      alerts.forEach(alert => {
        alert.duration -= 1;
      });
      setAlerts(alerts.filter((alert) => {
        return alert.duration > 0;
      }))
    }, 1000);

    return () => clearInterval(interval);
  }, [alerts, setAlerts, submitNewGame]);

  var counter = 0;
  var game_text = null;
  if (datastore.currentBlock !== null) {
    var pagination = null;
    if (datastore.blocks.length > 1) {
      const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
        datastore.goToPage(value - 1);
      };

      pagination = <Pagination count={datastore.blocks.length} shape="rounded" size="small" page={datastore.currentBlockIndex + 1} onChange={handlePageChange} />;
    }

    game_text = (
      <div>
        {pagination}
        <div key={counter} dangerouslySetInnerHTML={{ __html: datastore.currentBlock.chatSections.join("\n\n") }}></div>
      </div>
    );
  }
  // const game_text = (<ul>
  //   {datastore.blocks.map(chatBlock => {
  //     counter += 1;
  //     return <div key={counter} dangerouslySetInnerHTML={{ __html: chatBlock.chatSections.join("\n\n") }}></div>
  //   })}
  // </ul>
  // );

  var ellipses = null;
  var commandBox = null;
  if (datastore.blocks.length > 0) {
    var showReturnButton = false;
    var showCommandBox = false;
    if (waitingForAnswer) {
    } else {
      if (datastore.currentBlockIndex !== datastore.blocks.length - 1) {
        showCommandBox = false;
        showReturnButton = true;
      } else {
        showCommandBox = true;
      }
    }
    commandBox = (
      <div>
        <Button variant="contained" style={{ visibility: (showReturnButton ? 'visible' : 'hidden') }} onClick={() => {
          datastore.goToLastPage();
        }}>
          Return to current scene
        </Button>
        <Box sx={{ display: 'flex', p: 1 }} style={{ visibility: (showCommandBox ? 'visible' : 'hidden') }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-end', flexGrow: 1 }}>
            <ArrowForwardIos sx={{ color: 'action.active', mr: 1, my: 0.5 }} />
            <TextField id="input-with-sx" label="Tap/Click here" variant="standard" fullWidth onKeyDown={submitIfEnter} inputRef={commandValueRef} ref={commandRef} autoComplete="off" />
          </Box>
          <Button variant="contained" onClick={() => {
            const command = commandValueRef.current.value;
            //if (command.length === 0)
            //return;
            console.log("SUBMITTING");
            console.log(commandValueRef.current.value);
            submitCommand(command);
          }}>Submit</Button>
        </Box>
      </div>
    );
  }
  if (waitingForAnswer || datastore.blocks.length === 0) {
    ellipses = (
      <ReactAnimatedEllipsis
        fontSize="3rem"
        marginLeft="5px"
        spacing="0.3rem" />
    );
  }

  var alertHtml = null;
  var alertIndex = 0;
  if (alerts.length > 0) {
    alertHtml = (
      alerts.map((alert: GptifAlert) => {
        alertIndex += 1;
        return (
          <Alert severity={alert.severity} key={"Alert_" + alertIndex}>
            <AlertTitle>{alert.title}</AlertTitle>
            {alert.message}
          </Alert>
        );
      })
    )
  }

  var logoStyle;
  if (false && window.innerWidth >= 900) {
    logoStyle = { position: "absolute", bottom: "0px", width: "100%" };
  } else {
    logoStyle = { width: "100%" };
  }

  var gameImageHtml = null;
  if (datastore.gameImageUrl !== null) {
    gameImageHtml = <img src={datastore.gameImageUrl} alt="Logo" style={logoStyle} />;
  }

  return (
    <div className="App">
      <Grid container spacing={2}>
        <Grid item xs={12} md={6} style={{ whiteSpace: "normal" }}>
          {game_text}
          {ellipses}
          {alertHtml}
          {commandBox}
        </Grid>
        <Grid item xs={12} md={6} style={{ position: "relative", minHeight: "400px" }}>
          {gameImageHtml}
        </Grid>
        <Grid item xs={12}>
          <div>
            {datastore.blocks.length > 0 && <Button variant="contained" onClick={submitNewGame}>{datastore.blocks.length === 0 ? "Start Game" : "Restart Game"}</Button>}
          </div>
        </Grid>
      </Grid>
    </div>
  );
});

export default App;
