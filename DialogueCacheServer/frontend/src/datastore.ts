import { makeObservable, observable } from "mobx";

class ChatBlock {
  image_url: string | null = null;
  chat_sections: string[] = [];
}

export default class DataStore {
  blocks: ChatBlock[] = [];

  constructor() {
    makeObservable(this, {
      blocks: observable,
    });
  }
}
