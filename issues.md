# Issues Encountered — WealthSimple Submission Run

## 1. GitHub MCP `push_files` Failed — Empty Repository (409)

**What happened:** After creating the GitHub repo via MCP (`create_repository` with `autoInit: false`), calling `push_files` returned:
```
failed to initialize repository: failed to get initial commit:
GET .../git/commits/...: 409 Git Repository is empty.
```
The `push_files` tool requires an existing branch/commit to push to, which doesn't exist on a freshly created repo with no auto-initialization.

**Fix:** Fell back to local git commands — `git init`, `git add`, `git commit`, then `git push -u origin main`.

---

## 2. `id8-src` Treated as Git Submodule

**What happened:** The Next.js scaffold (`id8-src/`) had its own `.git` directory. When `git init` was run in the parent `WealthSimple/` directory, git detected the nested repo and added `id8-src` as a submodule (mode `160000`) instead of including its files. This meant none of the source files were committed.

**Fix:**
```bash
rm -rf id8-src/.git
git rm --cached id8-src
git add id8-src/
git commit -m "fix: add id8-src source files (remove nested git repo)"
```

---

## 3. Force Push Required on First Push

**What happened:** Even though the repo was created with `autoInit: false`, the remote still rejected the push with "Updates were rejected because the remote contains work that you do not have locally." GitHub appears to have auto-created something on the remote side.

**Fix:** Force pushed since the local code was authoritative and the remote had no real content:
```bash
git push -u origin main --force
```

---

## 4. `vercel link` Auto-Linked to Wrong Existing Project

**What happened:** Running `npx vercel link --yes` inside `id8-src/` auto-detected and linked to an existing Vercel project named `id8-src` from a previous deployment, not to the new `wealthsimple-submission` project.

**Fix:** Deleted the auto-created `.vercel/` directory and re-linked with an explicit project name flag:
```bash
rm -rf .vercel
npx vercel link --yes --project wealthsimple-submission
```

---

## 5. Supabase Free-Tier Project Limit Reached

**What happened:** Attempted to create a new Supabase project for WealthSimple, but the org had already hit the 2-project free-tier cap:
```
The following organization members have reached their maximum limits
for the number of active free projects... (2 project limit)
```

**Fix:** User chose to reuse the existing "ID8 Task App" project. Applied the WealthSimple migration (`accounts`, `transactions`, `budgets` tables with RLS) into that project using `apply_migration`.

---

## 6. Material Symbols Icons Rendering as Raw Text

**What happened:** On the deployed site, Material Symbols icons showed as their raw text names (e.g., `account_balance_wallet`, `arrow_forward`, `lock`) instead of rendering as glyphs.

**Root cause — broken font URL:** The Google Fonts link used an incorrect axis parameter format for Material Symbols:
```
# Wrong — wght@100..700,0..1 is not valid for Material Symbols
https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@100..700,0..1&display=swap
```
Material Symbols is a variable font that requires all four axes specified explicitly: `opsz`, `wght`, `FILL`, `GRAD`.

**Root cause — incomplete CSS class:** The `.material-symbols-outlined` CSS class was missing `font-family`, `display: inline-block`, `line-height: 1`, and other required properties for icon font rendering.

**Fix — `layout.tsx`:**
```html
<link
  href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
  rel="stylesheet"
/>
```

**Fix — `globals.css`:**
```css
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-smoothing: antialiased;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```
