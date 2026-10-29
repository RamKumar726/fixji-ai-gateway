# Fixji AI Gateway demo

## Run the floating chat demo

The demo is a static HTML page that talks to the gateway API. Start both backend
services from the repository root in separate PowerShell terminals:

```powershell
uv run fixji-mcp-server
```

```powershell
uv run uvicorn fixji_ai_gateway.main:app --reload --port 8000
```

Configure the gateway's Azure OpenAI environment variables and, if needed,
`FIXJI_BACKEND_URL` before starting it. Set `CORS_ORIGINS` to the origin that
will serve the demo, for example `http://localhost:5500`; for a hosted demo,
include its exact HTTPS origin as well.

In another terminal, serve the demo directory:

```powershell
python -m http.server 5500 --directory demo
```

Open [http://localhost:5500](http://localhost:5500), select the floating button
in the bottom-right corner, and sign in with a Fixji demo account. The page
keeps the login token in memory, sends messages to `/chat`, reuses the returned
session ID, and displays booking details with approve/reject controls when the
gateway requests approval.

By default, the page connects to `http://localhost:8000`. To use another
gateway URL, add it as the `api` query parameter, for example:
`http://localhost:5500/?api=https://your-gateway.example.com`.
