When `--dry-run` is present:

1. Validate Context7 connectivity with a read-only docs lookup.
2. Validate Stitch connectivity with a read-only project/list call.
3. Verify GitHub CLI is authenticated: `gh auth status`.
4. Verify Vercel CLI is authenticated: `npx vercel whoami`.
5. Verify Supabase CLI is authenticated: `supabase projects list` (if Supabase is in the tech plan).
6. Stop after reporting connectivity status. Do not create repos, deploy, or provision resources.
