from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import math

from load_data import load_gpt_prompts, load_speech_lengths

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
speech_lengths = load_speech_lengths().count_speeches_words

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

# load gpt prompts
gpt_df = load_gpt_prompts()

# output summary description
output_sum = gpt_df.output_summary_description[0].split('\n')
output_sum.remove('')
output_sum = [f'"{i}"' for i in output_sum]
output_sum = ',html.Br(),'.join(output_sum)

#output topic description
output_topic = gpt_df.output_topic_description[0].split('\n')
output_topic = [f'"{i}"' for i in output_topic]
output_topic = ',html.Br(),'.join(output_topic)

def methodology_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Methodology"),
                        html.P(
                            "This section describes how our data is sourced and transformed into the graphs and tables you see on the app. Our aim is to be as transparent as possible and provide users with the necessary context to understand what they are looking at. While best efforts are made to ensure the information is accurate, there may be inevitable parsing errors. Please use the information here with caution and check the underlying data."
                        ),                        
                        # Table of Contents
                        html.Ul([
                            html.Li(html.A("Why is there no data before 2011?", href="#before-2012-faq")),
                            html.Li(html.A("Data Sourcing", href="#datasourcing-method")),
                            html.Li(html.A("Participation", href="#participation-method")),
                            html.Li(html.A("Speeches", href="#speeches-method")),
                            html.Li(html.A("Topics", href="#topics-method")),
                            html.Li(html.A("GPT Prompts", href="#gpt-method")),
                            html.Li(html.A("Questions", href="#questions-method")),
                            html.Li(html.A("Demographics", href="#demographics-method")),
                        ]),

                        html.H2("Why is there no data before 2011?", id="before-2012-faq"),
                        html.P([
                            "The API in principle provides all parliamentary data from 1955 to present. However the data format of speeches before 2011 is highly unstructured and will require a significant amount of time to manually parse, time that we as volunteers do not have. However it remains something we are keen to explore in the future."
                        ]),
    
                        html.H2("Data Sourcing", id="datasourcing-method"),
                        html.P([
                            "All data comes courtesy of the Singapore Parliament Hansards API. We automate a Python script to call the API at 00:00 SGT every day to check for the addition of new speeches. Speeches are usually added to the Hansards ~2 weeks after a sitting. New speeches are then pulled into a database on BigQuery before being transformed into cleaned data which we also host on BigQuery and use for our graphs. This is also when speech summaries and topic labels for new speeches are generated. Information on the data lineage can be found on the ",
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
                        
                        html.H2("Participation", id="participation-method"),
                        html.P([
                            "We define an MP who spoke at least once during a sitting as having participated verbally in that session. This includes every form of verbal participation including procedural speeches but excludes written responses."
                            ]),
                        
                        html.H2("Speeches", id="speeches-method"),
                        html.P([
                            "How are speeches summarized and labelled?",
                            html.Br(),
                            html.Br(),
                            "Speeches are summarized to about 150 words with the help of GPT's 4o-mini model. We do not include written corrections, bill introductions, voting protocols, President's addresses, or speeches made by the Speaker (usually procedural in nature) since none of these can be really considered a parliamentary speech. We also make sure summaries are written in the third person to prevent wrongful attribution and limit the speeches passed to the API to between 70 and 2000 words. An upper word limit is necessary because of GPT's context length limit of ~4000 tokens, while a lower limit helps to exclude non-substantive procedural speeches. The idea is that a summary only makes sense if the speech is substantive. An example of a procedural speech is as follows:",
                            html.Br(),
                            html.Br()
                        ]),                            
                        html.Blockquote([
                            '"Mdm Speaker, may I ask the Member to clarify his first question? What does he mean by "supplementary schemes"?"',
                            ],
                            className="blockquote"
                            ),
                        html.P([
                            html.Br(),
                            "The speech is from a sitting in the 12th Parliament by Sim Ann (PAP) and is an example of something that is procedural and too unsubstantive to be worth summarizing. Ultimately 70 words corresponds to about a 30-second speech which we do not believe conveys much information even if substantive in nature. Imposing a strict word-limit is also much quicker than manually going through each speech to determine if they are substantive. The following graph highlights the distribution of speech lengths and what we exclude in our summaries.",
                            dcc.Graph(
                                id='speeches-length-graph',
                                figure=fig,
                                config={"responsive": True},
                                style={'minHeight': '300px'}
                                )
                        ]),    
                        html.H2("Topics", id="topics-method"),
                        html.P([
                            "Topics are labelled by GPT and are done at the same time as speech summarization. Our approach to topic labelling is semi-principled and involves a combination of unsupervised topic modelling and human interpretation to identify a set list of topics which we then pass to GPT. We first use a Latent Dirichlet Allocation (LDA) model to group words into 25 topics. We then use our own subjective judgement to label each topic based on the top 15 most important words in each topic, and then decide if a topic is relevant enough to be included in the final list. We end up with a list of 17 topics.",
                            html.Br(),
                            html.Br(),
                            "As can be observed from the table below, some topics like 23 and 24 contain words that do not belong to a coherent topic and are excluded. Topics like 2 (Religion) and 7 (Animal Welfare) were also excluded due to the likely rarity of these topics in parliament, though perhaps an argument can be made for Religion. Some topics like 18 were further split into sub-topics ('Military Defense and National Security' and 'Foreign Policy') based on our interpretation of the top words. Finally, topics 3, 4, and 19 were grouped under a single header of 'Urban Planning', again to minimize esoteric topics.",
                            html.Br(),
                            html.Br(), 
                            "LDA models are probabilistic in nature and do not account for semantic meaning between words in a sentence. This is a major flaw and partly why so much human interpretation is required, despite multiple attempts at fine tuning. As a next step we are looking to test the use of sentence transformers to better account for semantic meaning. The full script for the LDA model can be found ",
                            html.A(
                                "here",
                                href="https://colab.research.google.com/drive/1Egok9pP6vgV2gC2lVNIFH9v9SdcFoqY1?usp=sharing",
                                target="_blank",  # Opens the link in a new tab
                                style={'color': '#007bff', 'textDecoration': 'underline'}
                            ),
                            ".",
                            html.Br(),
                            html.Br(),
                            topics_table
                        ]),    
                        html.H2("GPT Prompts", id="gpt-method"),
                        html.P([
                            "Our summaries and topics are outputs from a GPT 4o-mini model using GPT's batch API. We also explored the use of Claude's Opus and Sonnet models but these were costlier and performed poorer at summarization across a random sample of speeches. The GPT model employs one-shot learning, meaning each request to summarize and label a speech is independent and the model does not get feedback or 'fine-tuned' after each attempt. To compensate for this, we specify clear, step by step instructions for how the model should perform summarization.",
                            html.Br(),
                            html.Br(),
                            "We find summary performance reasonable, though in <1% of cases the model still hallucinates new topics even after being told explicity not to. In these cases the output is not accepted and the model will try again with a different batch. It is important to note that LLM models can still make errors despite their high-level competency in natural language tasks. As these models improve in cost and capability, so we strive to also improve our summaries and topic labels. Our current prompts are as follows:",
                            html.Br(),
                            html.Br(),
                            html.H4("System Message:"),
                            gpt_df.system_message[0].replace('\n','').strip(),
                            html.Br(),
                            html.Br(),
                            html.H4("Output Summary Description:"),
                            *eval(output_sum),
                            html.Br(),
                            html.Br(),
                            html.H4("Output Topic Description:"),
                            *eval(output_topic)
                            
                    ]),  
                
                        html.H2("Questions", id="questions-method"),
                        html.P(
                            "Speeches do not come labelled as parliamentary questions (PQ) in the raw data and labels are supplemented by us in the data modelling process. Fortunately, they are also almost always recorded in the Hansards in the following format: 'asked the <insert minister here> <insert question here>'. For example, the PQ below was directed by Don Wee (PAP) during a sitting in Parliament 14."
                        ),
                        html.Blockquote([
                            '"asked the Minister for Sustainability and the Environment what are the criteria, such as the number of dwelling units, to set up a hawker centre and wet market within a constituency."',
                            ],
                            className="blockquote"
                            ),
                        html.P(
                            "We use this information to determine if 1) a speech was a question, and 2) which ministry the question was directed towards. It is important to note that cabinet ministers do not raise questions but answer them instead."
                        ),                        
                        html.H2("Demographics", id="demographics-method"),
                        html.P([
                            "We use year-age in place of actual age due to the lack of information on birthdates, though this should not make much difference to the analysis. Because MPs can come and go during the lifetime of an entire parliament session (especially NMPs), we chose to look at an MP's age at first sitting rather than the age of parliament at specific time frames. The former answers the question 'How old are parliamentarians in general when they enter parliament?' and gives an insight into party preferences on the age of candidates who are fielded.",
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