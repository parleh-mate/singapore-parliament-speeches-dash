
# party colors for speeches graph

PARTY_COLOURS = {
    "All": '#FF964F', # pastel orange
    "PAP": "#FF9999",  # pastel red
    "PSP": "#FFFF99",  # pastel yellow
    "WP": "#99CCFF",  # pastel blue
    "NMP": "#BAFFC9",  # pastel green
    "SPP": "#D8BFD8"  # pastel purple
}

ETHNIC_COLOURS = {
    "chinese": "#FFCBDB",  # pastel pink
    "malay": "#6CD0D0",  # pastel turquoise
    "indian": "#B1DDC9",  # pastel green
    "others": "#FBCEB1",  # pastel orange
}

# Define parliaments
parliaments = {
    "12th (2011-2015)": '12',
    "13th (2016-2020)": '13',
    "14th (2020-present)": '14',
    "All": 'All'
}

parliament_sessions = sorted(parliaments.keys(), reverse=True)