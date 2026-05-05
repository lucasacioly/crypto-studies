import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

import { AppComponent } from './app.component';
import {
  DashboardComponent,
  MempoolCardComponent,
  BlockchainCardComponent,
  EventActivityCardComponent,
  BlockchainReorgDetectorComponent,
  LatestEventsCardComponent
} from './components';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    MempoolCardComponent,
    BlockchainCardComponent,
    EventActivityCardComponent,
    BlockchainReorgDetectorComponent,
    LatestEventsCardComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatCardModule,
    MatButtonModule,
    CommonModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
