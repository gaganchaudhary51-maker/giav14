-- Optional Supabase mirror for approved Agent Studio prompts.
-- Apply manually to the intended Supabase project. Do not put the service-role key in the frontend.
create table if not exists public.studio_pod_prompts (
  tenant_id text not null,
  pod_id text not null,
  prompt text not null,
  model text not null,
  channels jsonb not null default '[]'::jsonb,
  enabled boolean not null default true,
  updated_at timestamptz not null default now(),
  primary key (tenant_id, pod_id)
);
alter table public.studio_pod_prompts enable row level security;
-- Backend uses the service-role key server-side for writes; no public/client policies are created.
