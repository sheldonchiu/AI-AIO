import pynecone as pc

config = pc.Config(
    app_name="app",
    db_url="sqlite:///pynecone.db",
    # bun_path="/app/.bun/bin/bun",
    env=pc.Env.DEV,
)
