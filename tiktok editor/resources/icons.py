class Icons:
    PLAY = "play.svg"
    PAUSE = "pause.svg"
    STOP = "stop.svg"
    SETTINGS = "settings.svg"
    EXPORT = "export.svg"
    IMPORT = "import.svg"
    CHECK = "check.svg"
    ARROW_DOWN = "arrow_down.svg"
    
    @classmethod
    def get_path(cls, icon_name: str) -> str:
        return f"resources/icons/{icon_name}"
