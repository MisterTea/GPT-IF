import { ArrowForwardIos } from '@mui/icons-material';
import { Alert, AlertTitle, Container, Divider, Grid, Link, Pagination, Paper, Stack, Typography } from '@mui/material';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { observer } from "mobx-react";
import { KeyboardEvent, useCallback, useEffect, useRef, useState } from 'react';
//import rehypeRaw from 'rehype-raw';
//import remarkDirective from 'remark-directive';
//import remarkGfm from 'remark-gfm';
import VideogameAssetIcon from '@mui/icons-material/VideogameAsset';
import * as React from 'react';
import FadeIn from 'react-fade-in';
import { getCookie } from 'typescript-cookie';
import './App.css';
import ReactAnimatedEllipsis from './ReactAnimatedEllipses';
import DataStore, { GptifAlert } from './datastore';

const App = observer(({ datastore }: { datastore: DataStore }) => {
  const commandValueRef: React.MutableRefObject<any> = useRef(''); //creating a refernce for TextField Component
  const commandRef: React.MutableRefObject<any> = useRef(null); //creating a refernce for TextField Component

  const [waitingForAnswer, setWaitingForAnswer] = useState<boolean>(false);

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
      if (datastore.blocks.length >= 10) {
        datastore.openChatFeedbackOnce();
        //datastore.openFeedback();
      }
      getFocusSoon();
    }).catch((reason: any) => {
      console.log("FETCH FAILED");
      console.log(reason);
      setWaitingForAnswer(false);
      console.log(commandValueRef.current);
      getFocusSoon();
      const newAlert: GptifAlert = { message: "Could not send command: " + reason, duration: 5, title: "Command failed", severity: "error" };
      datastore.addAlert(newAlert);
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
      datastore.addAlert(newAlert);
    });
  }, [datastore]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (datastore.alerts.length === 0) {
        return;
      }

      datastore.updateAlerts();
    }, 1000);

    const eventListener = () => {
      console.log("GOING TO NEXT PAGE");
      if (datastore.currentBlockIndex < datastore.blocks.length - 1) {
        datastore.goToNextPage();
      }
    };

    window.addEventListener("keydown", eventListener);

    return () => {
      window.removeEventListener("keydown", eventListener);
      clearInterval(interval);
    }
  }, [datastore, submitNewGame, window]);

  var game_text = null;
  if (datastore.currentBlock !== null) {
    var pagination = null;
    if (datastore.maxBlockIndex > 1 && datastore.maxBlockIndex === datastore.blocks.length - 1) {
      const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
        datastore.goToPage(value - 1);
      };

      pagination = <Pagination variant="outlined" count={datastore.maxBlockIndex + 1} shape="rounded" size="small" page={datastore.currentBlockIndex + 1} onChange={handlePageChange} hideNextButton={datastore.currentBlockIndex === datastore.blocks.length - 1} />;
    }

    game_text = (
      <div>
        {pagination}
        <FadeIn key={"ChatBlock/" + datastore.currentBlockIndex} transitionDuration={1000}>
          {
            datastore.currentBlock.chatSections.map((chatBlock: string, index: number, array: string[]) => {
              return <div key={"ChatBlock/" + datastore.currentBlockIndex + "/" + index} dangerouslySetInnerHTML={{ __html: chatBlock }}></div>
            })
          }
        </FadeIn>
      </div >
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
    var showNextPageButton = false;
    if (waitingForAnswer) {
    } else {
      if (datastore.currentBlockIndex !== datastore.blocks.length - 1) {
        showCommandBox = false;
        if (datastore.currentBlockIndex !== datastore.maxBlockIndex) {
          showReturnButton = true;
        } else {
          showNextPageButton = true;
        }
      } else {
        showCommandBox = true;
      }
    }
    commandBox = (
      <div>
        <Button variant="outlined" style={{ visibility: (showReturnButton ? 'visible' : 'hidden') }} onClick={() => {
          datastore.goToLastPage();
        }}>
          Return to current scene
        </Button>
        <Button variant="outlined" style={{ visibility: (showNextPageButton ? 'visible' : 'hidden') }} onClick={() => {
          datastore.goToNextPage();
        }}>
          Read on...
        </Button>
        <Box sx={{ display: 'flex', p: 1 }} style={{ visibility: (showCommandBox ? 'visible' : 'hidden') }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-end', flexGrow: 1 }}>
            <ArrowForwardIos sx={{ color: 'action.active', mr: 1, my: 0.5 }} />
            <TextField id="input-with-sx" label="Tap/Click here" variant="standard" fullWidth multiline onKeyDown={submitIfEnter} inputRef={commandValueRef} ref={commandRef} autoComplete="off" style={{ paddingRight: "10px" }} />
          </Box>
          <Button variant="outlined" onClick={() => {
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

  const loadingFirstLook = (datastore.blocks.length === 0 && getCookie('session_cookie'))
  const hasNoGame = getCookie('session_cookie') === undefined;
  if (waitingForAnswer || loadingFirstLook) {
    ellipses = (
      <React.Fragment>
        <span>Please wait</span>
        <ReactAnimatedEllipsis
          fontSize="3rem"
          marginLeft="5px"
          spacing="0.3rem" />
      </React.Fragment>
    );
  }

  var alertHtml = null;
  var alertIndex = 0;
  if (datastore.alerts.length > 0) {
    alertHtml = (
      datastore.alerts.map((alert: GptifAlert) => {
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
  if (datastore.currentBlock && datastore.currentBlock.imageUrl !== null) {
    gameImageHtml = <img src={datastore.currentBlock.imageUrl} alt="Logo" style={logoStyle} />;
  }

  var gameContent;

  if (hasNoGame) {
    gameContent = (
      <React.Fragment>
        <Stack spacing={2} textAlign='center' alignItems="center"
          justifyContent="center" paddingTop="32px" paddingBottom="32px">
          <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "10px", margin: "10px" }}>
              <Typography style={{ padding: "10px" }}>
                Text adventure games such as Zork, Colossal Caves, and Photopia, have captured the imagation of millions around the World.  I was one of those millions.
              </Typography>
              <Divider variant="middle" />
              <Typography style={{ padding: "10px" }}>
                My parents bought a commodore 64 second-hand from the <b>For Sale</b> section of the city newspaper.  The elderly gentleman was surprised when a 7 year old boy showed up at the doorstep.  He walked me through setting up the computer and loading disks, then handed me a box full of software.  One stood out: <Link href="https://www.myabandonware.com/game/essex-5t/play-5t" target="_blank" rel="noopener">The Essex</Link>.  It came with a hardcover fiction book instead of a manual.  After reading the book, players had to start the game to <s>find out</s> create what happened next.  This mixture of media was magical for me and I credit that moment to my interest in computers.
              </Typography>
              <Divider variant="middle" />
              <Typography style={{ padding: "10px" }}>
                I believe we are at the dawn of a new age in AI.  Large forward models, such as Large Langauge Models, are going to revolutionize how tomorrow's generation works and plays.  The text adventure you are about to play blends the latest AI with a human touch to tell a story about tragedy and friendship.  The Essex was a flawed game, but it captured my heart.  I hope The Fortuna will capture yours.
              </Typography>
            </Paper>
          </Container>
          <Container maxWidth="sm">
            {!waitingForAnswer &&
              <React.Fragment><Paper elevation={6} style={{ padding: "10px", margin: "10px" }}>
                <Typography style={{ padding: "10px" }} textAlign="center">
                  Welcome to the Fortuna.  Press the button to begin.
                </Typography>
              </Paper>
                <Box textAlign='center'>
                  <Button variant="outlined" onClick={submitNewGame} size="large" endIcon={<VideogameAssetIcon />}>Start Game</Button>
                </Box>
              </React.Fragment>
            }
            {waitingForAnswer && <React.Fragment>
              {ellipses}</React.Fragment>}
          </Container>
        </Stack>
      </React.Fragment>
    );
  } else {
    gameContent = (
      <React.Fragment>
        <Grid item xs={12} md={6} style={{ whiteSpace: "normal" }} >
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
            {false && !hasNoGame && datastore.blocks.length > 0 && <Button variant="outlined" onClick={submitNewGame}>{datastore.blocks.length === 0 ? "Start Game" : "Restart Game"}</Button>}
          </div>
        </Grid>
      </React.Fragment>
    );
  }

  return (
    <div className="App" style={{ marginTop: "16px", marginBottom: "32px" /* Cancel out the negative margin from grid */ }}>
      <Grid container spacing={2} alignItems="center"
        justifyContent="center">
        {gameContent}
      </Grid>
    </div>
  );
});

export default App;
