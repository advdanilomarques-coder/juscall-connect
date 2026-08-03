# 📦 Publicar o PedroIA (VS Code Marketplace + Open VSX + terminal)

Guia completo para publicar a extensão. Faça o **deploy do backend antes**
(veja `../deployment/DEPLOY_BACKEND.md`) e aponte a extensão para a URL dele.

---

## Passo 0 — Apontar a extensão para o seu backend

Edite `extension/package.json` → `contributes.configuration.properties.pedroia.backendUrl.default`
e troque para a URL do seu backend no Render:

```json
"pedroia.backendUrl": {
  "type": "string",
  "default": "https://SEU-SERVICO.onrender.com"
}
```

Troque também `publisher`, `repository`, `homepage` e `sponsor` no `package.json`
pelos seus dados reais.

---

## Passo 1 — Instalar as ferramentas

```bash
cd PedroIA/extension
npm install
npm install -g @vscode/vsce   # empacotador oficial (também dá pra usar via npx)
```

---

## Passo 2 — Testar localmente (antes de publicar)

1. Abra a pasta `extension/` no VS Code.
2. Pressione **F5** → abre uma janela "Extension Development Host".
3. Rode **PedroIA: Perguntar** (`Ctrl+Alt+P`) e teste o chat + autocomplete.

Ou empacote e instale o `.vsix` manualmente:

```bash
npm run compile
npx vsce package           # gera pedroia-0.1.0.vsix
# No VS Code: Extensões → "..." → Install from VSIX...
```

---

## Passo 3 — Criar o publisher (uma vez)

1. Crie uma organização no **Azure DevOps**: https://dev.azure.com
2. Gere um **Personal Access Token (PAT)**:
   - Perfil → **Personal Access Tokens → New Token**
   - **Organization:** All accessible organizations
   - **Scopes:** *Marketplace → Manage*
   - Copie o token.
3. Crie o publisher em https://marketplace.visualstudio.com/manage
   - O `publisher` do `package.json` deve ser exatamente o ID que você criar.
4. Faça login no terminal:

```bash
npx vsce login SEU_PUBLISHER
# cole o PAT quando pedir
```

---

## Passo 4 — Publicar no VS Code Marketplace

```bash
npx vsce publish
```

Pronto! Em alguns minutos a extensão aparece em
`https://marketplace.visualstudio.com/items?itemName=SEU_PUBLISHER.pedroia`.

Para publicar novas versões (sobe automaticamente o número de versão):

```bash
npx vsce publish patch   # 0.1.0 → 0.1.1
npx vsce publish minor   # 0.1.0 → 0.2.0
```

---

## Passo 5 — Publicar no Open VSX (Cursor, VSCodium, Gitpod)

O Marketplace da Microsoft não é usado pelo Cursor/VSCodium — eles usam o **Open VSX**.

```bash
npm install -g ovsx
# crie conta e token em https://open-vsx.org (via GitHub)
npx ovsx publish pedroia-0.1.0.vsix -p SEU_TOKEN_OPENVSX
```

---

## Passo 6 — Usar via terminal (instalar/rodar sem clicar)

Depois de publicada, qualquer pessoa instala pela linha de comando:

```bash
# VS Code
code --install-extension SEU_PUBLISHER.pedroia

# Cursor
cursor --install-extension SEU_PUBLISHER.pedroia

# A partir de um .vsix local
code --install-extension pedroia-0.1.0.vsix
```

E abre o chat pela paleta (`Ctrl+Shift+P` → "PedroIA: Perguntar") ou pelo atalho `Ctrl+Alt+P`.

---

## Passo 7 — Publicar no GitHub Releases (opcional)

Anexe o `.vsix` a um release para quem quiser baixar direto:

```bash
git tag v0.1.0
git push origin v0.1.0
# No GitHub: Releases → Draft new release → anexe pedroia-0.1.0.vsix
```

---

## Checklist final

- [ ] Backend no ar e `/health` respondendo
- [ ] `backendUrl` da extensão apontando para o backend
- [ ] `publisher`, `repository`, `homepage` preenchidos
- [ ] `icon.png` presente (128×128) ✅ (já incluso)
- [ ] Testado com **F5**
- [ ] `vsce publish` executado
- [ ] (opcional) Open VSX + GitHub Release
