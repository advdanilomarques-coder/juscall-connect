<div align="center">

# PedroIA

**Seu engenheiro de software com inteligência artificial — dentro do VS Code.**

Chat inteligente · Explicação de código · Autocomplete estilo Copilot

</div>

---

## O que tem aqui

```
PedroIA/
├── extension/        →  Extensão do VS Code (chat + autocomplete)
├── backend/          →  Backend blindado (proxy seguro para o Claude, com rate limit)
├── web/              →  Site oficial (Next.js + GSAP + Three.js)
├── deployment/       →  Guias de deploy
└── render.yaml       →  Blueprint de deploy do backend no Render
```

## A ordem certa para colocar no ar

O backend precisa existir antes da extensão publicada — senão ela não tem a quem se conectar.

1. **Hospedar o backend** → siga [`deployment/DEPLOY_BACKEND.md`](deployment/DEPLOY_BACKEND.md).
   Você vai precisar de uma conta no Render, uma chave da Anthropic e um `API_KEYS`.
   No fim, terá uma URL tipo `https://pedroia-backend.onrender.com`.
2. **Apontar a extensão para essa URL** → edite `extension/package.json` (default de `pedroia.backendUrl`).
3. **Publicar a extensão** → siga [`extension/PUBLICAR.md`](extension/PUBLICAR.md)
   (VS Code Marketplace + Open VSX + terminal).
4. **Publicar o site** → siga [`web/README.md`](web/README.md) (deploy na Vercel).

## Como funciona

```
VS Code (extensão)  ──x-pedroia-key──▶  Backend (Render)  ──ANTHROPIC_API_KEY──▶  Claude (Anthropic)
```

- A chave da **Anthropic** fica **só** no backend (nunca na extensão nem no site).
- O backend tem **rate limiting** e **trava de segurança** (`API_KEYS`) para proteger sua fatura.

## Segurança da chave

- `ANTHROPIC_API_KEY`: sua chave da Anthropic — vive apenas nas variáveis de ambiente do backend.
- `API_KEYS`: chaves de acesso que a extensão envia. Em produção, o backend **se recusa a subir** sem elas.
- Nenhum segredo é versionado — `.env` está no `.gitignore`.

## Licença

MIT — veja [`extension/LICENSE`](extension/LICENSE).
