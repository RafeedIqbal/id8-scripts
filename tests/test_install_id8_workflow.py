import argparse
import tempfile
import unittest

from install_id8_workflow import (
    MARKER_END,
    MARKER_START,
    Installer,
    build_codex_toml_block,
    parse_agents,
    upsert_managed_block,
)


class InstallWorkflowTests(unittest.TestCase):
    def test_parse_agents_deduplicates(self) -> None:
        self.assertEqual(
            parse_agents("claude,codex,claude,antigravity"),
            ["claude", "codex", "antigravity"],
        )

    def test_parse_agents_rejects_invalid(self) -> None:
        with self.assertRaises(ValueError):
            parse_agents("claude,unknown")

    def test_upsert_managed_block_inserts_when_missing(self) -> None:
        original = "model = \"gpt-5\"\n"
        block = f"{MARKER_START}\n[mcp_servers.id8_context7]\nurl = \"x\"\n{MARKER_END}\n"
        updated = upsert_managed_block(original, block)
        self.assertIn(MARKER_START, updated)
        self.assertIn(MARKER_END, updated)

    def test_upsert_managed_block_replaces_existing(self) -> None:
        old_block = f"{MARKER_START}\nold\n{MARKER_END}\n"
        original = f"before\n{old_block}after\n"
        new_block = f"{MARKER_START}\nnew\n{MARKER_END}\n"
        updated = upsert_managed_block(original, new_block)
        self.assertIn("new", updated)
        self.assertNotIn("old", updated)
        self.assertEqual(updated.count(MARKER_START), 1)

    def test_build_codex_toml_block_contains_headers(self) -> None:
        block = build_codex_toml_block(
            {
                "github_mcp_server": {
                    "command": "npx",
                    "args": ["-y", "mcp-remote", "https://example.com"],
                    "enabled": True,
                    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "abc"},
                }
            }
        )
        self.assertIn("[mcp_servers.github_mcp_server]", block)
        self.assertIn("command =", block)
        self.assertIn("[mcp_servers.github_mcp_server.env]", block)

    def test_codex_entries_are_non_docker_and_use_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = argparse.Namespace(
                project_dir=tmp,
                agents="codex",
                non_interactive=True,
                vercel_auth="key",
                supabase_auth="oauth",
                force=False,
                validate_only=True,
            )
            installer = Installer(args)
            entries = installer._build_codex_mcp_entries()

        self.assertNotIn("MCP_DOCKER", entries)
        for config in entries.values():
            self.assertNotEqual(config["command"], "docker")

        stitch_args = entries["StitchMCP"]["args"]
        self.assertIn("--header", stitch_args)
        self.assertIn("X-Goog-Api-Key: ${ID8_STITCH_API_KEY}", stitch_args)

        github_args = entries["github_mcp_server"]["args"]
        self.assertIn("Authorization: Bearer ${ID8_GITHUB_TOKEN}", github_args)

        vercel_args = entries["VercelMCP"]["args"]
        self.assertIn("Authorization: Bearer ${ID8_VERCEL_TOKEN}", vercel_args)

        supabase_args = entries["supabase_mcp_server"]["args"]
        joined_supabase = " ".join(supabase_args)
        self.assertNotIn("Authorization: Bearer ${ID8_SUPABASE_TOKEN}", joined_supabase)


if __name__ == "__main__":
    unittest.main()
