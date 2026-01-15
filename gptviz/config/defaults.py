DEFAULTS_MAIN_VALUE= {
    "K_VALUE": 5,
    "MIN_K_VALUE": 1,
    "MAX_K_VALUE": 15,
    "ICON_SIZE": 20,
    "ZOOM_FACTOR" : 1.05,
    "MIN_ZOOM" : 0.5,
    "MAX_ZOOM" : 1.5,
    "TEXT_FONT": "Arial",
    "TEXT_SIZE": 10,
    "THEME_MODE": "dark",
    "WORKSPACE_DIRECTORY": "gptviz/workspace",
} 

DEFAULT_CONSOLE_PALETTE = {
            "ERRO_COLOR": "#ff5555",
            "SUCC_COLOR": "#50fa7b",
            "WARN_COLOR": "#ffb86c",
            "INFO_COLOR": "#8be9fd",
            "GENE_COLOR": "#bd93f9"
        } 

DEFAULT_GRAPH_PALETTE= {
            "ACTION_SOURCE": "#F4D35E",
            "ACTIONS_CORRELATED": "#6834b2",
            "TOKEN_SOURCE": "#E54DBA",
            "TOKEN_CORRELATED": "#61afef",
            "LINE":"#939393",
            "EXPLICIT_LINK_FOUND":"#2ecc71",
            "EXPLICIT_LINK_NOT_FOUND":"#b62a1b"
        } 

DARK_PALETTE = {
    "primary": "#28454B", "secondary": "#2d2d2d", "terziary": "#424242",
    "app_color":"#6834b2","bg_main": "#181818", "text_main": "#e0e0e0",
    "border": "#333333", "bg_console": "#121212","text_font":DEFAULTS_MAIN_VALUE["TEXT_FONT"],
    "text_size":DEFAULTS_MAIN_VALUE["TEXT_SIZE"],
    "border_console": "#2A2A2A"
}

LIGHT_PALETTE = {
    "primary": "#3498db", "secondary": "#ecf0f1", "terziary": "#A0A0A0",
    "app_color":"#6834b2","bg_main": "#ffffff", "text_main": "#2c3e50",
    "border": "#dcdcdc", "bg_console": "#f8f9fa","text_font":DEFAULTS_MAIN_VALUE["TEXT_FONT"],
    "text_size":DEFAULTS_MAIN_VALUE["TEXT_SIZE"],
    "border_console": "#dee2e6"
}
