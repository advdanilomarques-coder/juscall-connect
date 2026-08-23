-- Memória de curto prazo das conversas do chatbot de WhatsApp.
-- Guarda as últimas mensagens por número, para a IA manter contexto.
create table if not exists public.wa_conversations (
  phone       text primary key,
  history     jsonb not null default '[]'::jsonb,
  updated_at  timestamptz not null default now()
);

-- A tabela é acessada apenas pela Edge Function (service role).
-- Ativamos RLS sem políticas públicas: ninguém acessa via anon/authenticated.
alter table public.wa_conversations enable row level security;

comment on table public.wa_conversations is
  'Histórico curto das conversas do chatbot WhatsApp (TMS Advogados). Uso interno da Edge Function.';
