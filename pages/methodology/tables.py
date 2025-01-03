from dash import dash_table
import pandas as pd

def create_topics_table():

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

    return topics_table