import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

marked.use({ breaks: true, gfm: true });

@Pipe({ name: 'markdown', standalone: true })
export class MarkdownPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string): SafeHtml {
    if (!value) return '';

    let text = value;

    // Fix 1 : "** texte**" → "**texte**"
    // CommonMark rejette ** ouvrant suivi d'un espace
    text = text.replace(/\*\*\s+([^*\n]+?)\*\*/g, '**$1**');

    // Fix 2 : ":**mot" → ":** mot"
    // ** fermant précédé de : et collé au mot suivant sans espace
    text = text.replace(/:\*\*([A-Za-zÀ-ÿ('])/g, ':** $1');

    // Fix 3 : double ":" consécutifs " : : " → " : "
    // Artefact de streaming : colon de fin d'intro + colon de début d'item fusionnés
    text = text.replace(/\s*:\s*:\s*/g, ' : ');

    // Fix 4 : "**mot**mot" → "**mot** mot"
    // ** fermant collé au mot suivant sans espace  ex: "**Live**et"
    text = text.replace(/(\w)\*\*([A-Za-zÀ-ÿ])/g, '$1** $2');

    // Fix 5 : ":Majuscule" → ": Majuscule"
    // Colon de fin d'intro collé directement à la lettre suivante sans espace
    text = text.replace(/:([A-ZÀÂÉÈÊËÎÏÔÙÛÜ])/g, ': $1');

    // Fix 6 : "Sources :" toujours sur son propre paragraphe
    text = text.replace(/([^\n])\n?(Sources\s*:)/gi, '$1\n\nSources :');

    // Auto-linker les URLs nues
    text = text.replace(
      /(^|[\s\n])(https?:\/\/[^\s)\]\n"'`<>]+)/gm,
      (_, pre, url) => `${pre}[${url}](${url})`
    );

    let html = marked.parse(text) as string;

    // Post-process : retirer les ** résiduels non convertis en gras (ouverture perdue en streaming)
    html = html.replace(/\*\*/g, '');

    // Liens dans un nouvel onglet
    html = html.replace(/<a href=/g, '<a target="_blank" rel="noopener noreferrer" href=');

    // Bloc Sources : détecter "Sources :" et entourer le contenu d'un bloc stylé
    html = html.replace(
      /(<p>)\s*(Sources\s*:)\s*([\s\S]*?)(<\/p>)/gi,
      (_, open, label, body, close) => {
        const links = body
          .split(/<br\s*\/?>/)
          .map((l: string) => l.trim())
          .filter((l: string) => l.length > 0)
          .map((l: string) => `<div class="source-link">${l}</div>`)
          .join('');
        return `<div class="sources-block"><span class="sources-label">Sources :</span>${links}</div>`;
      }
    );

    return this.sanitizer.bypassSecurityTrustHtml(html);
  }
}
