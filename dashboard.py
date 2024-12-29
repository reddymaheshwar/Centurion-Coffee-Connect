import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

# Load the data
file_path = "coffee_shop_purchases.xlsx"
try:
    purchase_data = pd.read_excel(file_path, engine="openpyxl")
    purchase_data['Date'] = pd.to_datetime(purchase_data['Date'])  # Ensure 'Date' is in datetime format
except Exception as e:
    raise Exception(f"An error occurred while loading the file: {e}")

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Centurion Coffee Connect"

# Layout
app.layout = html.Div([
   
    html.H1("Centurion Coffee Connect Dashboard", style={"textAlign": "center"}),

    dcc.Tabs([
        dcc.Tab(label="Overview", children=[
            html.Div([
                html.H3("Total Revenue", style={"textAlign": "center"}),
                html.H4(f"{purchase_data['Price'].sum():,.2f} Rs", style={"textAlign": "center"}),

                html.H3("Revenue by Product", style={"textAlign": "center", "marginTop": 20}),
                dcc.Graph(
                    id="product-revenue-chart",
                    figure=px.bar(
                        purchase_data.groupby("Product")['Price'].sum().reset_index(),
                        x="Product", y="Price",
                        title="Revenue by Product",
                        labels={"Price": "Revenue (Rs)"},
                        color="Price",
                        color_continuous_scale="Blues"
                    )
                )
            ])
        ]),

        dcc.Tab(label="Daily Trends", children=[
            html.Div([
                dcc.Dropdown(
                    id="days-dropdown",
                    options=[
                        {"label": "Last 7 Days", "value": 7},
                        {"label": "Last 30 Days", "value": 30},
                        {"label": "Last 365 Days", "value": 365}
                    ],
                    value=7,
                    placeholder="Select Time Range",
                    style={"width": "50%", "margin": "auto"}
                ),
                dcc.Graph(id="daily-revenue-chart")
            ])
        ]),

        dcc.Tab(label="Monthly Trends", children=[
            html.Div([
                dcc.Graph(
                    id="monthly-revenue-chart",
                    figure=px.scatter(
                        purchase_data.groupby(purchase_data['Date'].dt.to_period("M").astype(str))['Price'].sum().reset_index(),
                        x="Date", y="Price",
                        size="Price",
                        title="Monthly Revenue Trends",
                        labels={"Price": "Revenue (Rs)", "Date": "Month"},
                        color="Price",
                        color_continuous_scale="Greens"
                    )
                )
            ])
        ]),

        dcc.Tab(label="Product Insights", children=[
            html.Div([
                dcc.Dropdown(
                    id="product-days-dropdown",
                    options=[
                        {"label": "Last 1 Day", "value": 1},
                        {"label": "Last 30 Days", "value": 30},
                        {"label": "Last 365 Days", "value": 365},
                        {"label": "Total Available Days", "value": 0}  # Use 0 for total available days
                    ],
                    value=0,  # Set default to "Total Available Days"
                    placeholder="Select Time Range",
                    style={"width": "50%", "margin": "auto"}
                ),
                dcc.Graph(id="product-sales-chart")
            ])
        ]),

        dcc.Tab(label="Enquiry", children=[
            html.Div([
                html.H3("Find Purchases by ERP ID", style={"textAlign": "center", "marginTop": 20}),
                dcc.Input(
                    id="erp-input",
                    type="text",
                    placeholder="Enter ERP ID",
                    style={"width": "50%", "margin": "10px auto", "display": "block"}
                ),
                html.Button("Submit", id="submit-button", n_clicks=0, style={"display": "block", "margin": "10px auto"}),
                html.Div(id="enquiry-output", style={"textAlign": "center", "marginTop": 20})
            ])
        ])
    ])
])

# Callbacks
@app.callback(
    Output("daily-revenue-chart", "figure"),
    [Input("days-dropdown", "value")]
)
def update_daily_chart(selected_days):
    if not selected_days:
        return {}

    end_date = purchase_data['Date'].max()
    start_date = end_date - pd.Timedelta(days=selected_days)
    filtered_data = purchase_data[(purchase_data['Date'] >= start_date) & (purchase_data['Date'] <= end_date)]
    daily_sales = filtered_data.groupby("Date")['Price'].sum().reset_index()

    figure = px.line(
        daily_sales, x="Date", y="Price",
        title=f"Daily Revenue for Last {selected_days} Days",
        labels={"Price": "Revenue (Rs)"}
    )
    return figure

@app.callback(
    Output("product-sales-chart", "figure"),
    [Input("product-days-dropdown", "value")]
)
def update_product_pie_chart(selected_days):
    if selected_days == 0:  # Total available data
        filtered_data = purchase_data
    else:
        end_date = purchase_data['Date'].max()
        start_date = end_date - pd.Timedelta(days=selected_days)
        filtered_data = purchase_data[(purchase_data['Date'] >= start_date) & (purchase_data['Date'] <= end_date)]

    product_revenue = filtered_data.groupby("Product")['Price'].sum().reset_index()

    figure = px.pie(
        product_revenue, names="Product", values="Price",
        title=f"Revenue Distribution for Last {selected_days if selected_days != 0 else 'All'} Days",
        labels={"Price": "Revenue (Rs)"}
    )
    return figure

@app.callback(
    Output("enquiry-output", "children"),
    [Input("submit-button", "n_clicks")],
    [State("erp-input", "value")]
)
def show_user_purchases(n_clicks, erp_id):
    if n_clicks > 0 and erp_id:
        filtered_data = purchase_data[purchase_data['ERP'].astype(str) == str(erp_id)]
        if not filtered_data.empty:
            total_purchases = filtered_data['Price'].sum()
            return html.Div([
                html.H4(f"Total Purchases for ERP {erp_id}: {total_purchases:,.2f} Rs"),
                dcc.Graph(
                    figure=px.bar(
                        filtered_data.groupby("Product")['Price'].sum().reset_index(),
                        x="Product", y="Price",
                        title=f"Purchases for ERP {erp_id}",
                        labels={"Price": "Revenue (Rs)"},
                        color="Price",
                        color_continuous_scale="Blues"
                    )
                )
            ])
        else:
            return html.H4(f"No purchases found for ERP {erp_id}.")
    return ""

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
