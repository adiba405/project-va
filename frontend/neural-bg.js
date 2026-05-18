class NeuralBackground {
  constructor() {
    this.canvas = document.createElement('canvas');
    this.canvas.id = 'neural-bg';
    this.ctx = this.canvas.getContext('2d');

    this.waves = [];
    this.stars = [];
    this.mouse = { x: null, y: null };

    this.dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    this.maxStars = 520;

    this.init();
  }

  init() {
    this.canvas.style.position = 'fixed';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.zIndex = '-1';
    this.canvas.style.pointerEvents = 'none';
    this.canvas.style.opacity = '1';

    document.body.prepend(this.canvas);

    window.addEventListener('resize', () => this.resize());
    window.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });

    this.resize();
    this.createStars();
    this.createNeuralGrid();
    this.animate();
  }

  resize() {
    this.w = window.innerWidth;
    this.h = window.innerHeight;

    this.canvas.width = Math.floor(this.w * this.dpr);
    this.canvas.height = Math.floor(this.h * this.dpr);
    this.canvas.style.height = '100%';

    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

    const targetStars = Math.round(
      Math.min(this.maxStars, Math.max(120, (this.w * this.h) / 9000))
    );
    if (this.stars.length !== targetStars) {
      this.maxStars = targetStars;
      this.createStars();
    }

    this.createNeuralGrid();
  }

  createStars() {
    const count = this.maxStars;
    this.stars = [];

    for (let i = 0; i < count; i++) {
      const z = Math.random();
      this.stars.push({
        x: Math.random() * this.w,
        y: Math.random() * this.h,
        r: 0.5 + z * 1.7,
        a: 0.04 + z * 0.30,
        tw: 0.6 + Math.random() * 1.1,
        ph: Math.random() * Math.PI * 2
      });
    }
  }

  createNeuralGrid() {
    // Minimal, productivity-focused background.
    // No flowing ribbons/waves; instead we draw a faint neural grid and nodes.
    const spacing = Math.round(Math.max(34, Math.min(70, this.w / 18)));
    this.grid = {
      spacing,
      alpha: 0.075,
      lineAlpha: 0.065,
      nodeAlpha: 0.12
    };

    // Sparse nodes
    const cols = Math.ceil(this.w / spacing);
    const rows = Math.ceil(this.h / spacing);
    const nodes = [];

    for (let r = 0; r <= rows; r++) {
      for (let c = 0; c <= cols; c++) {
        // Keep it sparse
        if (Math.random() < 0.18) {
          const x = c * spacing + (Math.random() - 0.5) * (spacing * 0.25);
          const y = r * spacing + (Math.random() - 0.5) * (spacing * 0.25);
          const rad = 0.8 + Math.random() * 1.6;
          const glow = 0.35 + Math.random() * 0.9;
          nodes.push({ x, y, rad, glow });
        }
      }
    }

    this.nodes = nodes;
  }

  drawNeuralGrid() {
    const { spacing, alpha, lineAlpha, nodeAlpha } = this.grid;
    const ctx = this.ctx;

    const t = Date.now() * 0.0002;

    // Ultra-thin connecting lines
    ctx.globalCompositeOperation = 'source-over';
    ctx.lineWidth = 1;
    ctx.strokeStyle = `rgba(102, 255, 242, ${lineAlpha})`;

    ctx.beginPath();
    for (let x = 0; x <= this.w; x += spacing) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.h);
    }
    for (let y = 0; y <= this.h; y += spacing) {
      ctx.moveTo(0, y);
      ctx.lineTo(this.w, y);
    }
    ctx.stroke();

    // Faint nodes + subtle glow pulse
    for (const n of this.nodes) {
      const pulse = 0.6 + 0.4 * Math.sin(t + (n.x + n.y) * 0.0008);
      const a = nodeAlpha * pulse;

      ctx.fillStyle = `rgba(200, 240, 255, ${a})`;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.rad, 0, Math.PI * 2);
      ctx.fill();

      // Very soft outer glow (still low opacity)
      ctx.fillStyle = `rgba(102, 255, 242, ${a * 0.35})`;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.rad * (1.7 + n.glow * 0.5), 0, Math.PI * 2);
      ctx.fill();
    }

    // A couple of faint “connections” between near nodes
    ctx.strokeStyle = `rgba(167, 139, 250, ${alpha * 0.55})`;
    ctx.lineWidth = 0.7;
    ctx.beginPath();
    for (let i = 0; i < this.nodes.length; i++) {
      const a = this.nodes[i];
      // check only a few neighbors for performance
      for (let k = 0; k < 2; k++) {
        const j = (i + 3 + k * 7) % this.nodes.length;
        const b = this.nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < (spacing * 1.45) * (spacing * 1.45)) {
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
        }
      }
    }
    ctx.stroke();
  }

  drawNebula() {
    const ctx = this.ctx;
    const t = Date.now() * 0.00008;

    const gradA = ctx.createRadialGradient(
      this.w * 0.25,
      this.h * 0.20,
      0,
      this.w * 0.25,
      this.h * 0.20,
      this.w * 0.65
    );
    gradA.addColorStop(0, `rgba(90, 210, 255, ${0.08 + 0.03 * Math.sin(t)})`);
    gradA.addColorStop(0.45, `rgba(125, 80, 255, ${0.05 + 0.02 * Math.cos(t * 1.3)})`);
    gradA.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gradA;
    ctx.fillRect(0, 0, this.w, this.h);

    const gradB = ctx.createRadialGradient(
      this.w * 0.78,
      this.h * 0.62,
      0,
      this.w * 0.78,
      this.h * 0.62,
      this.w * 0.65
    );
    gradB.addColorStop(0, `rgba(90, 255, 240, ${0.06 + 0.03 * Math.cos(t * 1.1)})`);
    gradB.addColorStop(0.65, `rgba(170, 110, 255, ${0.035 + 0.02 * Math.sin(t * 0.9)})`);
    gradB.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gradB;
    ctx.fillRect(0, 0, this.w, this.h);
  }

  drawEarthRise() {
    const ctx = this.ctx;
    const t = Date.now() * 0.00006;

    const horizonY = this.h * 0.64;

    // lunar terrain shadow band
    const band = ctx.createLinearGradient(0, horizonY - 80, 0, horizonY + 120);
    band.addColorStop(0, 'rgba(0,0,0,0)');
    band.addColorStop(0.25, 'rgba(8, 10, 18, 0.30)');
    band.addColorStop(1, 'rgba(8, 10, 18, 0.75)');
    ctx.fillStyle = band;
    ctx.fillRect(0, horizonY - 60, this.w, 260);

    const earthX = this.w * 0.74;
    const baseY = horizonY - 95;
    const rise = 28 * Math.sin(t * 1.2);
    const earthY = baseY - rise;

    const radius = Math.min(128, Math.max(72, this.h * 0.095));

    // atmosphere glow
    const glow = ctx.createRadialGradient(
      earthX,
      earthY,
      radius * 0.2,
      earthX,
      earthY,
      radius * 1.38
    );
    glow.addColorStop(0, 'rgba(80, 220, 255, 0.28)');
    glow.addColorStop(0.38, 'rgba(60, 255, 245, 0.12)');
    glow.addColorStop(0.72, 'rgba(170, 95, 255, 0.10)');
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(earthX, earthY, radius * 1.36, 0, Math.PI * 2);
    ctx.fill();

    // planet body
    const body = ctx.createRadialGradient(
      earthX - radius * 0.25,
      earthY - radius * 0.25,
      radius * 0.1,
      earthX,
      earthY,
      radius
    );
    body.addColorStop(0, 'rgba(140, 245, 255, 0.95)');
    body.addColorStop(0.55, 'rgba(50, 140, 255, 0.55)');
    body.addColorStop(1, 'rgba(0, 0, 0, 0.65)');

    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.arc(earthX, earthY, radius, 0, Math.PI * 2);
    ctx.fill();

    // limb highlight
    ctx.strokeStyle = 'rgba(90, 255, 245, 0.48)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(earthX, earthY, radius * 1.01, -Math.PI * 0.25, Math.PI * 0.85);
    ctx.stroke();

    // faint cloud bands
    ctx.globalAlpha = 0.48;
    ctx.strokeStyle = 'rgba(180, 255, 255, 0.22)';
    ctx.lineWidth = 1;
    for (let k = 0; k < 4; k++) {
      const y = earthY + (k - 1.5) * (radius * 0.26);
      ctx.beginPath();
      ctx.ellipse(earthX, y, radius * 0.78, radius * 0.28, 0.2, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  drawWaveRibbons() {
    const ctx = this.ctx;
    const t = Date.now() * 0.001;

    for (const w of this.waves) {
      const baseColor = w.hueMix === 'cyan' ? 'rgba(90, 255, 240,' : 'rgba(175, 95, 255,';

      // outer glow
      ctx.globalCompositeOperation = 'lighter';
      ctx.lineWidth = w.width;
      ctx.strokeStyle = baseColor.replace('rgba(', 'rgba(').replace(/,$/, '') + '0.14)';

      ctx.beginPath();
      for (let x = 0; x <= this.w; x += 10) {
        const y = w.yBase + Math.sin(t * w.speed + x * w.freq + w.phase) * w.amp;
        const mx = this.mouse.x ?? this.w * 0.55;
        const dx = x - mx;
        const influence = Math.max(0, 1 - Math.abs(dx) / 520);
        const wobble = influence * Math.sin(t * 2 + dx * 0.01) * 9;
        const yy = y + wobble;

        if (x === 0) ctx.moveTo(x, yy);
        else ctx.lineTo(x, yy);
      }
      ctx.stroke();

      // bright core
      ctx.strokeStyle = baseColor + '0.55)';
      ctx.beginPath();
      for (let x = 0; x <= this.w; x += 10) {
        const y = w.yBase + Math.sin(t * w.speed + x * w.freq + w.phase) * (w.amp * 0.65);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    ctx.globalCompositeOperation = 'source-over';
  }

  drawStars() {
    const ctx = this.ctx;
    const t = Date.now() * 0.001;

    for (const s of this.stars) {
      const tw = 0.6 + 0.4 * Math.sin(t * s.tw + s.ph);
      ctx.fillStyle = `rgba(235, 245, 255, ${s.a * tw})`;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r * (0.55 + 0.45 * tw), 0, Math.PI * 2);
      ctx.fill();
    }
  }

  animate() {
    const ctx = this.ctx;

    // Premium dark matte gradient (minimal, productivity-focused)
    ctx.clearRect(0, 0, this.w, this.h);

    const bg = ctx.createLinearGradient(0, 0, 0, this.h);
    bg.addColorStop(0, '#050A18'); // deep navy
    bg.addColorStop(0.45, '#0B0F18');
    bg.addColorStop(1, '#000000'); // black
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, this.w, this.h);

    // Soft ambient glows behind sections (low opacity)
    const t = Date.now() * 0.00015;

    const glowCyan = ctx.createRadialGradient(this.w * 0.18, this.h * 0.28, 0, this.w * 0.18, this.h * 0.28, this.w * 0.55);
    glowCyan.addColorStop(0, `rgba(56, 255, 244, ${0.10 + 0.02 * Math.sin(t)})`);
    glowCyan.addColorStop(0.35, 'rgba(56, 255, 244, 0.05)');
    glowCyan.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glowCyan;
    ctx.fillRect(0, 0, this.w, this.h);

    const glowViolet = ctx.createRadialGradient(this.w * 0.72, this.h * 0.38, 0, this.w * 0.72, this.h * 0.38, this.w * 0.6);
    glowViolet.addColorStop(0, `rgba(167, 139, 250, ${0.085 + 0.02 * Math.cos(t * 1.2)})`);
    glowViolet.addColorStop(0.4, 'rgba(167, 139, 250, 0.04)');
    glowViolet.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glowViolet;
    ctx.fillRect(0, 0, this.w, this.h);

    // Neural grid + nodes
    this.drawNeuralGrid();

    // Sparse floating particles with gentle blur (very subtle)
    this.drawStars();

    requestAnimationFrame(() => this.animate());
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new NeuralBackground();
});

