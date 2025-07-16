"""Application constants and mappings."""

from typing import Dict

# Color mapping for travel time categories
TIME_CATEGORY_COLORS: Dict[str, str] = {
    "< 5": "#1a9850",
    "5~10": "#66bd63",
    "10~15": "#a6d96a",
    "15~20": "#fdae61",
    "20~25": "#fee08b",
    "25~30": "#f46d43",
    "30~45": "#d73027",
    "> 45": "#a50026",
}

# Default color for unknown categories
DEFAULT_COLOR = "#808080"
