def get_outlined_frame_stylesheet(style_name: str) -> str:
    return f'#{style_name} ' + r"""
    {
        background-color: rgb(60, 60, 60);
        border-radius: 2px;
        border-style: solid;
        border-width: 1px;
        border-color: rgb(100, 100, 100);
        padding: 2px;
    }"""


def get_highlight_outlined_frame_stylesheet(style_name: str) -> str:
    return f'#{style_name} ' + r"""
    {
        background-color: rgb(75, 75, 75);
        border-radius: 3px;
        border-style: solid;
        border-width: 1px;
        border-color: rgb(120, 120, 120);
    }"""


def get_tab_highlight_outlined_frame_stylesheet(style_name: str) -> str:
    return f'#{style_name} ' + r"""
    {
        background-color: rgb(95, 95, 95);
        border-radius: 3px;
        border-style: solid;
        border-width: 1px;
        border-color: rgb(140, 140, 140);
    }"""