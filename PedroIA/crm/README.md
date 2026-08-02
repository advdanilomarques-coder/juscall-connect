# PedroIA — CRM / Monitoramento

Painel leve para acompanhar o uso do PedroIA: total de requisições, erros,
conversas e distribuição por provedor de LLM.

Os dados vêm do backend em `GET /api/v1/crm/summary` e `GET /api/v1/crm/logs`.

## Uso

Abra `index.html` no navegador (ou sirva a pasta) com o backend rodando:

```bash
# a partir da raiz do projeto
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload
# depois, em outro terminal:
python -m http.server 5500 --directory crm
# abra http://localhost:5500
```

Ajuste a URL do backend no campo superior se necessário.
