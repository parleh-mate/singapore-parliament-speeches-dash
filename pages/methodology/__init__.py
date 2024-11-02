from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

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

def methodology_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Methodology"),
                        html.P(
                            "This section describes how our data is sourced and transformed into the graphs and tables you see on the app. Our aim is to be as transparent as possible and provide users with the necessary context to understand what they are looking at."
                        ),                        
                        # Table of Contents
                        html.Ul([
                            html.Li(html.A("Data Sourcing", href="#datasourcing-method")),
                            html.Li(html.A("Participation", href="#participation-method")),
                            html.Li(html.A("Questions", href="#questions-method")),
                            html.Li(html.A("Speeches", href="#speeches-method")),
                            html.Li(html.A("Topics", href="#topics-method")),
                            html.Li(html.A("Demographics", href="#demographics-method")),
                        ]),
    
                        html.H2("Data Sourcing", id="datasourcing-method"),
                        html.P(
                            "All data comes courtesy of the Singapore Parliament Hansards."
                        ),
                        
                        html.H2("Participation", id="participation-method"),
                        html.P(
                            "How is participation defined? Spoke at least once even if procedural speech?"
                            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
                        ),
                        
                        html.H2("Speeches", id="speeches-method"),
                        html.P([
                            "How are speeches summarized and labelled?",
                            html.Br(),
                            html.Br(),
                            "Speeches are summarized to about 150 words with the help of GPT's 4o-mini model. We do not include written corrections, bill introductions, voting protocols, President's addresses, or speeches made by the Speaker (usually procedural in nature) since none of these can be really considered a parliamentary speech. We also limit the speeches passed to the API to between 70 and 2000 words. An upper word limit is necessary because of GPT's context length limit of ~4000 tokens, while a lower limit helps to exclude non-substantive procedural speeches. An example of a procedural speech is as follows:",
                            html.Br(),
                            html.Br()
                        ]),                            
                        html.Blockquote([
                            'Mdm Speaker, may I ask the Member to clarify his first question? What does he mean by "supplementary schemes"?',
                            ],
                            className="blockquote"
                            ),
                        html.P([
                            html.Br(),
                            "The speech is non-substantive and a waste of resources if summarized. Ultimately 70 words corresponds to about a 30-second speech which we do not believe conveys much information even if substantive in nature. Imposing a strict word-limit is also much quicker than manually going through each speech and labeling it as substantive or not, since this information does not come with the data. The following graph highlights the distribution of speech lengths and what we exclude in our summaries. In total our method excludes only xx% of speeches."
                        ]),    
                        html.H2("Topics", id="topics-method"),
                        html.P([
                            "Topics are labelled by GPT and are done at the same time as speech summarization. Our approach to topic labelling is semi-principled and involves a combination of unsupervised topic modelling and human interpretation to identify a set list of topics which we then pass to GPT. We first use a Latent Dirichlet Allocation (LDA) model to group words into 25 topics. We then use our own subjective judgement to label each topic based on the top 15 most important words in each topic, and then decide if a topic is relevant enough to be included in the final list.",
                            html.Br(),
                            html.Br(),
                            "As can be observed from the table below, some topics like 23 and 24 contain words that do not belong to a coherent topic and are excluded. Topics like 2 (Religion) and 7 (Animal Welfare) were also excluded due to the likely rarity of these topics in parliament, though perhaps an argument can be made for Religion. Finally, some topics like 18 were further split into sub-topics ('Military Defense and National Security' and 'Foreign Policy') based on our interpretation of the top words. The full script for the LDA model can be found here.",
                            html.Br(),
                            html.Br(),
                            topics_table
                        ]),      
                
                        html.H2("Questions", id="questions-method"),
                        html.P(
                            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
                        ),            
                        
                        html.H2("Demographics", id="demographics-method"),
                        html.P(
                            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
                        ),
                    ],
                    width=10  # Occupy 10 out of 12 columns (~83.33% width)
                ),
                justify="center"  # Center the column within the row
            ),
        ],
        fluid=True,  # Ensures the container spans the full width of the viewport
        style={'padding': '20px'}
    )

