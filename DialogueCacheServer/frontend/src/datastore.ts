import { makeAutoObservable } from "mobx";

export class ChatBlock {
  imageUrl: string | null = null;
  chatSections: string[] = [];
}

export default class DataStore {
  blocks: ChatBlock[] = [];

  constructor() {
    makeAutoObservable(this);
    // makeObservable(this, {
    //   blocks: observable,
    // });
  }

  newGame(chatBlock: ChatBlock) {
    this.blocks.length = 0;
    this.blocks.push(chatBlock);
    console.log(this.blocks);
  }

  addChatBlock(chatBlock: ChatBlock) {
    this.blocks.push(chatBlock);
  }
}
