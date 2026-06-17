import { Component, inject, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HistoryService } from '../../../../core/services/history.service';
import { ChatService } from '../../../../core/services/chat.service';
import { LanguageService } from '../../../../core/services/language.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  readonly historyService = inject(HistoryService);
  readonly chatService = inject(ChatService);
  readonly langService = inject(LanguageService);

  readonly newChat = output<void>();
  readonly todayItems = this.historyService.history;

  get t() { return this.langService.t(); }

  onNewChat(): void {
    this.chatService.clearSession();
    this.newChat.emit();
  }

  onHistoryClick(id: string): void {
    this.historyService.setActive(id);
  }
}
