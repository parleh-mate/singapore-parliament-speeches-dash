from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from utils import PARTY_COLOURS, parliaments, parliament_sessions, member_metrics_options, SIZE_MIN, SIZE_MAX

# speeches layout with dropdowns, graph, and table
def member_metrics_layout():
    return html.Div(
        [
            html.H1("Parliamentary Member metrics"),            
            
            # Dropdowns Section
            dbc.Row([
                # Updated Column with Info Tooltip
                dbc.Col([
                    # Container for the Label and Info Icon
                    html.Div(
                        [
                            html.Label("Select a Parliament Session:"),
                            html.Span(
                                # Info Icon (Bootstrap Icons)
                                html.I(
                                    className="bi bi-info-circle",  # Bootstrap Icon classes
                                    id="member-metrics-parliament-session-info-icon",  # Unique ID for the tooltip
                                    style={
                                        "margin-left": "5px",          # Space between label and icon
                                        "cursor": "pointer",           # Pointer cursor on hover
                                        "color": "#17a2b8",            # Bootstrap's info color
                                        "fontSize": "1rem"             # Icon size
                                    }
                                    # Removed aria_label as it may not be supported directly
                                )
                            )
                        ],
                        style={"display": "flex", "alignItems": "center"}  # Align label and icon vertically
                    ),
                    
                    # Dropdown Component
                    dcc.Dropdown(
                        id='member-metrics-parliament-dropdown',
                        options=[{'label': session, 'value': session} for session in parliament_sessions],
                        value='All',  # Set default to 'All'
                        placeholder='Select a parliament session',
                        searchable=False,
                        clearable=False
                    ),
                    
                    # Tooltip Component
                    dbc.Tooltip(
                        "'All' takes the average across all parliamentary sittings from the 12th parliament to current",
                        target="member-metrics-parliament-session-info-icon",  # Link tooltip to the icon's ID
                        placement="right",                      # Position the tooltip to the right of the icon
                        style={
                            "maxWidth": "300px",
                            "textAlign": "left"  # Ensure text is left-aligned within the tooltip
                        }
                    )
                ], md=4),
                
                # Second Dropdown Column
                dbc.Col([
                    html.Label("Select a Constituency:"),
                    dcc.Dropdown(
                        id='member-metrics-constituency-dropdown',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a constituency',
                        searchable=True,
                        clearable=False
                    )
                ], md=4, id='member-metrics-constituency-dropdown-container', style={'display': 'none'}),
                
                # Third Dropdown Column
                dbc.Col([
                    html.Label("Select a Member Name:"),
                    dcc.Dropdown(
                        id='member-metrics-member-dropdown',
                        options=[],  # Will be populated via callback
                        value='All',
                        placeholder='Select a member name',
                        searchable=True,
                        clearable=False
                    )
                ], md=4),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Select a y-axis variable:"),
                    dcc.Dropdown(
                        id='member-metrics-yaxis-dropdown',
                        options=[{'label': key, 'value': value} for key, value in member_metrics_options.items()],
                        value='questions_per_sitting',
                        searchable=False,
                        clearable=False
                    )
                ], md=4),
                dbc.Col([
                    html.Label("Select an x-axis variable:"),
                    dcc.Dropdown(
                        id='member-metrics-xaxis-dropdown',
                        options=[{'label': key, 'value': value} for key, value in member_metrics_options.items()],
                        value='speeches_per_sitting',
                        searchable=False,
                        clearable=False
                    )
                ], md=4),
                dbc.Col([
                    html.Label("Select a size variable:"),
                    dcc.Dropdown(
                        id='member-metrics-size-dropdown',
                        options=[], # populated via callback
                        value='words_per_speech',
                        searchable=False,
                        clearable=False
                    )
                ], md=4),
            ], className = "mb-4"),
            
            # Accordion Section
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(
                                [
                                    "Speeches refers to any time a member speaks to address the chamber as recorded in the parliamentary Hansard. This includes substantial and procedural points but does not include written answers, parliamentary questions, or the President's address. Members who made no speeches do not appear on the graph.",
                                    html.Br(),
                                    html.Br(),
                                    "To assess how readable a speech is, we use the Flesch-Kincaid score, a well-known index for measuring how difficult a text is to understand in English. The index scales from 0 to 100, with 0 indicating extremely difficult and 100 very easy. Generally, a score of between 30-50 is a college level text, while 10-30 is college-graduate level. The full formula and interpretation guide can be found in the methodology section. Members who did not speak do not have a readability score and will not appear on the graph. Vernacular speeches are also not given a readability score since the index only works for English. Please refer to the methodology for more info."
                                ]
                            )
                        ],
                        title=html.Span(
                            "How are speech and readability score defined?",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "1.1rem"  # Optional: Increase font size
                            }
                        )
                    )
                ],
                start_collapsed=True,
                flush=True,
                className="border border-primary"
            ),
            
            # Graph Section with Fixed Height
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='member-metrics-graph',
                        config={"responsive": True},
                        style={'minHeight': '500px'}
                    )
                ], width=12)
            ]),
        ],
        className='content'
    )


def member_metrics_callbacks(app, data):
    # Callback to control visibility of the Constituency dropdown
    @app.callback(
        Output('member-metrics-constituency-dropdown-container', 'style'),
        Input('member-metrics-parliament-dropdown', 'value')
    )
    def toggle_constituency_dropdown(selected_parliament):
        if selected_parliament != 'All':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    # Callback to update Constituency options based on selected session
    @app.callback(
        [Output('member-metrics-constituency-dropdown', 'options'),
        Output('member-metrics-constituency-dropdown', 'value')],
        Input('member-metrics-parliament-dropdown', 'value')
    )
    def update_constituency_options(selected_parliament):
        if selected_parliament == 'All':
            # If 'All' is selected, reset options to include only 'All'
            return [{'label': 'All', 'value': 'All'}], 'All'
        member_metrics_df = data['member_metrics']
        # Filter the dataframe based on the selected parliament session
        member_metrics_df = member_metrics_df[member_metrics_df['parliament'] == parliaments[selected_parliament]]
        # Get unique constituencies
        constituencies = sorted(member_metrics_df['member_constituency'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': const, 'value': const} for const in constituencies]
        return options, 'All'

    # Callback to update Member Name options based on selected session and constituency
    @app.callback(
        [Output('member-metrics-member-dropdown', 'options'),
        Output('member-metrics-member-dropdown', 'value')],
        [Input('member-metrics-parliament-dropdown', 'value'),
        Input('member-metrics-constituency-dropdown', 'value')]
    )
    def update_member_options(selected_parliament, selected_constituency):
        member_metrics_df = data['member_metrics']
        # Start with filtering by parliament session
        member_metrics_df = member_metrics_df[member_metrics_df['parliament'] == parliaments[selected_parliament]]
        # Further filter by constituency if not 'All'
        if selected_constituency!= 'All':
            member_metrics_df = member_metrics_df[member_metrics_df['member_constituency'] == selected_constituency]
        # Get unique member names
        members = sorted(member_metrics_df['member_name'].unique())
        # Add 'All' option
        options = [{'label': 'All', 'value': 'All'}] + [{'label': member, 'value': member} for member in members]
        return options, 'All'
    
    @app.callback(
            [
                Output('member-metrics-size-dropdown', 'options'),
                Output('member-metrics-size-dropdown', 'value')
            ],
            [
                Input('member-metrics-xaxis-dropdown', 'value'),
                Input('member-metrics-yaxis-dropdown', 'value')
            ]
    )
    def update_size_dropdown(x_axis, y_axis):
    # Start with the 'none' option
        options = [{'label': 'none', 'value': "none"}]
        
        # Iterate through member_metrics_options and exclude selected x and y values
        for key, value in member_metrics_options.items():
            if value not in [x_axis, y_axis]:
                options.append({'label': key, 'value': value})
        
        return options, options[1]['value']

    # Callback to update the member_metrics graph and table on Page 1
    @app.callback(
        Output('member-metrics-graph', 'figure'),
        [
            Input('member-metrics-parliament-dropdown', 'value'),
            Input('member-metrics-constituency-dropdown', 'value'),
            Input('member-metrics-member-dropdown', 'value'),
            Input('member-metrics-xaxis-dropdown', 'value'),
            Input('member-metrics-yaxis-dropdown', 'value'),
            Input('member-metrics-size-dropdown', 'value')
            ]
    )
    def update_graph_and_table(selected_parliament, selected_constituency, selected_member, xaxis_var, yaxis_var, size_var):

        # set names of variables
        xaxis_varname = xaxis_var.replace('_', ' ').title()
        yaxis_varname = yaxis_var.replace('_', ' ').title()

        if size_var=="none":
            size_var = None
        else:
            size_varname = size_var.replace('_', ' ').title()

        # filter out vars for which None was chosen
        selected_vars = [i for i in [xaxis_var, yaxis_var, size_var] if i]

        # get data
        member_metrics_df = data['member_metrics'][list(set(['member_name', 'member_party', 'member_constituency', 'parliament'] + selected_vars))]

        # clean to get rid of NAs
        member_metrics_df = member_metrics_df.dropna(axis = 0, how = 'any')

        # get sizes of size variable
        if size_var:
            # Calculate the global minimum and maximum of size parameter
            global_min = member_metrics_df[size_var].min()
            global_max = member_metrics_df[size_var].max()

            # Define a scaling function
            def scale_marker_size(x, min_val, max_val, size_min, size_max):
                if max_val == min_val:
                    return (size_min + size_max) / 2
                else:
                    return size_min + (x - min_val) / (max_val - min_val) * (size_max - size_min)

            member_metrics_df['marker_size'] = member_metrics_df[size_var].apply(
                lambda x: scale_marker_size(x, global_min, global_max, SIZE_MIN, SIZE_MAX)
            )

        # Filter by parliament        
        member_metrics_df_highlighted = member_metrics_df[member_metrics_df['parliament'] == parliaments[selected_parliament]]

        full_df = member_metrics_df_highlighted.copy()
      
        # Further filter based on selected_constituency
        if selected_constituency != 'All' and selected_constituency:
            member_metrics_df_highlighted = member_metrics_df_highlighted[member_metrics_df_highlighted['member_constituency'] == selected_constituency]
        
        # Further filter based on selected_member
        if selected_member != 'All' and selected_member:
            member_metrics_df_highlighted = member_metrics_df_highlighted[member_metrics_df_highlighted['member_name'] == selected_member]

        member_metrics_df_non_highlighted = full_df.drop(member_metrics_df_highlighted.index)        
        
        # Create the scatter plot
        fig = go.Figure()

        # add traces for highlighted points
        for party in member_metrics_df_highlighted.member_party.unique():

            plot_df = member_metrics_df_highlighted.query(f"member_party=='{party}'")

            fig.add_trace(go.Scatter(
                x=plot_df[xaxis_var],
                y=plot_df[yaxis_var],
                mode='markers',
                marker={
                    'color': plot_df['member_party'].map(PARTY_COLOURS),
                    'opacity': 0.6,
                    **({'size': plot_df['marker_size']} if size_var else {})},
                hovertext=("Member: " + plot_df['member_name'] + "<br>" +
                            "Party: " + plot_df['member_party'] + "<br>" +
                            f"{xaxis_varname}: " + plot_df[xaxis_var].astype(str) + "<br>" +
                            f"{yaxis_varname}: " + plot_df[yaxis_var].astype(str) + "<br>" +
                            (f"{size_varname}: " + plot_df[size_var].astype(str) if size_var else '')
                ),
                hoverinfo='text',
                name=party,
                showlegend=True  # Only the highlighted trace shows in legend
            ))

        # now add traces for non highlighted points    
        fig.add_trace(go.Scatter(
            x=member_metrics_df_non_highlighted[xaxis_var],
            y=member_metrics_df_non_highlighted[yaxis_var],
            mode='markers',
            marker={
                'color': 'grey',
                'opacity': 0.2,
                **({'size': member_metrics_df_non_highlighted['marker_size']} if size_var else {})
            },
            hoverinfo='skip',  # Disable hover for non-highlighted points
            showlegend=False  # Non-highlighted trace doesn't show in legend
        ))

        # now update layout format

        fig.update_layout(
            title=(f"{yaxis_varname} vs. {xaxis_varname} - Parliament {selected_parliament}" + (f"<br><span style='font-size:12px; color:grey'>Point size corresponds to {size_var.replace('_', ' ').title()}</span>" if size_var else '')),
            xaxis_title=xaxis_varname,
            yaxis_title=yaxis_varname,
            legend=dict(
                title=dict(text='Party'),
                yanchor="top",
                y=1.1,
                xanchor="right",
                x=0.99,
                orientation='h'
            ),
            template='plotly_white'
        )
        
        return fig