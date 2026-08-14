-- Professor review workspace: apply through the Supabase migration runner.
-- Collaboration data is separate from scientific evidence and never upgrades a
-- research claim until the normal repository evidence pipeline registers it.

create type public.review_role as enum ('PUBLIC_READER', 'REVIEWER', 'MODERATOR', 'ADMIN');
create type public.moderation_state as enum ('PENDING', 'APPROVED', 'REJECTED', 'QUARANTINED', 'HIDDEN');

create table public.review_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 120),
  role public.review_role not null default 'REVIEWER',
  account_status text not null default 'PENDING' check (account_status in ('PENDING', 'ACTIVE', 'SUSPENDED')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

-- Tokens are stored only as hashes. A server-side acceptance handler validates
-- plaintext invitation tokens and never returns them to a browser.
create table public.review_invites (
  id uuid primary key default gen_random_uuid(), email_hash text not null,
  role public.review_role not null default 'REVIEWER', token_hash text not null unique,
  expires_at timestamptz not null, accepted_at timestamptz,
  accepted_by uuid references public.review_profiles(id),
  created_by uuid not null references public.review_profiles(id),
  created_at timestamptz not null default now(), check (expires_at > created_at)
);

create table public.review_documents (
  id uuid primary key default gen_random_uuid(), title text not null check (char_length(title) between 1 and 180),
  description text check (char_length(description) <= 2000),
  storage_path text not null unique check (storage_path ~ '^[0-9a-f-]+/[0-9a-f-]+/[A-Za-z0-9._-]+$'),
  original_filename text not null, safe_display_filename text not null,
  mime_type text not null check (mime_type in ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown', 'text/csv', 'image/png', 'image/jpeg')),
  size_bytes bigint not null check (size_bytes between 1 and 10485760), sha256 text not null check (sha256 ~ '^[A-Fa-f0-9]{64}$'),
  scan_status text not null default 'PENDING' check (scan_status in ('PENDING', 'CLEAN', 'REJECTED', 'NOT_CONFIGURED')),
  moderation_status public.moderation_state not null default 'PENDING', visibility text not null default 'PRIVATE' check (visibility in ('PRIVATE', 'PUBLIC')),
  uploaded_by uuid not null references public.review_profiles(id), created_at timestamptz not null default now(),
  reviewed_at timestamptz, reviewed_by uuid references public.review_profiles(id), moderation_note text check (char_length(moderation_note) <= 2000)
);

create table public.discussion_threads (
  id uuid primary key default gen_random_uuid(), page_key text not null default 'professor-review' check (page_key in ('professor-review')),
  title text not null check (char_length(title) between 1 and 180), thread_status text not null default 'OPEN' check (thread_status in ('OPEN', 'LOCKED', 'HIDDEN')),
  visibility text not null default 'PRIVATE' check (visibility in ('PRIVATE', 'PUBLIC')), moderation_status public.moderation_state not null default 'PENDING',
  created_by uuid not null references public.review_profiles(id), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

create table public.discussion_comments (
  id uuid primary key default gen_random_uuid(), thread_id uuid not null references public.discussion_threads(id) on delete cascade,
  parent_id uuid references public.discussion_comments(id) on delete cascade, author_id uuid not null references public.review_profiles(id),
  body text not null check (char_length(body) between 1 and 5000), moderation_status public.moderation_state not null default 'PENDING',
  created_at timestamptz not null default now(), edited_at timestamptz, hidden_at timestamptz, check (parent_id is null or parent_id <> id)
);

-- Append-only audit data: browser roles receive no mutation policy.
create table public.moderation_log (
  id bigint generated always as identity primary key, actor_id uuid not null references public.review_profiles(id),
  entity_type text not null check (entity_type in ('DOCUMENT', 'THREAD', 'COMMENT', 'INVITE')), entity_id uuid not null,
  action text not null, reason text check (char_length(reason) <= 2000), created_at timestamptz not null default now()
);

create index review_documents_visible_idx on public.review_documents (moderation_status, visibility, created_at desc);
create index discussion_comments_thread_idx on public.discussion_comments (thread_id, created_at);

create or replace function public.current_review_role()
returns public.review_role language sql stable security definer set search_path = public
as $$ select role from public.review_profiles where id = auth.uid() and account_status = 'ACTIVE' $$;

create or replace function public.is_review_staff()
returns boolean language sql stable security definer set search_path = public
as $$ select public.current_review_role() in ('MODERATOR', 'ADMIN') $$;

create or replace function public.touch_review_updated_at()
returns trigger language plpgsql as $$ begin new.updated_at = now(); return new; end; $$;

create or replace function public.limit_comment_reply_depth()
returns trigger language plpgsql as $$
begin
  if new.parent_id is not null and exists (select 1 from public.discussion_comments where id = new.parent_id and parent_id is not null) then
    raise exception 'Only one reply level is permitted';
  end if;
  return new;
end;
$$;

create trigger review_profiles_touch before update on public.review_profiles for each row execute function public.touch_review_updated_at();
create trigger discussion_threads_touch before update on public.discussion_threads for each row execute function public.touch_review_updated_at();
create trigger discussion_comments_reply_depth before insert or update of parent_id on public.discussion_comments for each row execute function public.limit_comment_reply_depth();

alter table public.review_profiles enable row level security;
alter table public.review_invites enable row level security;
alter table public.review_documents enable row level security;
alter table public.discussion_threads enable row level security;
alter table public.discussion_comments enable row level security;
alter table public.moderation_log enable row level security;

-- Profiles/invites are never public. Profile-role writes are server-only so a
-- reviewer cannot promote themself through a client update.
create policy "reviewer reads own profile" on public.review_profiles for select using (id = auth.uid() or public.is_review_staff());
create policy "staff manages invites" on public.review_invites for all using (public.is_review_staff()) with check (public.is_review_staff());

create policy "read approved public documents" on public.review_documents for select using (moderation_status = 'APPROVED' and visibility = 'PUBLIC');
create policy "reviewer reads own documents" on public.review_documents for select to authenticated using (uploaded_by = auth.uid() or public.is_review_staff());
create policy "reviewer submits own document metadata" on public.review_documents for insert to authenticated with check (uploaded_by = auth.uid() and public.current_review_role() in ('REVIEWER', 'MODERATOR', 'ADMIN'));
create policy "staff moderates documents" on public.review_documents for update to authenticated using (public.is_review_staff()) with check (public.is_review_staff());

create policy "read approved public threads" on public.discussion_threads for select using (moderation_status = 'APPROVED' and visibility = 'PUBLIC' and thread_status <> 'HIDDEN');
create policy "reviewer reads own threads" on public.discussion_threads for select to authenticated using (created_by = auth.uid() or public.is_review_staff());
create policy "reviewer opens a thread" on public.discussion_threads for insert to authenticated with check (created_by = auth.uid() and public.current_review_role() in ('REVIEWER', 'MODERATOR', 'ADMIN'));
create policy "staff moderates threads" on public.discussion_threads for update to authenticated using (public.is_review_staff()) with check (public.is_review_staff());

create policy "read approved comments on public threads" on public.discussion_comments for select using (moderation_status = 'APPROVED' and exists (select 1 from public.discussion_threads t where t.id = thread_id and t.moderation_status = 'APPROVED' and t.visibility = 'PUBLIC' and t.thread_status <> 'HIDDEN'));
create policy "reviewer reads own comments" on public.discussion_comments for select to authenticated using (author_id = auth.uid() or public.is_review_staff());
create policy "reviewer submits a comment" on public.discussion_comments for insert to authenticated with check (author_id = auth.uid() and public.current_review_role() in ('REVIEWER', 'MODERATOR', 'ADMIN') and exists (select 1 from public.discussion_threads t where t.id = thread_id and t.thread_status = 'OPEN'));
create policy "staff moderates comments" on public.discussion_comments for update to authenticated using (public.is_review_staff()) with check (public.is_review_staff());
create policy "staff reads moderation log" on public.moderation_log for select using (public.is_review_staff());

-- Private, quota-limited bucket. Client files use <user-id>/<document-id>/<safe
-- name>; only staff can read objects directly. User download is brokered by a
-- server route after document authorization, never a public bucket URL.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('professor-review', 'professor-review', false, 10485760, array['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown', 'text/csv', 'image/png', 'image/jpeg'])
on conflict (id) do update set public = false, file_size_limit = 10485760;
create policy "reviewer uploads to own prefix" on storage.objects for insert to authenticated with check (bucket_id = 'professor-review' and (storage.foldername(name))[1] = auth.uid()::text and public.current_review_role() in ('REVIEWER', 'MODERATOR', 'ADMIN'));
create policy "staff reads private review files" on storage.objects for select to authenticated using (bucket_id = 'professor-review' and public.is_review_staff());
