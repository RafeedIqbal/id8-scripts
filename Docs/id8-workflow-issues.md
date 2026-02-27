# /id8 Workflow — Errors & Issues Log

Captured from a full HabitFlow run (Next.js 16 + Supabase + Vercel + Stitch).
Use this to improve the skill instructions and tool call patterns.

---

## 1. Stitch: `create_project` rejects `deviceType` parameter

**Step:** 3 (UI Design)
**Symptom:** `mcp__stitch__create_project` returned "Request contains an invalid argument" when called with `deviceType: "DESKTOP"`.
**Root cause:** The tool schema only accepts `title`. `deviceType` is not a valid parameter for project creation — it is set per-screen at generation time.
**Fix:** Remove `deviceType` from `create_project` calls. Pass `deviceType` only to `generate_screen_from_text`.
**Skill update:** Clarify in Step 3 instructions that `create_project` only accepts `title`.

---

## 2. Stitch: `generate_screen_from_text` uses `projectId` not `project`

**Step:** 3 (UI Design)
**Symptom:** First generation attempt returned "Request contains an invalid argument" when using the parameter `project: "projects/..."`.
**Root cause:** The correct parameter name is `projectId` and it expects the bare ID (e.g. `"11246616908548421333"`) without the `projects/` prefix.
**Fix:** Always use `projectId` with the numeric ID only.
**Skill update:** Add a note: `projectId` = numeric ID only, no `projects/` prefix. `get_screen` and `list_screens` use the full `projects/{id}` path.

---

## 3. Stitch: Dashboard screen generation returned no output (silent failure)

**Step:** 3 (UI Design)
**Symptom:** `generate_screen_from_text` returned `Tool ran without output or errors` for the Dashboard screen, on both attempts (first and retry).
**Root cause:** Unknown — likely a timeout or server-side generation failure with no error returned. The screens were actually generated in the background but the MCP call returned nothing.
**Impact:** Had to ask the user to provide screen IDs manually via the Stitch UI.
**Fix / Workaround:** After a silent return, use `get_project` or `list_screens` (with polling) to discover newly generated screens rather than assuming failure. The tool description says "DO NOT RETRY" but that only applies to connection errors — for silent completions, checking the project state is appropriate.
**Skill update:** After any `generate_screen_from_text` call that returns empty, call `list_screens` to verify before reporting failure. Include the note: "Silent return ≠ failure; check the project."

---

## 4. Stitch: `list_screens` requires bare `projectId`, not `parent`

**Step:** 3 (UI Design)
**Symptom:** `mcp__stitch__list_screens` returned "Request contains an invalid argument" when called with `parent: "projects/..."`.
**Root cause:** The correct parameter is `projectId` (bare numeric ID), not `parent`.
**Fix:** Always use `projectId` for `list_screens`. Use `get_screen` with the full `projects/{id}/screens/{screenId}` path.
**Skill update:** Standardize parameter lookup from tool schema before calling any Stitch tool.

---

## 5. Next.js 16: `middleware.ts` is deprecated — must use `proxy.ts`

**Step:** 6 (Local build)
**Symptom:** Build warning: *"The 'middleware' file convention is deprecated. Please use 'proxy' instead."* Then a build error: *"Proxy is missing expected function export name"*.
**Root cause:** Next.js 16 renamed the middleware system to "proxy". The file must be `proxy.ts` and the exported function must be named `proxy` (not `middleware`).
**Fix:** Create `proxy.ts` with `export async function proxy(request: NextRequest) { ... }` and `export const config = { matcher: [...] }`.
**Skill update:** Add to the tech plan: "Next.js 16 uses `proxy.ts` instead of `middleware.ts`. Export function must be named `proxy`."

---

## 6. TypeScript: `startTransition` callback cannot return a value

**Step:** 6 (Local build)
**Symptom:** TypeScript error: *"Type `Promise<{ error: string } | undefined>` is not assignable to type `VoidOrUndefinedOnly`"* in `HabitCard.tsx`.
**Root cause:** `startTransition(fn)` requires the callback to return `void`. Server actions that return `Promise<{ error } | undefined>` cannot be passed directly.
**Fix:** Wrap in a void async arrow: `startTransition(async () => { await serverAction(...) })`.
**Skill update:** Add code pattern to component generation notes: always wrap server action calls in `startTransition` with `async () => { await ... }`.

---

## 7. Tailwind v4: `@import url()` for Google Fonts silently dropped in production

**Step:** 6 + post-deploy (icons showed as text strings)
**Symptom:** All Material Symbols Outlined icons rendered as their ligature text fallback (e.g. `check`, `add`, `local_fire_department`) in the deployed Vercel build. Worked fine locally.
**Root cause:** Tailwind v4 uses a CSS-based config via `@import "tailwindcss"`. External `@import url(...)` statements placed after `@import "tailwindcss"` are silently dropped during the production CSS optimization pass. The Material Symbols font never loaded.
**Fix:** Move all Google Fonts `<link>` tags directly into `<head>` in `layout.tsx`. Remove `@import url(...)` from `globals.css` entirely.
**Skill update:** When generating Next.js projects with Tailwind v4, always load external fonts via `<link>` in `layout.tsx`, never via CSS `@import url()`. Add this as a rule in the tech plan step.

---

## 8. Supabase: Free tier 2-project limit blocks new project creation

**Step:** 8 (Supabase deployment)
**Symptom:** `create_project` returned: *"The following organization members have reached their maximum limits for the number of active free projects (2 project limit)."*
**Root cause:** Supabase free tier allows max 2 active projects per org. User already had one active project.
**Impact:** Could not create a dedicated `habitflow` project; had to reuse an existing one.
**Fix / Workaround:** Added a user prompt to choose between: pause existing project, reuse existing project, or skip deployment.
**Skill update:** In Step 8, always call `list_projects` first. If the user is at the free tier limit, present options before attempting `create_project`. Add check: "If ≥ 2 active projects exist, ask user to pause one or opt to reuse an existing project."

---

## 9. Supabase MCP: `get_cost` and `confirm_cost` parameter naming inconsistencies

**Step:** 8 (Supabase deployment)
**Symptom 1:** `get_cost` failed with *"Unrecognized key: organizationId"* — the correct key is `organization_id` (snake_case).
**Symptom 2:** `confirm_cost` failed with *"Invalid input: expected number, received string"* for the `amount` field — must be a number `0`, not a string `"0"`.
**Fix:** Always use `organization_id` (snake_case) for `get_cost`. Pass `amount` as a number literal.
**Skill update:** Add explicit parameter examples for `get_cost` and `confirm_cost` in Step 8 instructions.

---

## 10. Vercel CLI: Project must be linked before `env add` or `deploy`

**Step:** 9 (Vercel deployment)
**Symptom:** `npx vercel env add` returned *"Your codebase isn't linked to a project on Vercel. Run vercel link to begin."*
**Root cause:** `create-next-app` does not auto-link to Vercel. The CLI requires a `.vercel/project.json` created by `vercel link`.
**Fix:** Run `npx vercel link --scope <team-slug> --yes` before any `vercel env add` or `vercel deploy` commands.
**Skill update:** Add `vercel link --scope <team-slug> --yes` as the first CLI step in Step 9 before env var injection.

---

## 11. Vercel: Env vars already exist from prior deployment cause `env add` to fail

**Step:** 9 (Vercel deployment)
**Symptom:** `vercel env add NEXT_PUBLIC_SUPABASE_URL` returned *"A variable with the name already exists for the target production"*.
**Root cause:** `create-next-app` linked to an existing Vercel project (`frontend`) that already had Supabase env vars set from a previous `/id8` run.
**Fix:** Run `vercel env rm <VAR> production --yes` before `vercel env add` to ensure a clean state.
**Skill update:** In Step 9, wrap env var injection in a remove-then-add pattern, or check `vercel env ls` first and skip adding if already correct.

---

## 12. Vercel MCP `deploy_to_vercel` takes no parameters

**Step:** 9 (Vercel deployment)
**Symptom:** The `mcp__vercel__deploy_to_vercel` tool has an empty parameter schema `{}`. It's unclear how it determines which project/directory to deploy.
**Impact:** Could not use the MCP tool reliably for deployment; fell back to `npx vercel deploy --prod --yes` via CLI.
**Skill update:** Default to the Vercel CLI (`npx vercel deploy --prod --yes`) for deployment in Step 9. Only use the MCP tool if the project is already linked and the MCP tool's behavior is confirmed.

---

## Summary Table

| # | Area | Severity | Type |
|---|------|----------|------|
| 1 | Stitch `create_project` | Low | Wrong parameter |
| 2 | Stitch `generate_screen_from_text` | High | Wrong parameter name |
| 3 | Stitch silent screen generation | High | Unreliable tool output |
| 4 | Stitch `list_screens` | Medium | Wrong parameter name |
| 5 | Next.js 16 proxy rename | High | Framework version change |
| 6 | TypeScript `startTransition` | Medium | Type constraint |
| 7 | Tailwind v4 font loading | High | Production-only silent failure |
| 8 | Supabase free tier limit | Medium | Infrastructure constraint |
| 9 | Supabase MCP param naming | Low | API inconsistency |
| 10 | Vercel CLI project linking | Medium | Missing setup step |
| 11 | Vercel env var conflicts | Low | State from prior runs |
| 12 | Vercel MCP deploy tool | Medium | Unclear behavior |
