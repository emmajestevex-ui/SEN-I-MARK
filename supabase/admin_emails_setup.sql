create table if not exists public.license_admins (
    user_id uuid primary key references auth.users(id) on delete cascade,
    role text not null default 'founder',
    created_at timestamptz not null default now(),
    check (role in ('founder', 'admin'))
);

alter table public.license_admins enable row level security;

create or replace function public.is_license_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select exists (
        select 1
        from public.license_admins
        where user_id = auth.uid()
          and role in ('founder', 'admin')
    );
$$;

-- Legacy founder list intentionally removed for SEN$I MARK.


grant execute on function public.is_license_admin() to authenticated;
