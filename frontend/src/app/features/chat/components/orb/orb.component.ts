import { Component } from '@angular/core';

@Component({
  selector: 'app-orb',
  standalone: true,
  template: `
    <div class="orb-wrap">
      <div class="orb-glow"></div>
      <div class="orb"></div>
      <img src="logo-agl.png" alt="AGL" class="orb-logo" />
    </div>
  `,
  styleUrl: './orb.component.scss',
})
export class OrbComponent {}
