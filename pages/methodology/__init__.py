from dash import html
import dash_bootstrap_components as dbc

def methodology_layout():
    return html.Div(
        [
            html.H1("Methodology/FAQ"),
            html.P(
                "This section describes how our data is sourced and transformed into the graphs and tables you see on the app. Our aim is to be as transparent as possible and provide users with the necessary context to understand what they are looking at."
            ),
            
            # Table of Contents
            html.H4("Methodology"),
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
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
            ),
            
            
            html.H2("Speeches", id="speeches-method"),
            html.P([
                "How are speeches summarized and labelled?",
                html.Br(),
                "Speeches are summarized to about 150 words with the help of GPT's 4o-mini model. We do not include written corrections, bill introductions, or President's addresses since none of these can be really considered a parliamentary speech. We also limit the speeches passed to the API to between 70 and 2000 words. An upper word limit is necessary because of GPT's context length limit of ~4000 tokens, while a lower limit helps to exclude non-substantive procedural speeches. An example of a procedural speech is as follows:",
                html.Br(),
                "XXX",
                html.Br(),
                "The speech is non-substantive and a waste of resources if summarized. Ultimately 70 words corresponds to about a 30-second speech which we do not believe conveys much information even if substantive in nature. Imposing a strict word-limit is also much quicker than manually going through each speech and labeling it as substantive or not, since this information does not come with the data."
            ]
            ),

            html.H2("Topics", id="topics-method"),
            html.P([
                "Topics are labelled by GPT and are done at the same time as speech summarization. Our approach to topic labelling is semi-principled and involves a combination of unsupervised topic modelling and human interpretation to identify a set list of topics which we then pass to GPT. We first use a Latent Dirichlet Allocation (LDA) model to group words into 25 topics. We then use our own subjective judgement to label each topic based on the top 15 most important words in each topic, and then decide if a topic is relevant enough to be included in the final list. We end up with a list of 17 topics.",
                html.Br(),
                "INSERT TABLE HERE"
            ]         
                
            ),      

            html.H2("Questions", id="questions-method"),
            html.P(
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
            ),            
            
            html.H2("Demographics", id="demographics-method"),
            html.P(
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
            ),
        ],
        className='content',
        style={'padding': '20px'}
    )
