"""Opt-in: two browser servers at once (criteria 6 and 7). CI does not run it; it needs Node and Chrome.

    WS_BROWSER_TEST=1 python3 -m unittest tests.test_browser -b

It starts the browser server exactly as .mcp.json configures it, speaks the MCP protocol to it over
standard input and output, and asks it to open about:blank. Two isolated copies at once must both
succeed. Two copies that share one profile folder must collide, and the second must report the lock:
that is the failure the isolation flag prevents, and the negative control for the first test.
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import threading
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENABLED = os.environ.get("WS_BROWSER_TEST") == "1"


def configured_command():
    server = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["playwright"]
    command = shutil.which(server["command"]) or server["command"]
    return [command, *server["args"]]


class Server:
    """One browser server, spoken to over MCP's newline-delimited JSON-RPC."""

    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, encoding="utf-8")
        self.next_id = 0
        self.stderr = []
        threading.Thread(target=lambda: self.stderr.extend(self.process.stderr), daemon=True).start()

    def send(self, method, params=None, notify=False):
        message = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if not notify:
            self.next_id += 1
            message["id"] = self.next_id
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()
        if notify:
            return None
        for line in self.process.stdout:
            reply = json.loads(line)
            if reply.get("id") == message["id"]:
                return reply
        raise RuntimeError("the server closed its output: " + "".join(self.stderr)[-500:])

    def start(self):
        reply = self.send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                         "clientInfo": {"name": "ws-browser-test", "version": "1"}})
        self.send("notifications/initialized", notify=True)
        return reply

    def navigate(self, url="about:blank"):
        return self.send("tools/call", {"name": "browser_navigate", "arguments": {"url": url}})

    def close(self):
        try:
            self.send("tools/call", {"name": "browser_close", "arguments": {}})
        except (OSError, RuntimeError, ValueError):
            pass
        self.process.kill()
        self.process.wait(timeout=30)


def text_of(reply):
    result = reply.get("result") or {}
    return "\n".join(part.get("text", "") for part in result.get("content", []) if isinstance(part, dict)) \
        + json.dumps(reply.get("error") or "")


@unittest.skipUnless(ENABLED, "opt-in: set WS_BROWSER_TEST=1, with Node and Chrome installed")
class TwoBrowsersTests(unittest.TestCase):
    def servers(self, command):
        first, second = Server(command), Server(command)
        self.addCleanup(second.close)
        self.addCleanup(first.close)
        first.start()
        second.start()
        return first, second

    def test_two_isolated_servers_both_open_a_page(self):
        command = configured_command()
        self.assertIn("--isolated", command)
        first, second = self.servers(command)
        one = first.navigate()           # the first holds its browser open while the second opens one
        two = second.navigate()
        for reply in (one, two):
            self.assertFalse((reply.get("result") or {}).get("isError"), text_of(reply))
            self.assertIn("about:blank", text_of(reply))
        print(f"\n  isolated: both servers opened about:blank with {' '.join(command[1:])}")

    def test_two_servers_sharing_one_profile_folder_collide(self):
        profile = tempfile.mkdtemp(prefix="ws-browser-profile-")
        self.addCleanup(shutil.rmtree, profile, True)
        command = [part for part in configured_command() if part != "--isolated"] + ["--user-data-dir", profile]
        first, second = self.servers(command)
        one = first.navigate()
        self.assertFalse((one.get("result") or {}).get("isError"), text_of(one))
        two = second.navigate()
        self.assertTrue((two.get("result") or {}).get("isError") or two.get("error"), text_of(two))
        self.assertRegex(text_of(two), r"(?i)already in use|in use by another|profile|user data dir|lock")
        print(f"\n  shared profile: the second server reported: {text_of(two).strip()[:200]}")


if __name__ == "__main__":
    unittest.main()
