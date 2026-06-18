import { Injectable, inject, signal, computed, NgZone } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { Message, ChatSession, ApiHealthResponse } from '../models/message.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http   = inject(HttpClient);
  private readonly zone   = inject(NgZone);

  // Cache suggestions par langue pour éviter les re-fetch
  private readonly suggestionsCache = new Map<string, Array<{ title: string; desc: string }>>();

  // ── State ────────────────────────────────────────────────────────────────
  readonly messages  = signal<Message[]>([]);
  readonly isLoading = signal(false);
  readonly sessionId = signal<string | null>(null);
  readonly error     = signal<string | null>(null);
  readonly apiOnline = signal<boolean | null>(null);

  readonly hasMessages = computed(() => this.messages().length > 0);

  private readonly _newMessage$ = new Subject<Message>();
  readonly newMessage$ = this._newMessage$.asObservable();

  // ── Health check ─────────────────────────────────────────────────────────
  checkHealth(): void {
    fetch(`${environment.apiUrl}/health`)
      .then(res => res.json())
      .then(data => this.zone.run(() => this.apiOnline.set(data?.status === 'ok')))
      .catch(() => this.zone.run(() => this.apiOnline.set(false)));
  }

  // ── Send message (streaming SSE) ─────────────────────────────────────────
  sendMessage(content: string): void {
    if (!content.trim() || this.isLoading()) return;

    const userMsg = this.buildMessage('user', content);
    this.messages.update(msgs => [...msgs, userMsg]);
    this.isLoading.set(true);
    this.error.set(null);

    // Placeholder du message assistant (sera rempli token par token)
    const assistantMsg = this.buildMessage('assistant', '');
    assistantMsg.isStreaming = true;
    this.messages.update(msgs => [...msgs, assistantMsg]);

    this.streamChat(content, assistantMsg.id);
  }

  private async streamChat(question: string, assistantId: string): Promise<void> {
    try {
      const res = await fetch(`${environment.apiUrl}/chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader  = res.body!.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Découper sur le délimiteur d'événement SSE \n\n
        const events = buffer.split('\n\n');
        buffer = events.pop() ?? '';  // garde l'événement incomplet

        for (const event of events) {
          if (!event.startsWith('data:')) continue;

          // Retirer le préfixe "data: " ou "data:"
          const raw   = event.startsWith('data: ') ? event.slice(6) : event.slice(5);
          // ligne data vide = le modèle a émis \n ; sinon garder le contenu tel quel
          const token = raw === '' ? '\n' : raw;
          if (token.trim() === '[DONE]') continue;

          this.zone.run(() => {
            this.messages.update(msgs =>
              msgs.map(m =>
                m.id === assistantId
                  ? { ...m, content: m.content + token }
                  : m
              )
            );
          });
        }
      }

      // Fin du streaming
      this.zone.run(() => {
        this.messages.update(msgs =>
          msgs.map(m =>
            m.id === assistantId ? { ...m, isStreaming: false } : m
          )
        );
        this._newMessage$.next(
          this.messages().find(m => m.id === assistantId)!
        );
        this.isLoading.set(false);
      });

    } catch (err: any) {
      this.zone.run(() => {
        // Retire le placeholder vide en cas d'erreur
        this.messages.update(msgs => msgs.filter(m => m.id !== assistantId));
        const msg = err.message?.includes('Failed to fetch')
          ? 'Impossible de joindre le serveur. Vérifiez que le backend est démarré.'
          : `Erreur : ${err.message}`;
        this.error.set(msg);
        this.isLoading.set(false);
      });
    }
  }

  // ── Dynamic suggestions ───────────────────────────────────────────────────

  /** Retourne le cache immédiatement (si dispo) et lance un refresh en fond */
  getCachedSuggestions(lang: 'fr' | 'en'): Array<{ title: string; desc: string }> | null {
    return this.suggestionsCache.get(lang) ?? null;
  }

  async getSuggestions(lang: 'fr' | 'en'): Promise<Array<{ title: string; desc: string }>> {
    const prompt = lang === 'fr'
      ? 'Assistant AGL logistique. Donne 3 suggestions COURTES. Format STRICT, rien d\'autre:\n1. [titre 3 mots max] | [phrase courte 10 mots max]\n2. [titre 3 mots max] | [phrase courte 10 mots max]\n3. [titre 3 mots max] | [phrase courte 10 mots max]'
      : 'AGL logistics assistant. Give 3 SHORT suggestions. STRICT format, nothing else:\n1. [title 3 words max] | [short phrase 10 words max]\n2. [title 3 words max] | [short phrase 10 words max]\n3. [title 3 words max] | [short phrase 10 words max]';

    try {
      const res = await fetch(`${environment.apiUrl}/chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question: prompt }),
      });

      if (!res.ok) return [];

      const reader  = res.body!.getReader();
      const decoder = new TextDecoder();
      let   full    = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split('\n')) {
          if (line.startsWith('data:') && !line.includes('[DONE]'))
            full += line.slice(5);
        }
      }

      const parts = full.split(/\|\||\n/).map(p => p.trim()).filter(Boolean);
      const items: Array<{ title: string; desc: string }> = [];

      for (const part of parts) {
        const clean = part.replace(/^\d+\.\s*/, '').trim();
        if (!clean) continue;
        const sep   = clean.indexOf('|');
        const title = sep !== -1 ? clean.slice(0, sep).trim() : clean;
        const raw   = sep !== -1 ? clean.slice(sep + 1).trim() : '';
        // Nettoyer les URLs et liens Markdown de la description
        const desc  = raw
          .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // [texte](url) → texte
          .replace(/https?:\/\/\S+/g, '')            // URLs nues
          .replace(/\s{2,}/g, ' ')
          .trim()
          .slice(0, 100);                             // max 100 chars
        if (title.length > 2) items.push({ title, desc });
        if (items.length === 3) break;
      }

      if (items.length > 0) this.suggestionsCache.set(lang, items);
      return items;

    } catch {
      return [];
    }
  }

  // ── Session management ────────────────────────────────────────────────────
  getSessions(): Observable<ChatSession[]> {
    return this.http.get<ChatSession[]>('/sessions');
  }

  getSession(id: string): Observable<ChatSession> {
    return this.http.get<ChatSession>(`/sessions/${id}`);
  }

  loadSession(session: ChatSession): void {
    this.sessionId.set(session.id);
    this.messages.set(session.messages);
  }

  clearSession(): void {
    this.messages.set([]);
    this.sessionId.set(null);
    this.error.set(null);
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  private buildMessage(role: Message['role'], content: string, id?: string): Message {
    return {
      id:        id ?? crypto.randomUUID(),
      role,
      content,
      timestamp: new Date(),
    };
  }
}
