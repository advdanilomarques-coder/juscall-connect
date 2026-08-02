# 📦 Publicar a extensão PedroIA

Guia para publicar no **VS Code Marketplace** (o oficial) e no **Open VSX**
(usado por Cursor, VSCodium, Windsurf, Gitpod). Publicar nos dois = alcance máximo.

> Antes de publicar, o **backend precisa estar no ar** e a extensão deve apontar para ele.
> Veja `deployment/DEPLOY_BACKEND.md`.

---

## 0. Preparação (uma vez)

```bash
cd PedroIA/extension
npm install
npm install -g @vscode/vsce ovsx
```

Ajuste o `package.json`:
- **`publisher`** — troque `"pedroia"` pelo **ID do seu publisher** (criado no passo 1).
- **`pedroia.backendUrl` → `default`** — coloque a URL do seu backend hospedado, para já
  vir configurado para quem instalar.

Recomendado antes de publicar:
- Adicione um **GIF de demonstração** em `media/demo.gif` e referencie no `README.md`.
- Revise o `CHANGELOG.md`.

---

## 1. VS Code Marketplace

### 1.1 Criar o publisher
1. Crie/entre numa conta **Azure DevOps** (grátis): https://dev.azure.com
2. Gere um **Personal Access Token (PAT)**:
   - Azure DevOps → canto superior direito → **User settings → Personal access tokens**
   - **New Token** → Organization: **All accessible organizations**
   - Scopes: **Custom defined → Marketplace → Manage**
   - Copie o token (você só o vê uma vez).
3. Crie o **publisher**: https://marketplace.visualstudio.com/manage
   - **Create publisher** → escolha um **ID** (ex.: `danilomarques`) e um nome de exibição.

### 1.2 Fazer login e publicar
```bash
vsce login SEU_PUBLISHER_ID     # cole o PAT quando pedir
vsce package                    # gera o pedroia-0.1.0.vsix (confira se está tudo certo)
vsce publish                    # publica no Marketplace
```

Para versões futuras:
```bash
vsce publish patch   # 0.1.0 -> 0.1.1   (ou: minor / major)
```

Em minutos a extensão aparece em `https://marketplace.visualstudio.com/items?itemName=SEU_PUBLISHER.pedroia`.

---

## 2. Open VSX (Cursor / VSCodium / Windsurf)

1. Entre em https://open-vsx.org com sua conta do GitHub e gere um **Access Token**
   (Settings → Access Tokens). Aceite o *Publisher Agreement*.
2. Publique:
```bash
ovsx create-namespace SEU_PUBLISHER_ID -p SEU_TOKEN_OPENVSX   # só na 1ª vez
ovsx publish pedroia-0.1.0.vsix -p SEU_TOKEN_OPENVSX
```

---

## 3. Distribuir pelo GitHub (Releases)

Mesmo sem Marketplace, dá para distribuir o `.vsix`:

1. No GitHub, **Releases → Draft a new release** → tag `v0.1.0`.
2. Anexe o arquivo `pedroia-0.1.0.vsix`.
3. Quem quiser instala com:
   ```bash
   code --install-extension pedroia-0.1.0.vsix
   ```

---

## 4. Checklist final antes de publicar

- [ ] `publisher` correto no `package.json`
- [ ] `pedroia.backendUrl` padrão apontando para o backend hospedado
- [ ] Ícone `media/icon.png` (128×128) presente ✅
- [ ] `README.md` com descrição e, idealmente, um GIF
- [ ] `CHANGELOG.md` atualizado
- [ ] `LICENSE` presente ✅
- [ ] `vsce package` roda sem erros e o `.vsix` abre corretamente
- [ ] Backend no ar e testado (`/api/v1/health` responde)

---

## Automação (opcional): publicar no push de tag

Crie `.github/workflows/publish-extension.yml` para publicar automaticamente ao criar uma tag
`v*`, guardando os tokens em **GitHub → Settings → Secrets**
(`VSCE_PAT`, `OVSX_TOKEN`). Peça ao PedroIA para gerar esse workflow quando quiser.
