# src

In a real workspace each folder here is a code repository, included as a git submodule pinned at an exact commit. See [decision 0001](../docs/decisions/0001-pin-code-repositories.md).

This sample checks in a few invented files directly, so the checks and hooks have code to run against:

- `orders-api/`: the live order service (C#).
- `orders-web/`: its front end (TypeScript).
- `orders-service-v1/`: the service `orders-api` replaced. It is shelved, and the `shelved` hook refuses edits to it.
