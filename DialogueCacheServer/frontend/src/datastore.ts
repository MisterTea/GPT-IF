import { makeAutoObservable } from "mobx";

export class ChatBlock {
  imageUrl: string | null = null;
  chatSections: string[] = [];
}

export default class DataStore {
  blocks: ChatBlock[] = [];
  currentBlock: ChatBlock|null = null;

  constructor() {
    makeAutoObservable(this);
    // makeObservable(this, {
    //   blocks: observable,
    // });
  }

  newGame(chatBlock: ChatBlock) {
    this.blocks.length = 0;
    this.blocks.push(chatBlock);
    this.currentBlock = chatBlock;
  }

  addChatBlock(chatBlock: ChatBlock) {
    this.blocks.push(chatBlock);
    this.currentBlock = chatBlock;
  }
}
