import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'app-db-settings-form',
  templateUrl: './db-settings-form.component.html',
  styleUrls: [
    '../connect-form.component.scss',
    '../../../styles/scan-data-form.scss',
    '../../../styles/scan-data-connect-form.scss'
  ]
})
export class DbSettingsFormComponent {

  @Input()
  form: FormGroup;
}
