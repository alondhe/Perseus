import { Injectable } from '@angular/core';
import { VocabSearchMode, VocabSearchReqParams } from './vocabulary-search.service';
import { FilterValue } from '../vocabulary-search/filter-list/filter-list.component';
import { Concept } from '../vocabulary-search/concept';
import { Filter } from '../vocabulary-search/filter-item/filter-item.component';

export interface VocabSearchState {
  requestParams: VocabSearchReqParams;
  mode: VocabSearchMode;
  selectedFilters: FilterValue[];
  concepts: Concept[];
  currentPage: number;
  pageCount: number;
  filters: Filter[];
  movableIndexes: {second: number; third: number};
}

@Injectable({
  providedIn: 'root'
})
export class VocabularySearchStateService {

  private searchState: VocabSearchState;

  constructor() { }

  get state() {
    return this.searchState;
  }

  set state(state: VocabSearchState) {
    this.searchState = state;
  }
}
