import { Injectable, signal, computed } from '@angular/core';

export type Lang = 'fr' | 'en';

const TRANSLATIONS = {
  fr: {
    newChat: 'Nouvelle conversation',
    search: 'Rechercher',
    explore: 'Explorer',
    library: 'Bibliothèque',
    history: 'Historique',
    today: "Aujourd'hui",
    exportChat: 'Exporter la conversation',
    upgrade: 'Mettre à niveau',
    greeting: 'Bonjour, Jackson',
    greetingQuestion: 'Comment puis-je vous aider aujourd\'hui ?',
    inputPlaceholder: 'Posez-moi n\'importe quelle question...',
    deeperResearch: 'Recherche',
    savedPrompts: 'Invites sauvegardées',
    attachFile: 'Joindre un fichier',
    footerText: 'Découvrez tous les services AGL',
    joinDiscord: 'aglgroup.com',
    suggestions: [
      {
        title: 'Transport multimodal',
        desc: 'Optimisez vos flux en combinant maritime, aérien et terrestre.',
        icon: 'truck',
      },
      {
        title: 'Suivi des expéditions',
        desc: 'Consultez en temps réel le statut de vos marchandises en transit.',
        icon: 'map-pin',
      },
      {
        title: 'Conformité douanière',
        desc: 'Vérifiez vos documents d\'import/export et obligations réglementaires.',
        icon: 'shield',
      },
    ],
  },
  en: {
    newChat: 'New chat',
    search: 'Search',
    explore: 'Explore',
    library: 'Library',
    history: 'History',
    today: 'Today',
    exportChat: 'Export chat',
    upgrade: 'Upgrade',
    greeting: 'Hello, Jackson',
    greetingQuestion: 'How can I assist you today?',
    inputPlaceholder: 'Ask me anything...',
    deeperResearch: 'Search',
    savedPrompts: 'Saved prompts',
    attachFile: 'Attach file',
    footerText: 'Discover all AGL services',
    joinDiscord: 'aglgroup.com',
    suggestions: [
      {
        title: 'Multimodal transport',
        desc: 'Optimize your flows combining sea, air and land freight.',
        icon: 'truck',
      },
      {
        title: 'Shipment tracking',
        desc: 'Check the real-time status of your goods in transit.',
        icon: 'map-pin',
      },
      {
        title: 'Customs compliance',
        desc: 'Verify your import/export documents and regulatory requirements.',
        icon: 'shield',
      },
    ],
  },
};

@Injectable({ providedIn: 'root' })
export class LanguageService {
  readonly current = signal<Lang>('fr');
  readonly t = computed(() => TRANSLATIONS[this.current()]);

  setLang(lang: Lang): void {
    this.current.set(lang);
  }
}
