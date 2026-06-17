import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService } from '../../../../core/services/language.service';
import { ChatService } from '../../../../core/services/chat.service';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss',
})
export class TopbarComponent {
  readonly langService  = inject(LanguageService);
  readonly chatService  = inject(ChatService);

  get t()         { return this.langService.t(); }
  get apiOnline() { return this.chatService.apiOnline(); }
}
