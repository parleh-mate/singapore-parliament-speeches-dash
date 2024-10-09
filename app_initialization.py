import dash
import dash_bootstrap_components as dbc

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
server = app.server  # Expose the Flask app as a variable
