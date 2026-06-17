import { Component, ViewChild, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { TopbarComponent } from './components/topbar/topbar.component';
import { OrbComponent } from './components/orb/orb.component';
import { ChatInputComponent } from './components/chat-input/chat-input.component';
import { ChatMessagesComponent } from './components/chat-messages/chat-messages.component';
import { SuggestionCardsComponent } from './components/suggestion-cards/suggestion-cards.component';
import { ChatService } from '../../core/services/chat.service';
import { HistoryService } from '../../core/services/history.service';
import { LanguageService, Lang } from '../../core/services/language.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    SidebarComponent,
    TopbarComponent,
    OrbComponent,
    ChatInputComponent,
    ChatMessagesComponent,
    SuggestionCardsComponent,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent {
  @ViewChild(ChatInputComponent) chatInput!: ChatInputComponent;

  readonly chatService = inject(ChatService);
  readonly historyService = inject(HistoryService);
  readonly langService = inject(LanguageService);

  constructor() {
    this.chatService.checkHealth();
  }

  readonly hasMessages = this.chatService.hasMessages;
  readonly langMenuOpen = signal(false);

  get t() { return this.langService.t(); }
  get currentLang() { return this.langService.current(); }

  onSend(text: string): void {
    if (!this.hasMessages()) {
      this.historyService.addItem(text, crypto.randomUUID());
    }
    this.chatService.sendMessage(text);
  }

  onSuggestionSelected(text: string): void {
    this.chatInput.setMessage(text);
  }

  onNewChat(): void {}

  toggleLangMenu(): void {
    this.langMenuOpen.update(v => !v);
  }

  selectLang(lang: Lang): void {
    this.langService.setLang(lang);
    this.langMenuOpen.set(false);
  }
}
