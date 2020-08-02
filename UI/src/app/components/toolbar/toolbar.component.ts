import { Component, ElementRef, ViewChild, OnInit } from '@angular/core';

import { OpenMappingDialog } from '../../app.component';
import { BridgeService } from '../../services/bridge.service';
import { CommonUtilsService } from '../../services/common-utils.service';
import { UploadService } from '../../services/upload.service';
import { StoreService } from '../../services/store.service';
import { stringify } from 'querystring';

@Component({
  selector: 'app-toolbar',
  styleUrls: ['./toolbar.component.scss'],
  templateUrl: './toolbar.component.html'
})
export class ToolbarComponent implements OnInit {
  @ViewChild('sourceUpload', { static: true }) fileInput: ElementRef;

  cdmVersion: string;
  reportName: string;
  constructor(
    private bridgeService: BridgeService,
    private commonUtilsService: CommonUtilsService,
    private uploadService: UploadService,
    private storeService: StoreService
  ) {

  }

  ngOnInit(){
    this.storeService.state$.subscribe(res => {
      this.cdmVersion = res['version'] ? `CDM v${res['version']}` : 'CDM version';
      this.reportName = res['report'] ? res['report'] : 'Report name';
    });
  }

  resetAllMappings() {
    this.commonUtilsService.resetMappingsWithWarning();
  }

  openSaveMappingDialog() {
  this.commonUtilsService.saveMappingDialog();
  }

  openLoadMappingDialog() {
    this.commonUtilsService.loadMappingDialog();
    }

  onOpenSourceClick() {
    this.uploadService.onFileInputClick(this.fileInput);
  }

  onFileUpload(event: Event) {
    this.uploadService.onFileChange(event);
  }

  openSetCDMDialog() {
    this.commonUtilsService.openSetCDMDialog();
  }

  resetSourceAndTarget() {
    this.commonUtilsService.resetSourceAndTargetWithWarning();
  }
}
