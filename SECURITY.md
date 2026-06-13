# Security

## Reporting a vulnerability

Please **do not** file a public issue for security problems.

Email **kareem@kareemsafwat.com** with a description of the
vulnerability and a reproducer. Expect an acknowledgement within
72 hours and a fix or mitigation plan within 14 days, depending on
severity.

## Data storage

Tawreed is a **local desktop application**. It does not phone home
and does not collect telemetry. The only network calls it makes are
the ones you configure in the Settings page — to the LLM provider
you selected.

API keys are stored in plaintext at `~/.tawreed/config.json`
(or `%USERPROFILE%\.tawreed\config.json` on Windows). On a shared
machine, restrict access to that file:

```bash
# Linux / macOS
chmod 600 ~/.tawreed/config.json
```

```powershell
# Windows (PowerShell, current user only)
icacls "$env:USERPROFILE\.tawreed\config.json" /inheritance:r /grant:r "$env:USERNAME:(R,W)"
```

## Supply chain

Dependencies are pinned in `pyproject.toml` with soft upper bounds.
Run `pip-audit` periodically (the `chore/dev-tooling` PR adds it to
CI). A failed `pip-audit` is a release blocker.

## Out of scope

- Vulnerabilities in third-party LLM providers (OpenAI, Anthropic,
  Google) — report those to the provider.
- Windows SmartScreen warnings on unsigned EXEs — these are
  expected, not vulnerabilities. See [docs/INSTALL.md](docs/INSTALL.md).
