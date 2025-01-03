import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde
import math

from load_data import data
from utils import position_threshold_low, position_threshold_high

def create_speech_lengths_kde():

    # get speech length graph
    speech_lengths = data['method-speech-lengths'].count_speeches_words

    # Calculate KDE with custom bandwidth
    kde = gaussian_kde(speech_lengths, bw_method=0.2)

    # Define thresholds

    x_min = speech_lengths.min()
    x_max = speech_lengths.max()
    x_range = np.linspace(x_min, x_max, 2000)
    x_range = np.append(x_range, [position_threshold_low, position_threshold_high])
    x_range.sort()

    # Evaluate KDE
    kde_values = kde(x_range)

    # Create masks for different regions
    mask_left = x_range <= position_threshold_low
    mask_middle = (x_range >= position_threshold_low) & (x_range <= position_threshold_high)
    mask_right = x_range >= position_threshold_high

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
    fig.add_vline(x=position_threshold_low, line=dict(color="black", width=1, dash="dash"))
    fig.add_vline(x=position_threshold_high, line=dict(color="black", width=1, dash="dash"))

    # add label, we find the log scaled midpoint
    x_coords = [math.log10(position_threshold_low*10)/2, # 10 is origin
                math.log10(position_threshold_low*position_threshold_high)/2,
                math.log10(position_threshold_high*x_max)/2]

    # get the area under curve or prop
    text_labels = [np.round(np.mean(speech_lengths<=position_threshold_low)*100, 1),
                np.round(np.mean((speech_lengths>position_threshold_low) & (speech_lengths<=position_threshold_high))*100, 1),
                np.round(np.mean(speech_lengths>position_threshold_high)*100, 1)]

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

    return fig