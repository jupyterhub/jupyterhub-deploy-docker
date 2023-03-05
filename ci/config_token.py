c.JupyterHub.load_roles = [  # noqa: F821
    {
        "name": "test-admin",
        "scopes": ["admin:users", "admin:servers", "access:servers"],
        "services": ["test"],
    }
]

c.JupyterHub.services = [  # noqa: F821
    {
        "name": "test",
        "api_token": "test-token-123",
    }
]
