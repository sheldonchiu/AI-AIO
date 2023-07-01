import reflex as rx

class PaperspaceaiaioConfig(rx.Config):
    pass

config = PaperspaceaiaioConfig(
    app_name="app",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)