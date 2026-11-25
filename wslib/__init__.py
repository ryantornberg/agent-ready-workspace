"""The engine: the runner, and the small core every part plugs into. Snapshots, markdown reading, symbol lookup,
the part loader, the event adapters and the edit ledger. A workspace's own files never sit in this folder."""

# The manifest's "version" must equal this. Raise it when the manifest's keys or a part's settings change meaning.
VERSION = "0.4.0"
