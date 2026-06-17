import { Component, ElementRef, ViewChild, effect, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../../../core/services/chat.service';
import { MarkdownPipe } from '../../../../core/pipes/markdown.pipe';

@Component({
  selector: 'app-chat-messages',
  standalone: true,
  imports: [CommonModule, MarkdownPipe],
  templateUrl: './chat-messages.component.html',
  styleUrl: './chat-messages.component.scss',
})
export class ChatMessagesComponent {
  @ViewChild('messagesEnd') private messagesEnd!: ElementRef;

  readonly chatService = inject(ChatService);
  readonly messages = this.chatService.messages;
  readonly isLoading = this.chatService.isLoading;
  readonly error = this.chatService.error;

  constructor() {
    effect(() => {
      this.messages();
      setTimeout(() => this.scrollToBottom(), 50);
    });
  }

  private scrollToBottom(): void {
    this.messagesEnd?.nativeElement.scrollIntoView({ behavior: 'smooth' });
  }
}
