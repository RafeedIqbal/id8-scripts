1. Generate a PRD from the initial prompt.
   Pause after output. Ask for confirmation before continuing.
2. Call Context7 and produce a technical plan compatible with Vercel and Supabase.
   Pause after output. Ask for confirmation before continuing.
3. Call Stitch to generate UI screens and collect user review/adjustments.
   Pause after user feedback loop finishes.
4. Implement backend code using the approved tech plan and Context7 references.
   Pause after implementation summary.
5. Implement frontend code using approved Stitch output and Context7 references.
   Pause after implementation summary.
6. Run local test suites and report pass/fail with actionable fixes.
   Pause after presenting test results.
7. Prompt for repository model (monorepo vs split repos), then call GitHub MCP to create repos if needed and push code.
   Mandatory confirmation required immediately before any repo creation/push action.
8. Call Vercel MCP to deploy the frontend.
   Mandatory confirmation required immediately before deployment.
9. Call Supabase MCP to provision/deploy backend resources.
   Mandatory confirmation required immediately before provisioning/deployment.
10. Perform post-deploy verification checks and publish a completion report with links, status, and outstanding actions.
    Pause after final report for explicit closeout confirmation.
