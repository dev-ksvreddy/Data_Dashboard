from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import plotly
import plotly.express as px
import json
import os
app = Flask(__name__)

# Fetch data function
def fetch_data(url="https://vtsvcnode1.xyz/api/get-data"):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", [])
            return pd.DataFrame(data)
        else:
            print("Failed to retrieve data:", response.status_code)
            return pd.DataFrame()
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

@app.route('/')
def index():
    try:
        # Fetch data using fetch_data function
        df = fetch_data()

        if df.empty:
            return "No data available to display.", 500

        # Default plot type
        plot_type = request.args.get('plot_type', 'line')

        # Generate graph based on the selected plot type
        if plot_type == 'line':
            fig = px.line(df, x='Timestamp', y='Vehicle_count', title='Vehicle Count Over Time')
        elif plot_type == 'bar':
            fig = px.bar(df, x='Timestamp', y='Vehicle_count', title='Vehicle Count Over Time')
        elif plot_type == 'scatter':
            fig = px.scatter(df, x='Timestamp', y='Vehicle_count', title='Vehicle Count Over Time')
        else:
            return "Invalid plot type selected.", 400

        fig.update_layout(
            xaxis_title='Timestamp',
            yaxis_title='Vehicle Count',
            title_x=0.5,  # Center the title
            template="plotly_white",
        )

        # Convert the Plotly figure to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('index.html', graphJSON=graphJSON)
    except Exception as e:
        return f"Error generating graph: {e}", 500

@app.route('/get-data', methods=['GET'])
def get_paginated_data():
    try:
        # Fetch data
        df = fetch_data()

        if df.empty:
            return jsonify({"message": "No data available"}), 500

        # Pagination parameters
        page = int(request.args.get('page', 1))
        rows_per_page = 100
        start = (page - 1) * rows_per_page
        end = start + rows_per_page

        # Paginate the data
        paginated_data = df.iloc[start:end].to_dict(orient='records')

        # Total number of pages
        total_pages = (len(df) + rows_per_page - 1) // rows_per_page

        return jsonify({
            "data": paginated_data,
            "total_pages": total_pages,
            "current_page": page,
        })
    except Exception as e:
        return jsonify({"message": f"Error fetching paginated data: {e}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if PORT not set
    app.run(host='0.0.0.0', port=port, debug=True)
