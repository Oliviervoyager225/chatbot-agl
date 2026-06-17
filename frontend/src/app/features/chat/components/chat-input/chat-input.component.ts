import { Component, ElementRef, ViewChild, inject, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../../../core/services/chat.service';
import { LanguageService } from '../../../../core/services/language.service';

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-input.component.html',
  styleUrl: './chat-input.component.scss',
})
export class ChatInputComponent {
  @ViewChild('textarea') textareaRef!: ElementRef<HTMLTextAreaElement>;

  readonly chatService   = inject(ChatService);
  readonly langService   = inject(LanguageService);
  readonly submitted     = output<string>();

  readonly isRecording   = signal(false);

  get t()         { return this.langService.t(); }
  get isLoading() { return this.chatService.isLoading(); }

  message = '';

  private recognition: any = null;

  setMessage(value: string): void {
    this.message = value;
    setTimeout(() => this.autosize());
  }

  onKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.send();
    }
  }

  send(): void {
    const text = this.message.trim();
    if (!text || this.isLoading) return;
    this.submitted.emit(text);
    this.message = '';
    setTimeout(() => this.autosize());
  }

  onMicClick(): void {
    if (this.isLoading) return;

    // Exclusivement vocal — jamais d'envoi de texte
    if (this.isRecording()) {
      this.stopVoice();
    } else {
      this.startVoice();
    }
  }

  private startVoice(): void {
    const SR = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
    if (!SR) {
      alert('La reconnaissance vocale n\'est pas supportée par ce navigateur.');
      return;
    }

    this.recognition = new SR();
    this.recognition.lang        = this.langService.current() === 'fr' ? 'fr-FR' : 'en-US';
    this.recognition.continuous  = false;
    this.recognition.interimResults = true;

    this.recognition.onstart = () => this.isRecording.set(true);

    this.recognition.onresult = (event: any) => {
      let transcript = '';
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      this.message = transcript;
      setTimeout(() => this.autosize());
    };

    this.recognition.onend = () => {
      this.isRecording.set(false);
      // Auto-send if we got a result
      if (this.message.trim()) {
        setTimeout(() => this.send(), 200);
      }
    };

    this.recognition.onerror = () => this.isRecording.set(false);

    this.recognition.start();
  }

  private stopVoice(): void {
    this.recognition?.stop();
    this.isRecording.set(false);
  }

  autosize(): void {
    const el = this.textareaRef?.nativeElement;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  }
}
