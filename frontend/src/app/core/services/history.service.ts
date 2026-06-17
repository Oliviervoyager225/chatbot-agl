import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HistoryItem } from '../models/message.model';

@Injectable({ providedIn: 'root' })
export class HistoryService {
  private readonly http = inject(HttpClient);

  readonly history = signal<HistoryItem[]>([
    { id: '1', title: 'Create a detailed 7-day sprint plan f...', preview: '', date: new Date(), active: true },
    { id: '2', title: 'Draft a concise email to stakeholder...', preview: '', date: new Date(), active: false },
    { id: '3', title: "Analyze the 'Eisenhower Matrix' an...", preview: '', date: new Date(), active: false },
  ]);

  readonly activeId = signal<string | null>('1');

  setActive(id: string): void {
    this.activeId.set(id);
    this.history.update(items =>
      items.map(i => ({ ...i, active: i.id === id }))
    );
  }

  addItem(title: string, id: string): void {
    const newItem: HistoryItem = {
      id,
      title: title.length > 40 ? title.slice(0, 40) + '...' : title,
      preview: '',
      date: new Date(),
      active: true,
    };
    this.history.update(items => [newItem, ...items.map(i => ({ ...i, active: false }))]);
    this.activeId.set(id);
  }

  // Will be wired once endpoints are provided
  loadHistory(): void {
    this.http.get<HistoryItem[]>('history').subscribe({
      next: items => this.history.set(items),
    });
  }
}
