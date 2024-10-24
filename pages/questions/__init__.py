import plotly_express as px
import plotly.graph_objects as go
from utils import PARTY_COLOURS, parliaments, parliament_sessions

questions_df = data['questions']

# ministry addressed graph

orders = []
for i in ['count_questions', 'prop_questions']:
    orders.append(questions_df.groupby('ministry_addressed').sum().sort_values(i).index)

count_order, prop_order = orders

# Create the initial figure with count_questions
fig_count = px.bar(
    questions_df,
    x='count_questions',
    y='ministry_addressed',
    color='member_party',
    barmode='relative',
    color_discrete_map=PARTY_COLOURS
)


# Create a separate figure for prop_questions
fig_prop = px.bar(
    questions_df,
    x='prop_questions',
    y='ministry_addressed',
    color='member_party',
    barmode='relative',
    yaxis={'categoryorder':'total ascending'},
    color_discrete_map=PARTY_COLOURS
)

# Combine the two figures by adding traces from fig_prop to fig_count
for trace in fig_prop.data:
    fig_count.add_trace(trace)

# Total number of traces per view
num_traces = len(fig_count.data) // 2

# Initially, show only count traces and hide proportion traces
for i, trace in enumerate(fig_count.data):
    if i >= num_traces:
        trace.visible = False

# Define the buttons
buttons = [
    dict(
        label="Count",
        method="update",
        args=[
            {"visible": [True]*num_traces + [False]*num_traces},
            {"title": "Questions addressed to Ministries",
             "xaxis": {"title": "Questions"},
             "yaxis": {
                    "title": "Ministry Addressed",
                    "categoryorder": "array",
                    "categoryarray": count_order
                }}
        ]
    ),
    dict(
        label="Proportion",
        method="update",
        args=[
            {"visible": [False]*num_traces + [True]*num_traces},
            {"title": "Questions addressed to Ministries",
             "xaxis": {"title": "Proportion of Questions"},
             "yaxis": {
                    "title": "Ministry Addressed",
                    "categoryorder": "array",
                    "categoryarray": prop_order
                }}
        ]
    )
]

# Update the layout to include the buttons
fig_count.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            buttons=buttons,
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.99,
            xanchor="left",
            y=1.2,
            yanchor="top"
        )
    ],
    title="Questions addressed to Ministries",
    xaxis_title="Questions",
    yaxis_title="Ministry Addressed",
    legend_title_text='Party',
    template='plotly_white'
)

fig_count.update_yaxes(
    categoryorder='array',
    categoryarray=count_order
)

fig_count.show()

questions_df = data['speech_agg'].query("parliament=='14'")

# Create the strip plot
fig = px.strip(
    questions_df,
    x='member_party',
    y='questions_per_sitting',
    color = 'member_party',
    stripmode="overlay",
    color_discrete_map=PARTY_COLOURS
)

fig.update_traces(
    marker=dict(size=5),
    opacity=0.6 
)

fig.update_layout(
    template='plotly_white'
)

# Display the figure
fig.show()

fig = px.box(questions_df,
           x = 'member_party',
           y = 'questions_per_sitting',
           points = 'all',
           notched=True
           )

fig.show()