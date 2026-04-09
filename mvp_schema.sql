-- 산업안전보건 조항 적용 시스템 MVP 스키마 (PostgreSQL)

create table if not exists law_clause (
  id bigserial primary key,
  law_name text not null,
  article_no text not null,
  paragraph_no text,
  subparagraph_no text,
  title text,
  legal_text text not null,
  plain_guide_text text,
  hazard_tags text[] default '{}',
  effective_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists clause_card (
  id bigserial primary key,
  law_clause_id bigint not null references law_clause(id) on delete cascade,
  applicability_conditions jsonb not null default '[]'::jsonb,
  exclusion_conditions jsonb not null default '[]'::jsonb,
  evidence_required jsonb not null default '[]'::jsonb,
  immediate_actions jsonb not null default '[]'::jsonb,
  admin_actions jsonb not null default '[]'::jsonb,
  criminal_review_points jsonb not null default '[]'::jsonb,
  canonical_examples jsonb not null default '[]'::jsonb,
  review_status text not null default 'draft' check (review_status in ('draft', 'reviewed', 'approved')),
  owner_team text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists case_file (
  id bigserial primary key,
  site_type text,
  industry text,
  process_type text,
  incident_date date,
  inspector_id text,
  risk_level text not null default 'medium' check (risk_level in ('low', 'medium', 'high', 'critical')),
  summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists case_evidence (
  id bigserial primary key,
  case_file_id bigint not null references case_file(id) on delete cascade,
  file_url text not null,
  file_type text not null,
  captured_at timestamptz,
  evidence_tags text[] default '{}',
  location_note text,
  created_at timestamptz not null default now()
);

create table if not exists case_clause_mapping (
  id bigserial primary key,
  case_file_id bigint not null references case_file(id) on delete cascade,
  law_clause_id bigint not null references law_clause(id),
  decision text not null check (decision in ('applied', 'not_applied', 'needs_more')),
  rationale text,
  reviewer_comment text,
  created_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (case_file_id, law_clause_id)
);

create index if not exists idx_law_clause_article_no on law_clause(article_no);
create unique index if not exists uq_law_clause_identity
  on law_clause (law_name, article_no, coalesce(paragraph_no, ''), coalesce(subparagraph_no, ''));
create index if not exists idx_law_clause_hazard_tags on law_clause using gin(hazard_tags);
create index if not exists idx_case_evidence_tags on case_evidence using gin(evidence_tags);
