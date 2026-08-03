# PedroIA Web — Site oficial

Landing page premium do PedroIA — **Next.js 14 + TypeScript + Tailwind CSS + GSAP (ScrollTrigger) + Three.js**.

## Estrutura

```
web/
├── app/                # App Router (layout, página, estilos globais, SEO)
│   ├── layout.tsx      # fontes (Inter + Space Grotesk) e metadados/SEO
│   ├── page.tsx        # monta todas as seções
│   └── globals.css
├── components/         # seções da landing (Hero, PowerCards, CopilotDemo, ...)
│   └── ParticlesBackground.tsx   # rede neural 3D (Three.js) no Hero
├── lib/                # helpers (GSAP reveal, links)
├── public/             # favicon e assets
├── install.sh          # instalador automático
└── package.json
```

## Rodar localmente

```bash
bash install.sh
# ou manualmente:
npm install
npm run dev        # http://localhost:3000
```

## Build de produção

```bash
npm run build
npm start
```

## Deploy na Vercel (recomendado)

1. Suba o repositório no GitHub.
2. Em https://vercel.com → **New Project** → importe o repositório.
3. **Root Directory:** `PedroIA/web`
4. A Vercel detecta Next.js automaticamente. Clique em **Deploy**.
5. HTTPS e domínio próprio são configurados nas settings do projeto.

## Personalização

- **Links:** edite `lib/links.ts` (Marketplace, GitHub, docs).
- **Cores/tema:** `tailwind.config.ts` (roxo IA, azul neon, preto profundo).
- **SEO:** `app/layout.tsx` (title, description, Open Graph).

## Performance & acessibilidade

- Fontes otimizadas via `next/font` (sem FOUT).
- Animações respeitam `prefers-reduced-motion`.
- Partículas 3D reduzidas no mobile e desligadas quando o usuário pede menos movimento.
