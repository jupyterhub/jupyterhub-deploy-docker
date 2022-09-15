c.JupyterHub.load_roles = [
    {
        "name": "test-admin",
        "scopes": ["admin:users", "admin:servers", "access:servers"],
        "services": ["test"],
    }
]

c.JupyterHub.services = [
    {
        "name": "test",
        "api_token": "test-token-123",
    }
]
