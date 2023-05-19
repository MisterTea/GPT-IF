import { Marked } from "@ts-stack/markdown";
import { makeAutoObservable } from "mobx";
import { getCookie } from "typescript-cookie";
import fetchPlus from "./FetchPlus";

export var API_SERVER_BASE: string = "/";
if (window.location.hostname.endsWith("amazonaws.com")) {
  API_SERVER_BASE = "https://90rjg2sbkg.execute-api.us-east-1.amazonaws.com/dev/";
}

export class ChatBlock {
  imageUrl: string | null = null;
  chatSections: string[] = [];
}

export default class DataStore {
  blocks: ChatBlock[] = [];
  currentBlockIndex: number = -1;
  gameImageUrl: string | null = null;
  feedbackModal: boolean = false;

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
      this.submitNewGame()
    }
  }

  setGameImage(image_url: string) {
    this.gameImageUrl = image_url;
  }

  createChatBlockFromResponse(responseResults: any[]) {
    const chatBlock = new ChatBlock();
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
        const image_id = responseText.split(" ")[1];
        const image_url = API_SERVER_BASE + "api/ai_image/" + image_id;
        console.log("GOT IMAGE: " + image_url);
        this.setGameImage(image_url);
        return null;
      }
      return Marked.parse(responseText);
    }).filter(response => response !== null) as string[];
    chatBlock.chatSections = chatSections;
    return chatBlock;
  }

  submitNewGame() {
    console.log("STARTING NEW GAME");
    return fetchPlus(API_SERVER_BASE + "api/begin_game", {
      method: "POST",
      credentials: 'include',
    }, 3).then((responseResults: any[]) => {
      const chatBlock = this.createChatBlockFromResponse(responseResults);
      this.newGame(chatBlock);
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
      const chatBlock = this.createChatBlockFromResponse(responseResults);
      chatBlock.chatSections.unshift("> " + command)
      this.addChatBlock(chatBlock);
    })
  }

  newGame(chatBlock: ChatBlock) {
    this.blocks.length = 0;
    this.blocks.push(chatBlock);
    this.currentBlockIndex = 0;
  }

  addChatBlock(chatBlock: ChatBlock) {
    this.blocks.push(chatBlock);
    this.currentBlockIndex = this.blocks.length-1;
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
}
