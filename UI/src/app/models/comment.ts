export interface IComment {
  id: number;
  date: Date;
  hasBeenEdited: boolean;

  updateDate(): void;
  setAsEdited(): void;
  newValue(value: string): void;
}

export class Comment {
  id: number;
  date: Date;
  hasBeenEdited: boolean;

  constructor(
    private text: string
  ) {
    this.id = Math.floor(Math.random() * 1000000);
    this.date = new Date(Date.now());
    this.hasBeenEdited = false;
  }

  updateDate() {
    this.date = new Date(Date.now());
  }

  setAsEdited() {
    this.hasBeenEdited = true;
  }

  newValue(value: string) {
    this.text = value;
  }

}