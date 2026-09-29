-- Nexora Phase 4: Supabase schema
-- Run once in the Supabase SQL editor (Dashboard > SQL > New query > paste > Run).
-- All access is server-side via the service-role key; RLS stays enabled with
-- no public policies, so client-side (anon) access reads nothing.

create table if not exists profiles (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  full_name text,
  created_at timestamptz not null default now()
);

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  doc_id text unique not null,
  user_id uuid references profiles(id),
  name text not null,
  kind text,
  detail text,
  size_bytes bigint,
  chars int,
  created_at timestamptz not null default now()
);

create table if not exists document_history (
  id uuid primary key default gen_random_uuid(),
  doc_id text,
  user_id uuid references profiles(id),
  action text not null,          -- summary | chat | extract | analyze | career:<tool> | hr_document:<slug>
  input_preview text,            -- question or tool inputs, trimmed
  output_preview text,           -- first 2000 chars of the AI output
  created_at timestamptz not null default now()
);

create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  doc_id text,
  user_id uuid references profiles(id),
  role text not null,            -- user | assistant
  message text not null,
  created_at timestamptz not null default now()
);

create table if not exists usage (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  event text not null,           -- upload | ai_call | career:<slug> | hr_document | download
  meta jsonb,
  created_at timestamptz not null default now()
);

create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  plan text not null default 'free',
  status text not null default 'active',
  started_at timestamptz not null default now(),
  ends_at timestamptz
);

create table if not exists payments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  razorpay_order_id text,
  razorpay_payment_id text,
  amount_paise int,
  currency text default 'INR',
  status text,                   -- created | paid | failed | verified
  product text,                  -- resume_fix | jd_improve | offer_review | cover_letter
  created_at timestamptz not null default now()
);

create table if not exists purchases (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  product text not null,
  payment_id uuid references payments(id),
  unlocked boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists resume_projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  title text,
  source_doc_id text,
  analysis text,
  result text,
  created_at timestamptz not null default now()
);

create table if not exists jd_projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  title text,
  source_doc_id text,
  analysis text,
  result text,
  created_at timestamptz not null default now()
);

create table if not exists generated_files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  kind text,                     -- resume | jd | cover_letter | hr_document | extract
  filename text,
  content text,
  created_at timestamptz not null default now()
);

alter table profiles enable row level security;
alter table documents enable row level security;
alter table document_history enable row level security;
alter table conversations enable row level security;
alter table usage enable row level security;
alter table subscriptions enable row level security;
alter table payments enable row level security;
alter table purchases enable row level security;
alter table resume_projects enable row level security;
alter table jd_projects enable row level security;
alter table generated_files enable row level security;

create index if not exists documents_doc_id_idx on documents (doc_id);
create index if not exists document_history_doc_id_idx on document_history (doc_id);
create index if not exists usage_event_idx on usage (event);
