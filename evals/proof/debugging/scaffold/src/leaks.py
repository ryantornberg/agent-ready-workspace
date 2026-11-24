"""The leak check: a transcript is saved only when it names nothing that identifies the person who ran it."""
import json


def leaks(actions, secrets):
    """The secrets that appear anywhere in the transcript, ignoring case. actions: the transcript, a list of
    {"kind", "target", "output"} records. secrets: the user name, the home folder and the like."""
    text = json.dumps(actions).lower()
    return [secret for secret in secrets if secret.lower() in text]
