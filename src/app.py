import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name%s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    # Initialize the Dash app with external stylesheets
    app = Dash(__name__, suppress_callback_exceptions=True)

    # For web deployment
    server = app.server

    # Read the data
    import os
    import sys

    # Get the absolute path to the data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'data', 'df_top.csv')

    try:
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"__file__ location: {__file__}")
        logger.info(f"Attempting to load data from: {data_path}")
        
        # List the contents of the directory where the file should be
        data_dir = os.path.dirname(data_path)
        if os.path.exists(data_dir):
            logger.info(f"Contents of {data_dir}:")
            logger.info(str(os.listdir(data_dir)))
        else:
            logger.error(f"Data directory does not exist: {data_dir}")
        
        # Try to read the file
        if os.path.exists(data_path):
            df_top = pd.read_csv(data_path)
            logger.info("Successfully loaded the data file")
        else:
            raise FileNotFoundError(f"Data file not found at: {data_path}")

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        logger.error(f"Stack trace:", exc_info=True)
        raise

    # Convert relevant columns to numeric types, coerce errors to NaN
    columns_to_convert = [
        'First Financing Size', 'First Financing Valuation',
        'Revenue', 'Revenue Growth %', 'Net Income', 'Net Debt', 'Market Cap',
        'Gross Profit', 'Enterprise Value', 'EBITDA', 'EBIT',
        'Total Patent Document', 'Total Clinical Trials', '#Active Investors'
    ]

    for col in columns_to_convert:
        df_top[col] = pd.to_numeric(df_top[col], errors='coerce')

    # Group data by 'Primary Industry Group' and calculate descriptive statistics
    grouped = df_top.groupby('Primary Industry Group')[columns_to_convert].agg(['mean', 'median', 'std', 'count'])

    # Flatten the multi-level column names in the grouped DataFrame
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns]

    # Adjust column names for compatibility with Dash DataTable
    grouped.columns = [col.replace(' ', '_').replace('(', '').replace(')', '') for col in grouped.columns]

    print("Grouped DataFrame:")
    print(grouped.head())

    print("Grouped DataFrame after flattening and adjustments:")
    print(grouped.head())

    app.layout = html.Div([
        html.H1("Analysis Dashboard", style={
            'textAlign': 'center', 
            'color': '#2c3e50', 
            'margin-bottom': '30px',
            'font-family': 'Arial, sans-serif',
            'font-size': '2.5em'
        }),

        html.Div([
            html.Label("Select Variable for Analysis:", style={
                'font-weight': 'bold', 
                'margin-bottom': '10px',
                'font-family': 'Arial, sans-serif',
                'font-size': '1.2em'
            }),
            dcc.Dropdown(
                id='variable-dropdown',
                options=[{'label': col, 'value': col} for col in columns_to_convert],
                value='First Financing Size',
                style={
                    'margin-bottom': '20px',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '1em',
                    'padding': '10px',
                    'border-radius': '5px',
                    'box-shadow': 'none',
                    'background-color': '#f9f9f9'
                }
            ),
        ], style={
            'width': '50%', 
            'margin': 'auto', 
            'margin-bottom': '30px',
            'background-color': '#f9f9f9',
            'padding': '20px',
            'border-radius': '10px',
            'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
        }),

        dcc.Graph(id='box-plot', style={'margin-bottom': '30px'}),
        dcc.Graph(id='industry-group-bar-plot', style={'margin-bottom': '30px'}),

        html.Div([
            html.H3("Descriptive Statistics by Top 10 Primary Industry Group", style={
                'textAlign': 'center',
                'font-family': 'Arial, sans-serif',
                'font-size': '1.5em',
                'margin-bottom': '20px'
            }),
            dash_table.DataTable(
                id='descriptive-stats-table',
                columns=[{"name": col, "id": col} for col in grouped.reset_index().columns],
                data=grouped.reset_index().to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'minWidth': '150px', 'width': '200px', 'maxWidth': '300px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left',
                    'padding': '10px',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '0.9em'
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '1em'
                },
                sort_action='native',
                filter_action='native',
                row_selectable='multi',
                selected_rows=[],
            ),
            html.Button("Download CSV", id="download-button", n_clicks=0, style={
                'margin-top': '20px',
                'padding': '10px 20px',
                'font-size': '1em',
                'background-color': '#2c3e50',
                'color': 'white',
                'border': 'none',
                'border-radius': '5px',
                'cursor': 'pointer'
            }),
            dcc.Download(id="download-csv"),
        ], style={
            'margin': '50px 0',
            'background-color': '#f9f9f9',
            'padding': '20px',
            'border-radius': '10px',
            'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
        }),

        html.Div([
            html.H3("Top 10 Primary Industry Group Data Table", style={
                'textAlign': 'center',
                'font-family': 'Arial, sans-serif',
                'font-size': '1.5em',
                'margin-bottom': '20px'
            }),
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df_top.columns],
                data=df_top.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left',
                    'padding': '10px',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '0.9em'
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '1em'
                },
                filter_action='custom',
                filter_query='',
                style_filter={
                    'backgroundColor': '#f9f9f9',
                    'color': '#333',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '0.9em',
                    'padding': '5px',
                    'border': '1px solid #ccc',
                    'border-radius': '5px'
                },
                sort_action='native',
                row_selectable='multi',
                selected_rows=[],
            )
        ], style={
            'margin': '50px 0',
            'background-color': '#f9f9f9',
            'padding': '20px',
            'border-radius': '10px',
            'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
        })
    ], style={
        'padding': '20px',
        'background-color': '#f4f4f4',
        'font-family': 'Arial, sans-serif'
    })

    @app.callback(
        [Output('box-plot', 'figure'),
         Output('industry-group-bar-plot', 'figure')],
        Input('variable-dropdown', 'value')
    )
    def update_graphs(selected_variable):
        # Create box plot
        box_fig = px.box(
            df_top, 
            x='Primary Industry Group', 
            y=selected_variable, 
            title=f'Box Plot of {selected_variable} by Primary Industry Group',
            hover_data=['Company'] if 'Company' in df_top.columns else None
        )
        box_fig.update_layout(
            xaxis_title='Primary Industry Group', 
            yaxis_title=selected_variable, 
            xaxis_tickangle=-45,
            height=600,
            template='plotly_white'
        )

        # Create bar plot
        bar_fig = px.bar(
            df_top.groupby('Primary Industry Group').size().reset_index(name='Company Count'),
            x='Primary Industry Group',
            y='Company Count',
            title='Company Count per Primary Industry Group',
            text='Company Count'
        )
        bar_fig.update_layout(
            xaxis_title='Primary Industry Group',
            yaxis_title='Company Count',
            xaxis_tickangle=-45,
            height=600,
            template='plotly_white'
        )

        return box_fig, bar_fig

    @app.callback(
        Output("download-csv", "data"),
        Input("download-button", "n_clicks"),
        prevent_initial_call=True
    )
    def download_csv(n_clicks):
        return dcc.send_data_frame(grouped.reset_index().to_csv, "descriptive_statistics.csv")

    if __name__ == '__main__':
        app.run_server(debug=True)

except Exception as e:
    logger.error("Unhandled exception during application startup", exc_info=True)
    raise
