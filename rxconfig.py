import reflex as rx

class PaperspaceaiaioConfig(rx.Config):
    pass

config = PaperspaceaiaioConfig(
    app_name="app",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    tailwind={
        "darkMode": 'class',
        "theme": {
            "colors":{
            "gray1": "#F5F7F5",
            "gray2": "#7885A7",
            "blue1": "#243863",
            "pink1": "#AC435B",
            "dark1": "#1D131E",
            },
            "extend": {},
        },
        # "plugins": [
        #     "@flowbite/plugin"
        # ],
    }
)