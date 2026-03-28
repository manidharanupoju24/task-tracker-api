-- ── 1. Create the todos table ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.todos (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    completed   BOOLEAN NOT NULL DEFAULT FALSE,
    priority    TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    category    TEXT NOT NULL DEFAULT 'personal' CHECK (category IN ('personal', 'work', 'shopping', 'other')),
    due_date         DATE,
    notes            TEXT,
    created_by_email TEXT,
    created_by_name  TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Trigger: auto-update updated_at on every row update ───────────────────────

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER todos_set_updated_at
    BEFORE UPDATE ON public.todos
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

-- ── 2. Enable Row Level Security ──────────────────────────────────────────────

ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;

-- ── 3. RLS Policies ───────────────────────────────────────────────────────────
-- Each policy ensures users can only access their own todos.

-- SELECT: users can only read their own todos
CREATE POLICY "Users can view their own todos"
    ON public.todos
    FOR SELECT
    USING (auth.uid() = user_id);

-- INSERT: users can only create todos for themselves
CREATE POLICY "Users can create their own todos"
    ON public.todos
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- UPDATE: users can only update their own todos
CREATE POLICY "Users can update their own todos"
    ON public.todos
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- DELETE: users can only delete their own todos
CREATE POLICY "Users can delete their own todos"
    ON public.todos
    FOR DELETE
    USING (auth.uid() = user_id);

-- ── 4. Index for faster queries per user ──────────────────────────────────────

CREATE INDEX IF NOT EXISTS todos_user_id_idx ON public.todos(user_id);
CREATE INDEX IF NOT EXISTS todos_created_at_idx ON public.todos(created_at DESC);
