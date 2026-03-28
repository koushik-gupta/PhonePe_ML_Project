# PhonePe Transaction Insights

This project analyzes PhonePe Pulse data to understand transaction behavior, user engagement, insurance adoption, and top-performing geographic entities across India. The workflow follows a complete pipeline from JSON extraction to SQL-backed analysis and an interactive Streamlit dashboard.

## Project Links

- GitHub Repository: https://github.com/koushik-gupta/PhonePe_ML_Project
- Live Streamlit App: https://phonepe-analytics-dashboard.streamlit.app/

## Project Workflow

1. Extract nested PhonePe Pulse JSON files with Python.
2. Flatten the raw data into clean analytical tables.
3. Store the cleaned tables in SQLite.
4. Perform business analysis with SQL queries.
5. Build an interactive Streamlit app on top of the SQLite database.

## Main Files

- `Phone_Pay_EDA_Analysis.ipynb`: end-to-end notebook with extraction, EDA, chart insights, SQL section, and Streamlit stage documentation.
- `phonepe_insights.db`: SQLite database created from the cleaned CSV tables.
- `app.py`: Streamlit dashboard connected to the SQLite database.
- `business_queries.sql`: reusable SQL queries for major business questions.
- `requirements.txt`: Python dependencies required to run the dashboard.
- `*.csv`: cleaned analytical tables generated from the PhonePe Pulse JSON source and used in the SQL loading stage.

## Dashboard Features

- Filter by year, quarter, and state
- Overview metrics for transaction value, transaction count, registered users, and app opens
- Transaction category analysis and period trend analysis
- Interactive India state maps for transactions, user engagement, and insurance activity with hover tooltips and click-based drill-down
- Geography page with top states, top districts, top pincodes, and focused state drill-down panels
- Insurance adoption and yearly insurance growth analysis
- Top-performer views for transactions, users, and insurance

## How To Run

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## GitHub Repository Notes

- The cleaned CSV files and the SQLite database are intentionally included in the repository because they are small and make the SQL stage and Streamlit app runnable immediately.
- Local-only folders such as `.venv/`, `pulse/`, and `pulse-master/` should not be pushed to GitHub.
- The notebook already contains a safe clone step for the raw PhonePe Pulse repository and will clone `pulse/` only if that folder is missing.
- The CSV-generation cells in the notebook are kept on purpose because they demonstrate the JSON extraction and transformation stage required by the project.

## Data Tables Used

- `aggregated_transaction_country`
- `aggregated_transaction_state`
- `aggregated_user_country`
- `aggregated_user_state`
- `aggregated_insurance_country`
- `aggregated_insurance_state`
- `map_transaction_hover`
- `map_user_hover`
- `map_insurance_hover`
- `top_transaction`
- `top_user`
- `top_insurance`

## Business Outcome

The final output helps identify:

- high-value transaction categories
- leading states, districts, and pincodes
- regions with strong user adoption
- insurance growth opportunities
- geography-driven business expansion patterns
