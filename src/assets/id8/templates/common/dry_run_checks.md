When `--dry-run` is present:

1. Validate Context7 connectivity with a read-only docs lookup.
2. Validate Stitch connectivity with a read-only project/list call.
3. Validate GitHub connectivity with a read-only identity/list call.
4. Validate Vercel connectivity with read-only team/project inspection.
5. Stop after reporting connectivity status. Do not create repos, deploy, or provision resources.
