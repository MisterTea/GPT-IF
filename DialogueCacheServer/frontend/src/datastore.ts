import { AlertColor } from "@mui/material";
import { Marked } from "@ts-stack/markdown";
import { makeAutoObservable } from "mobx";
import { getCookie } from "typescript-cookie";
import fetchPlus from "./FetchPlus";

export var API_SERVER_BASE: string = "/";
if (window.location.hostname.endsWith("amazonaws.com")) {
  API_SERVER_BASE = "https://90rjg2sbkg.execute-api.us-east-1.amazonaws.com/dev/";
}

export interface GptifAlert {
  message: string;
  title: string;
  severity: AlertColor;
  duration: number;
}

export class ChatBlock {
  imageUrl: string | null = null;
  chatSections: string[] = [];
}

export default class DataStore {
  blocks: ChatBlock[] = [];
  maxBlockIndex: number = -1;
  feedbackModal: boolean = false;
  _currentBlockIndex: number = -1;

  get currentBlockIndex(): number {
    return this._currentBlockIndex;
  }

  set currentBlockIndex(i: number) {
    this._currentBlockIndex = i;
    this.maxBlockIndex = Math.max(i, this.maxBlockIndex);
  }

  alerts:GptifAlert[] = [];

  constructor() {
    makeAutoObservable(this);
    // makeObservable(this, {
    //   blocks: observable,
    // });

    if (getCookie('session_cookie')) {
      if (this.blocks.length === 0) {
        this.submitCommand("LOOK");
      }
    } else {
      // Start a new game right when the browser window opens
      //this.submitNewGame();
    }
  }

  createChatBlocksFromResponse(responseResults: any[]) {
    const chatBlocks = []
    var chatBlock = new ChatBlock();
    chatBlocks.push(chatBlock);
    const chatSections = responseResults.map((responseResult: any[]) => {
      var responseText = responseResult[0];
      if (responseResult[1] !== null) {
        //const colorHtmlMap = new Map<string, string[]>();
        //colorHtmlMap.set("yellow", ["<span style=\"color:yellow\">", "</span>"]);
        //const htmlResult: string[] | undefined = colorHtmlMap.get(responseResult[1]);
        //if (htmlResult === undefined) {
        //throw "Oops: " + responseResult[1];
        //}
        responseText = "[" + responseResult[1] + "]" + responseText + "[/]";
      }
  
      // Replace rich tags with spans
      const acceptedTags = ["yellow", "blue", "bright_blue bold", "yellow bold", "purple", "green", "light_green", "red on black"]
      responseText = responseText.replaceAll("[/]", "</span>")
      acceptedTags.forEach(acceptedTag => {
        responseText = responseText.replaceAll("[" + acceptedTag + "]", "<span class=\"game_markdown_" + acceptedTag.replaceAll(" ", "_") + "\">")
      });
      if (responseText.includes("%%IMAGE%%")) {
        return responseText;
      }

      return Marked.parse(responseText);
    }).filter(response => response !== null) as string[];

    chatSections.forEach(chatSection => {
      if (chatSection.includes("Press enter to continue...")) {
        chatBlock = new ChatBlock();
        chatBlocks.push(chatBlock);
        return;
      }
      if(chatSection.includes("%%IMAGE%%")) {
        const image_id = chatSection.split(" ")[1];
        const image_url = API_SERVER_BASE + "api/ai_image/" + image_id;
        console.log("GOT IMAGE: " + image_url);
        chatBlock.imageUrl = image_url;
        return;
      }
      chatBlock.chatSections.push(chatSection);
    });
    return chatBlocks;
  }

  submitNewGame() {
    console.log("STARTING NEW GAME");
    return fetchPlus(API_SERVER_BASE + "api/begin_game", {
      method: "POST",
      credentials: 'include',
    }, 3).then((responseResults: any[]) => {
      const chatBlocks = this.createChatBlocksFromResponse(responseResults);
      this.newGame(chatBlocks);
      //setWaitingForAnswer(false);
      //window.scrollTo(0, 0);
    });
  }

  submitCommand(command: string) {
    return fetchPlus(API_SERVER_BASE + "api/handle_input", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ "command": command }),
      credentials: 'include',
    }, 3).then((responseResults: any[]) => {
      //const responseResults = await value.json();
      console.log(responseResults);
      const chatBlocks = this.createChatBlocksFromResponse(responseResults);
      chatBlocks[0].chatSections.unshift("> " + command)
      this.addChatBlocks(chatBlocks);
    })
  }

  newGame(chatBlocks: ChatBlock[]) {
    this.blocks.length = 0;
    this.blocks = this.blocks.concat(chatBlocks);
    this.currentBlockIndex = this.maxBlockIndex = 0;
  }

  addChatBlocks(chatBlocks: ChatBlock[]) {
    this.currentBlockIndex = this.blocks.length;
    this.blocks = this.blocks.concat(chatBlocks);
  }

  get currentBlock() {
    if (this.currentBlockIndex === -1) {
      return null
    }
    return this.blocks[this.currentBlockIndex];
  }

  goToLastPage() {
    this.goToPage(this.blocks.length-1);
  }

  goToNextPage() {
    if (this.currentBlockIndex === this.blocks.length-1) {
      throw Error("Tried to go to the next page when at the end");
    }
    this.goToPage(this.currentBlockIndex + 1);
  }

  goToPage(value:number) {
    console.log("GOING TO PAGE: " + (value));
    this.currentBlockIndex = value;
  }

  openFeedback() {
    console.log("FEEDBACK IS OPEN");
    this.feedbackModal = true;
  }

  closeFeedback() {
    this.feedbackModal = false;
  }

  handleFeedback(feedback: string) {
    if (feedback.length === 0) {
      this.feedbackModal = false;
      return;
    }

    return fetchPlus(API_SERVER_BASE + "api/feedback", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ "feedback": feedback }),
      credentials: 'include',
    }, 3).then(() => {
      this.closeFeedback();
    }).catch((reason: any) => {
      this.closeFeedback();
    });
  }

  addAlert(alert:GptifAlert) {
    this.alerts.push(alert);
  }

  updateAlerts() {
    this.alerts.forEach(alert => {
      alert.duration -= 1;
    });
    this.alerts = this.alerts.filter((alert) => {
      return alert.duration > 0;
    });
  }
}
