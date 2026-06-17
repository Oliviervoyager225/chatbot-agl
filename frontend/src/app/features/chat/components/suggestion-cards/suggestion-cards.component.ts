import { Component, inject, output, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService } from '../../../../core/services/language.service';
import { ChatService } from '../../../../core/services/chat.service';

export interface Suggestion {
  title: string;
  desc:  string;
  icon:  string;
}

export interface DynamicSuggestion {
  title: string;
  desc:  string;
  icon:  string;
}

@Component({
  selector: 'app-suggestion-cards',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './suggestion-cards.component.html',
  styleUrl: './suggestion-cards.component.scss',
})
export class SuggestionCardsComponent {
  readonly selected    = output<string>();
  readonly langService = inject(LanguageService);
  readonly chatService = inject(ChatService);

  readonly cards      = signal<DynamicSuggestion[]>([]);
  readonly refreshing = signal(false);   // refresh silencieux en fond

  constructor() {
    effect(() => {
      const lang = this.langService.current();
      this.loadSuggestions(lang);
    });
  }

  private async loadSuggestions(lang: 'fr' | 'en'): Promise<void> {
    const statics = this.staticFallback(lang);

    // 1. Afficher immédiatement : cache API si dispo, sinon statiques
    const cached = this.chatService.getCachedSuggestions(lang);
    if (cached && cached.length > 0) {
      this.cards.set(this.fill(cached.map(s => ({ ...s, icon: this.iconForTitle(s.title) })), statics));
    } else {
      this.cards.set(statics);
    }

    // 2. Fetch API en fond (silencieux si on avait déjà le cache)
    this.refreshing.set(!cached);
    const fromApi = await this.chatService.getSuggestions(lang);
    this.refreshing.set(false);

    if (fromApi.length > 0) {
      const dynamic = fromApi.map(s => ({ ...s, icon: this.iconForTitle(s.title) }));
      this.cards.set(this.fill(dynamic, statics));
    }
  }

  /** Complète jusqu'à 3 cartes avec les statiques si besoin */
  private fill(dynamic: DynamicSuggestion[], statics: DynamicSuggestion[]): DynamicSuggestion[] {
    const result = [...dynamic];
    for (let i = 0; result.length < 3 && i < statics.length; i++) result.push(statics[i]);
    return result.slice(0, 3);
  }

  private staticFallback(lang: 'fr' | 'en'): DynamicSuggestion[] {
    return this.langService.t().suggestions.map(s => ({ title: s.title, desc: s.desc, icon: s.icon }));
  }

  iconForTitle(title: string): string {
    const t = title.toLowerCase();
    if (/transport|fret|expéd|livraison|cargo|ship|multimod/.test(t)) return 'truck';
    if (/douane|customs|déclar|dédouane|import|export|ac\b|autorisa/.test(t)) return 'shield';
    if (/suivi|tracking|statut|temps réel|real.time|traçab/.test(t)) return 'map-pin';
    if (/document|dossier|conformité|bilan|rapport|projet/.test(t)) return 'document';
    if (/analyse|écart|comparai|audit|innov|durable/.test(t)) return 'chart';
    if (/recherch|tvf|trouv|find|search|groupe|groupage/.test(t)) return 'search';
    return 'document';
  }

  onSelect(title: string, desc: string): void {
    this.selected.emit(desc || title);
  }
}
