from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import math

from load_data import data
from utils import top_k_rag_policy_positions

df_topics = pd.read_csv("assets/topics_LDA.csv").sort_values("topic").drop(columns = "mean_word_weight")

# read topics table

# Create a DataTable from the DataFrame
topics_table = dash_table.DataTable(
    data=df_topics.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_topics.columns],
    style_table={
        'width': '100%',       
        'overflowX': 'hidden',  
        'maxHeight': '400px',
        'overflowY': 'auto'
    },
    style_cell={
        'textAlign': 'left',
        'padding': '8px',
        'font-family': 'Arial, sans-serif',
        'font-size': '12px',
        'whiteSpace': 'normal',   # Enable text wrapping
        'wordWrap': 'break-word', # Break long words
    },
    style_header={
        'backgroundColor': '#f2f2f2',
        'fontWeight': 'bold'
    }
)

# get speech length graph
speech_lengths = data['method-speech-lengths'].count_speeches_words


# Calculate KDE with custom bandwidth
kde = gaussian_kde(speech_lengths, bw_method=0.2)

# Define thresholds
threshold_low = 70
threshold_high = 2000
x_min = speech_lengths.min()
x_max = speech_lengths.max()
x_range = np.linspace(x_min, x_max, 2000)
x_range = np.append(x_range, [threshold_low, threshold_high])
x_range.sort()

# Evaluate KDE
kde_values = kde(x_range)

# Create masks for different regions
mask_left = x_range <= threshold_low
mask_middle = (x_range >= threshold_low) & (x_range <= threshold_high)
mask_right = x_range >= threshold_high

# Left region data
x_left = x_range[mask_left]
y_left = kde_values[mask_left]

# Middle region data
x_middle = x_range[mask_middle]
y_middle = kde_values[mask_middle]

# Right region data
x_right = x_range[mask_right]
y_right = kde_values[mask_right]

# Initialize the figure
fig = go.Figure()

# Add filled area for the left region (x <= 70)
fig.add_trace(go.Scatter(
    x=x_left,
    y=y_left,
    mode='lines',
    fill='tozeroy',
    fillcolor='rgba(255, 153, 153, 0.6)',  # Semi-transparent green
    line=dict(color='rgba(0, 128, 0, 0)'),  # Invisible line
    name='<= 70 words',
    hoverinfo='skip'  # Disable hover for filled areas
))


# middle region
fig.add_trace(go.Scatter(
    x=x_middle,
    y=y_middle,
    mode='lines',
    fill='tozeroy',
    fillcolor='rgba(186, 255, 201, 0.6)',  
    line=dict(color='rgba(128, 128, 128, 0)'),  # Invisible line
    name='70 < x <= 2k words',
    hoverinfo='skip'
))

# Add filled area for the right region (x > 2000)
fig.add_trace(go.Scatter(
    x=x_right,
    y=y_right,
    mode='lines',
    fill='tozeroy',
    fillcolor='rgba(216, 191, 216, 0.6)',  
    line=dict(color='rgba(255, 0, 0, 0)'),  # Invisible line
    name='> 2k words',
    hoverinfo='skip'
))


# Add vertical lines at x=70 and x=2000
fig.add_vline(x=threshold_low, line=dict(color="black", width=1, dash="dash"))
fig.add_vline(x=threshold_high, line=dict(color="black", width=1, dash="dash"))

# add label, we find the log scaled midpoint
x_coords = [math.log10(threshold_low*10)/2, # 10 is origin
            math.log10(threshold_low*threshold_high)/2,
            math.log10(threshold_high*x_max)/2]

# get the area under curve or prop
text_labels = [np.round(np.mean(speech_lengths<=threshold_low)*100, 1),
               np.round(np.mean((speech_lengths>threshold_low) & (speech_lengths<=threshold_high))*100, 1),
               np.round(np.mean(speech_lengths>threshold_high)*100, 1)]

for x, text in zip(x_coords, text_labels):
    # Add annotation
    fig.add_annotation(
        x=x,  # x-coordinate
        y=0.001,  # y-coordinate
        text=f"{text}%",  # Text to display
        showarrow=False,
        font=dict(
            color="black",  # Font color
            size=12         # Font size
        ),
        align="center"
    )

# Update the layout
fig.update_layout(
    title="Density of Speech Lengths" + '<br>' + '<span style="font-size:12px; color:grey">X-axis is log scaled</span>',
    xaxis_title="Number of Words",
    yaxis_title="Density",
    xaxis_type="log",
    template="plotly_white",
    hovermode="closest",
    legend=dict(
        x=0.99,
        y=0.99,
        xanchor='right',
        yanchor='top'
    ),
    legend_title_text='Legend'
)

fig.update_yaxes(showticklabels=False)

def methodology_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Methodology"),
                        html.P(
                            "This section describes how data is sourced and transformed into the graphs and tables you see on the app. While best efforts are made to ensure the information is accurate, there may be inevitable parsing errors. Please use the information here with caution and check the underlying data."
                        ),                        
                        # Table of Contents
                        html.Ul([
                            html.Li(html.A("Why is there no data before 2011?", href="#before-data-faq")),
                            html.Li(html.A("Data Sourcing", href="#datasourcing-method")),
                            html.Li(html.A("Policy Positions", href="#policy-method")),
                            
                            # Member Metrics with nested sub-items
                            html.Li([
                                "Member Metrics",
                                html.Ul([
                                    html.Li(html.A("Participation", href="#participation-method")),
                                    html.Li(html.A("Attendance", href="#attendance-method")),
                                    html.Li(html.A("Speeches", href="#speeches-method")),
                                    html.Li(html.A("Readability", href="#readability-method")),
                                    html.Li(html.A("Questions", href="#questions-method")),
                                ])
                            ]),
                            html.Li(html.A("Topics", href="#topics-method")),
                            html.Li(html.A("Demographics", href="#demographics-method")),
                        ]),

                        html.H2("Why is data only available for certain timeframes?", id="before-data-faq"),
                        html.P([
                            "The API in principle provides all parliamentary sitting data from 1955 to present, with the exception of bill data which is only available from 2006. However the data format of speeches before 2012 is highly unstructured and requires significant effort to parse. This remains something we are keen to tackle in future."
                        ]),
    
                        html.H2("Data Sourcing", id="datasourcing-method"),
                        html.P([
                            "All data comes courtesy of the Singapore Parliament Hansards API. A request is made to the API at 00:00 SGT every day to check for new speeches, which are usually added to the Hansards ~2 weeks after a sitting. Data is then transformed and stored on BigQuery. Information on the data lineage can be found on the ",
                            html.A(
                                "DBT documentation page",
                                href="https://cloud.getdbt.com/accounts/237272/jobs/506988/docs/#!/overview",  # Replace with actual URL
                                target="_blank",  # Opens the link in a new tab
                                style={'color': '#007bff', 'textDecoration': 'underline'}
                            ),
                            ", or visit the ",
                            html.A(
                                "Github repository",
                                href="https://github.com/parleh-mate",  # Replace with actual URL
                                target="_blank",  # Opens the link in a new tab
                                style={'color': '#007bff', 'textDecoration': 'underline'}
                            ),
                            " for more info."
                        ]),
                        html.H2("Policy Positions", id="policy-method"),
                        html.P([
                            dcc.Markdown(f"Policy positions are generated by summarizing the top {top_k_rag_policy_positions} speech summaries most related to the user-submitted query using GPT's `4o` model. Indexing of related speeches is done using a vector database and GPT's `text-embedding-3-small` model, while speech summaries are pre-generated using GPT's `4o-mini` model. We use speech summaries instead of raw speeches since this is quicker and more cost efficient, though possibly at the risk of some information loss. Only speeches between 70-2000 words are summarized. These do not include written corrections, bill introductions, voting protocols, President's addresses, or speeches made by the Speaker (usually procedural in nature) since none of these can be really considered a parliamentary speech. The word limit is imposed to exclude extremely long speeches or short procedural ones like the following:"),
                            html.Br()
                        ]),                            
                        html.Blockquote([
                            '"Mdm Speaker, may I ask the Member to clarify his first question? What does he mean by "supplementary schemes"?"',
                            ],
                            className="blockquote"
                            ),
                        html.P([
                            html.Br(),
                            "The following graph highlights the distribution of speech lengths and what we exclude in our summaries. Information on our GPT prompts can be found in the Github repository.",
                            dcc.Graph(
                                id='speeches-length-graph',
                                figure=fig,
                                config={"responsive": True},
                                style={'minHeight': '300px'}
                                )
                        ]),
                        html.H2("Member Metrics"),
                        html.Br(),
                        html.H3("Participation", id="participation-method", style={'marginLeft': '20px'}),
                        html.P([
                            "Participation is measured by the number of sessions in which the member spoke at least once as a proportion of the number of sessions the member attended. This includes every form of verbal participation including procedural speeches but excludes written responses. For example, in the 13th parliament Walter Theseira (NMP) had a participation rate of 94.2%, meaning that he spoke in 94.2% of the of 98.1% of sessions he attended."
                            ], style={'marginLeft': '20px'}),
                        html.H3("Attendance", id="attendance-method", style={'marginLeft': '20px'}),
                        html.P([
                            "Attendance is measured by the number of sessions the member attended (or was present in) out of the total number of sessions which occurred while they were sitting as a member. For example, WP's Lee Li Lian won the Punggol East SMC by-election in January 2013 as the 12th parliament was underway. Her attendance is calculated as the proportion of the remaining 80 sittings she was qualified to attend instead of the total 89."
                            ], style={'marginLeft': '20px'}),
                        html.H3("Speeches", id="speeches-method", style={'marginLeft': '20px'}),
                        html.P([
                            "Speeches refers to any time a member speaks to address the chamber as recorded in the parliamentary Hansard. This includes substantial and procedural points but does not include written answers, parliamentary questions, or the President's address. Members who made no speeches do not appear on the graph."
                            ], style={'marginLeft': '20px'}),
                        html.H3("Readability", id="readability-method", style={'marginLeft': '20px'}),
                        html.P("To assess how readable a speech is, we use the Flesch-Kincaid score, a widely used index for measuring how difficult a text is to understand in English. The formula is as follows:"
                            , style={'marginLeft': '20px'}),
                        html.P(
                            dcc.Markdown(r'$$206.835 - 1.015 \left( \frac{\text{total words}}{\text{total sentences}} \right) - 84.6 \left( \frac{\text{total syllables}}{\text{total words}} \right)$$', mathjax=True),
                            style={'textAlign': 'center'}
                        ),
                        html.P("The index scales from 0 to 100, with 0 indicating extremely difficult and 100 very easy. Generally, a score of between 30-50 is a college level text, while 10-30 is college-graduate level. Members who did not speak do not have a readability score and will not appear on the graph. Vernacular speeches are also not given a readability score since the index only works for English.", style={'marginLeft': '20px'}),
                        html.H3("Questions", id="questions-method", style={'marginLeft': '20px'}),
                        html.P(
                            "Parliamentary questions (PQ) do not come labelled in the raw data and are only identified during the data modelling process. Fortunately, they are also almost always recorded in the Hansards in the following format: 'asked the <insert minister here> <insert question here>'. For example, the PQ below was directed by Don Wee (PAP) during a sitting in Parliament 14.",
                            style={'marginLeft': '20px'}
                        ),
                        html.Blockquote([
                            '"asked the Minister for Sustainability and the Environment what are the criteria, such as the number of dwelling units, to set up a hawker centre and wet market within a constituency."',
                            ],
                            className="blockquote",
                            style={'marginLeft': '20px'}
                            ),
                        html.P(
                            "We use this information to determine if 1) a speech was a question, and 2) which ministry the question was directed towards. Note that cabinet ministers do not raise questions but answer them instead.",
                            style={'marginLeft': '20px'}
                        ),                  
                        html.H2("Topics", id="topics-method"),
                        html.P([
                            "Topics are labelled by GPT and are done at the same time as speech summarization. Our approach is semi-principled and involves a combination of unsupervised topic modelling and human interpretation to identify a set list of topics which we then pass to GPT. We first use a Latent Dirichlet Allocation (LDA) model to group words into 25 topics. We then use our own subjective judgement to label each topic based on the top 15 most important words in each topic, and then decide if a topic is relevant enough to be included in the final list. We end up with a list of 17 topics.",
                            html.Br(),
                            html.Br(),
                            "As can be observed from the table below, some topics like 23 and 24 contain words that do not belong to a coherent topic and are excluded. Topics like 2 (Religion) and 7 (Animal Welfare) were also excluded due to the likely rarity of these topics in parliament. Some topics like 18 were further split into sub-topics ('Military Defense and National Security' and 'Foreign Policy') based on our interpretation of the top words. Finally, topics 3, 4, and 19 were grouped under a single header of 'Urban Planning', again to minimize esoteric topics.",
                            html.Br(),
                            html.Br(),
                            topics_table,
                            html.Br()
                        ]),    
                        html.H2("Demographics", id="demographics-method"),
                        html.P([
                            "We use year-age in place of actual age due to the lack of information on birthdates. Because MPs can come and go during the lifetime of an entire parliament session (especially NMPs), we look at an MP's age at their first sitting rather than at the start of session.",
                            html.Br(),
                            html.Br(),
                            "The parliamentary Hansards comes with information on an MP's gender but not ethnicity. Where possible, we locate this information through manual web searches, otherwise it is derived by looking at the name. In most cases this is straightforward, but in some we remain unsure. For example, Walter Theseira (NMP) and Christopher de Souza (PAP) were labelled as 'Others', while Mohamed Irshad (NMP) was labelled as Indian."
                        ]),
                    ],
                    width=10  # Occupy 10 out of 12 columns (~83.33% width)
                ),
                justify="center"  # Center the column within the row
            ),
        ],
        fluid=True,  # Ensures the container spans the full width of the viewport
        style={'padding': '20px'}
    )