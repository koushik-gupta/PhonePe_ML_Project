from pathlib import Path
import sqlite3

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(
    page_title="PhonePe Transaction Insights",
    page_icon="PH",
    layout="wide",
)

DB_PATH = Path(__file__).resolve().parent / "phonepe_insights.db"

STATE_COORDINATES = {
    "Andaman & Nicobar Islands": {"lat": 11.7401, "lon": 92.6586},
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.74},
    "Arunachal Pradesh": {"lat": 28.218, "lon": 94.7278},
    "Assam": {"lat": 26.2006, "lon": 92.9376},
    "Bihar": {"lat": 25.0961, "lon": 85.3131},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
    "Dadra & Nagar Haveli & Daman & Diu": {"lat": 20.2731, "lon": 73.0087},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Goa": {"lat": 15.2993, "lon": 74.124},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924},
    "Haryana": {"lat": 29.0588, "lon": 76.0856},
    "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
    "Jammu & Kashmir": {"lat": 33.7782, "lon": 76.5762},
    "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139},
    "Kerala": {"lat": 10.8505, "lon": 76.2711},
    "Ladakh": {"lat": 34.2268, "lon": 77.5619},
    "Lakshadweep": {"lat": 10.5667, "lon": 72.6417},
    "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
    "Manipur": {"lat": 24.6637, "lon": 93.9063},
    "Meghalaya": {"lat": 25.467, "lon": 91.3662},
    "Mizoram": {"lat": 23.1645, "lon": 92.9376},
    "Nagaland": {"lat": 26.1584, "lon": 94.5624},
    "Odisha": {"lat": 20.9517, "lon": 85.0985},
    "Puducherry": {"lat": 11.9416, "lon": 79.8083},
    "Punjab": {"lat": 31.1471, "lon": 75.3412},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
    "Sikkim": {"lat": 27.533, "lon": 88.5122},
    "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
    "Telangana": {"lat": 18.1124, "lon": 79.0193},
    "Tripura": {"lat": 23.9408, "lon": 91.9882},
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
    "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
    "West Bengal": {"lat": 22.9868, "lon": 87.855},
}


@st.cache_data(show_spinner=False)
def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


@st.cache_data(show_spinner=False)
def get_year_options() -> list[int]:
    df = run_query(
        "SELECT DISTINCT Year FROM aggregated_transaction_country ORDER BY Year"
    )
    return df["Year"].astype(int).tolist()


@st.cache_data(show_spinner=False)
def get_quarter_options(selected_year):
    if selected_year == "All":
        return [1, 2, 3, 4]

    df = run_query(
        "SELECT DISTINCT Quarter FROM aggregated_transaction_country WHERE Year = ? ORDER BY Quarter",
        (int(selected_year),),
    )
    return df["Quarter"].astype(int).tolist()


@st.cache_data(show_spinner=False)
def get_state_options() -> list[str]:
    df = run_query(
        "SELECT DISTINCT State FROM aggregated_transaction_state ORDER BY State"
    )
    return df["State"].tolist()


def build_filters(year="All", quarter="All", state="All", include_state=True):
    clauses = []
    params = []

    if year != "All":
        clauses.append("Year = ?")
        params.append(int(year))
    if quarter != "All":
        clauses.append("Quarter = ?")
        params.append(int(quarter))
    if include_state and state != "All":
        clauses.append("State = ?")
        params.append(state)

    return clauses, tuple(params)


def build_where(clauses):
    return f" WHERE {' AND '.join(clauses)}" if clauses else ""


def fmt_trillion(value) -> str:
    value = 0 if pd.isna(value) else value
    return f"{value:,.2f} T"


def fmt_billion(value) -> str:
    value = 0 if pd.isna(value) else value
    return f"{value:,.2f} B"


def fmt_crore(value) -> str:
    value = 0 if pd.isna(value) else value
    return f"{value:,.2f} Cr"


def fmt_int(value) -> str:
    value = 0 if pd.isna(value) else int(value)
    return f"{value:,}"


DISPLAY_COLUMN_NAMES = {
    "App_Opens": "App Opens",
    "Entity_Name": "Entity",
    "insurance_amount_crore": "Insurance Amount (Cr)",
    "insurance_transactions": "Insurance Transactions",
    "period": "Period",
    "Quarter": "Quarter",
    "Registered_Users": "Registered Users",
    "State": "State",
    "total_registered_users": "Registered Users",
    "total_transaction_amount_billion": "Transaction Amount (B)",
    "total_transaction_amount_crore": "Transaction Amount (Cr)",
    "total_transaction_count": "Transaction Count",
    "Transaction_Type": "Transaction Type",
    "transaction_amount_trillion": "Transaction Amount (T)",
    "transaction_count": "Transaction Count",
    "transaction_count_billion": "Transaction Count (B)",
    "Year": "Year",
}


def show_table(df: pd.DataFrame):
    display_df = df.rename(
        columns={column: DISPLAY_COLUMN_NAMES.get(column, column) for column in df.columns}
    )
    st.dataframe(display_df, width="stretch", hide_index=True)


def format_selection(selected_year, selected_quarter, selected_state):
    year_label = "All years" if selected_year == "All" else f"Year {selected_year}"
    quarter_label = (
        "All quarters" if selected_quarter == "All" else f"Quarter {selected_quarter}"
    )
    state_label = "All states" if selected_state == "All" else selected_state
    return f"{year_label} | {quarter_label} | {state_label}"


def with_state_coordinates(df: pd.DataFrame, size_column: str) -> pd.DataFrame:
    coords = pd.DataFrame(
        [
            {"State": state, "lat": value["lat"], "lon": value["lon"]}
            for state, value in STATE_COORDINATES.items()
        ]
    )
    enriched = df.merge(coords, on="State", how="left")
    values = pd.to_numeric(enriched.get(size_column), errors="coerce").fillna(0)
    if not values.empty and values.max() > 0:
        enriched["marker_size"] = ((values / values.max()).pow(0.5) * 45) + 6
    else:
        enriched["marker_size"] = 8
    return enriched.dropna(subset=["lat", "lon"])


def get_selected_state_from_event(event, layer_id: str):
    if not event:
        return None

    selection = event.get("selection", {})
    objects = selection.get("objects", {})
    selected_objects = objects.get(layer_id, [])
    if not selected_objects:
        return None

    return selected_objects[0].get("State")


def render_state_map(
    map_df: pd.DataFrame,
    *,
    layer_id: str,
    color,
    caption: str,
    tooltip_html: str,
    key: str,
    zoom: int = 4,
):
    if map_df.empty:
        st.info("No map data available for the current selection.")
        return None

    st.caption(caption)
    st.caption(
        "Hover over a bubble for quick metrics and click it to open a focused state detail view below."
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        id=layer_id,
        pickable=True,
        opacity=0.78,
        stroked=True,
        filled=True,
        radius_scale=700,
        radius_min_pixels=4,
        radius_max_pixels=18,
        line_width_min_pixels=1,
        get_position="[lon, lat]",
        get_radius="marker_size",
        get_fill_color=color,
        get_line_color=[15, 23, 42, 220],
    )
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=22.9734,
            longitude=78.6569,
            zoom=zoom,
            pitch=0,
        ),
        map_style=None,
        tooltip={
            "html": tooltip_html,
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#f8fafc",
                "fontSize": "13px",
            },
        },
    )
    event = st.pydeck_chart(
        deck,
        width="stretch",
        height=500,
        on_select="rerun",
        selection_mode="single-object",
        key=key,
    )
    return get_selected_state_from_event(event, layer_id)


def get_transaction_metrics(selected_year, selected_quarter, selected_state):
    if selected_state == "All":
        table_name = "aggregated_transaction_country"
        clauses, params = build_filters(selected_year, selected_quarter, include_state=False)
    else:
        table_name = "aggregated_transaction_state"
        clauses, params = build_filters(selected_year, selected_quarter, selected_state)

    query = f"""
        SELECT
            COALESCE(SUM(Transaction_Count) / 1000000000.0, 0) AS transaction_count_billion,
            COALESCE(SUM(Transaction_Amount) / 1000000000000.0, 0) AS transaction_amount_trillion
        FROM {table_name}{build_where(clauses)}
    """
    return run_query(query, params).iloc[0]


def get_user_snapshot(selected_year, selected_quarter, selected_state):
    if selected_state == "All":
        table_name = "aggregated_user_country"
        clauses, params = build_filters(selected_year, selected_quarter, include_state=False)
    else:
        table_name = "aggregated_user_state"
        clauses, params = build_filters(selected_year, selected_quarter, selected_state)

    query = f"""
        SELECT
            Year,
            Quarter,
            Registered_Users,
            App_Opens
        FROM {table_name}{build_where(clauses)}
        ORDER BY Year DESC, Quarter DESC
        LIMIT 1
    """
    snapshot = run_query(query, params)
    if snapshot.empty:
        return pd.Series({
            "Year": None,
            "Quarter": None,
            "Registered_Users": 0,
            "App_Opens": 0,
        })
    return snapshot.iloc[0]


def get_yearly_trend(selected_state):
    if selected_state == "All":
        query = """
            SELECT
                Year,
                ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
            FROM aggregated_transaction_country
            GROUP BY Year
            ORDER BY Year
        """
        return run_query(query)

    return run_query(
        """
        SELECT
            Year,
            ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
        FROM aggregated_transaction_state
        WHERE State = ?
        GROUP BY Year
        ORDER BY Year
        """,
        (selected_state,),
    )


def get_transaction_type_summary(selected_year, selected_quarter, selected_state):
    clauses, params = build_filters(selected_year, selected_quarter, selected_state)
    query = f"""
        SELECT
            Transaction_Type,
            ROUND(SUM(Transaction_Count) / 1000000000.0, 2) AS transaction_count_billion,
            ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
        FROM aggregated_transaction_state{build_where(clauses)}
        GROUP BY Transaction_Type
        ORDER BY transaction_amount_trillion DESC
    """
    return run_query(query, params)


def get_transaction_period_trend(selected_year, selected_quarter, selected_state):
    clauses, params = build_filters(selected_year, selected_quarter, selected_state)
    query = f"""
        SELECT
            printf('%d-Q%d', Year, Quarter) AS period,
            ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
        FROM aggregated_transaction_state{build_where(clauses)}
        GROUP BY Year, Quarter
        ORDER BY Year, Quarter
    """
    return run_query(query, params)


def get_top_states(selected_year, selected_quarter):
    clauses, params = build_filters(selected_year, selected_quarter, include_state=False)
    query = f"""
        SELECT
            State,
            ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion,
            ROUND(SUM(Transaction_Count) / 1000000000.0, 2) AS transaction_count_billion
        FROM aggregated_transaction_state{build_where(clauses)}
        GROUP BY State
        ORDER BY transaction_amount_trillion DESC
        LIMIT 15
    """
    return run_query(query, params)


def get_transaction_state_footprint(selected_year, selected_quarter):
    clauses, params = build_filters(selected_year, selected_quarter, include_state=False)
    query = f"""
        SELECT
            State,
            SUM(Transaction_Count) AS transaction_count,
            ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
        FROM map_transaction_hover{build_where(clauses)}
        GROUP BY State
        ORDER BY transaction_amount_trillion DESC
    """
    df = with_state_coordinates(run_query(query, params), "transaction_amount_trillion")
    if not df.empty:
        df["transaction_amount_label"] = df["transaction_amount_trillion"].map(fmt_trillion)
        df["transaction_count_label"] = df["transaction_count"].map(fmt_int)
    return df


def get_selected_state_trend(selected_state):
    if selected_state == "All":
        return pd.DataFrame()

    return run_query(
        """
        SELECT
            printf('%d-Q%d', Year, Quarter) AS period,
            ROUND(SUM(Transaction_Amount) / 1000000000000.0, 2) AS transaction_amount_trillion
        FROM aggregated_transaction_state
        WHERE State = ?
        GROUP BY Year, Quarter
        ORDER BY Year, Quarter
        """,
        (selected_state,),
    )


def get_user_state_trend(selected_state):
    if selected_state == "All":
        return pd.DataFrame()

    return run_query(
        """
        SELECT
            printf('%d-Q%d', Year, Quarter) AS period,
            Registered_Users,
            App_Opens
        FROM aggregated_user_state
        WHERE State = ?
        ORDER BY Year, Quarter
        """,
        (selected_state,),
    )


def get_user_state_snapshot(selected_year, selected_quarter):
    if selected_year == "All" and selected_quarter == "All":
        query = """
            SELECT
                State,
                Year,
                Quarter,
                Registered_Users,
                App_Opens
            FROM vw_latest_user_state_snapshot
            ORDER BY Registered_Users DESC
        """
        return run_query(query)

    if selected_year == "All" and selected_quarter != "All":
        query = """
            WITH latest AS (
                SELECT MAX(Year) AS Year
                FROM aggregated_user_state
                WHERE Quarter = ?
            )
            SELECT
                a.State,
                a.Year,
                a.Quarter,
                a.Registered_Users,
                a.App_Opens
            FROM aggregated_user_state AS a
            JOIN latest AS l
                ON a.Year = l.Year
            WHERE a.Quarter = ?
            ORDER BY a.Registered_Users DESC
        """
        return run_query(query, (int(selected_quarter), int(selected_quarter)))

    if selected_year != "All" and selected_quarter == "All":
        query = """
            WITH latest AS (
                SELECT Year, MAX(Quarter) AS Quarter
                FROM aggregated_user_state
                WHERE Year = ?
            )
            SELECT
                a.State,
                a.Year,
                a.Quarter,
                a.Registered_Users,
                a.App_Opens
            FROM aggregated_user_state AS a
            JOIN latest AS l
                ON a.Year = l.Year AND a.Quarter = l.Quarter
            ORDER BY a.Registered_Users DESC
        """
        return run_query(query, (int(selected_year),))

    query = """
        SELECT
            State,
            Year,
            Quarter,
            Registered_Users,
            App_Opens
        FROM aggregated_user_state
        WHERE Year = ? AND Quarter = ?
        ORDER BY Registered_Users DESC
    """
    return run_query(query, (int(selected_year), int(selected_quarter)))


def get_insurance_state_summary(selected_year, selected_quarter):
    clauses, params = build_filters(selected_year, selected_quarter, include_state=False)
    query = f"""
        SELECT
            State,
            SUM(Transaction_Count) AS insurance_transactions,
            ROUND(SUM(Transaction_Amount) / 10000000.0, 2) AS insurance_amount_crore
        FROM aggregated_insurance_state{build_where(clauses)}
        GROUP BY State
        ORDER BY insurance_amount_crore DESC
    """
    return run_query(query, params)


def get_insurance_yearly_trend():
    query = """
        SELECT
            Year,
            ROUND(SUM(Transaction_Amount) / 10000000.0, 2) AS insurance_amount_crore
        FROM aggregated_insurance_country
        GROUP BY Year
        ORDER BY Year
    """
    return run_query(query)


def get_insurance_state_map(selected_year, selected_quarter):
    clauses, params = build_filters(selected_year, selected_quarter, include_state=False)
    query = f"""
        SELECT
            State,
            SUM(Transaction_Count) AS insurance_transactions,
            ROUND(SUM(Transaction_Amount) / 10000000.0, 2) AS insurance_amount_crore
        FROM map_insurance_hover{build_where(clauses)}
        GROUP BY State
        ORDER BY insurance_amount_crore DESC
    """
    df = with_state_coordinates(run_query(query, params), "insurance_amount_crore")
    if not df.empty:
        df["insurance_amount_label"] = df["insurance_amount_crore"].map(fmt_crore)
        df["insurance_transactions_label"] = df["insurance_transactions"].map(fmt_int)
    return df


def get_insurance_state_trend(selected_state):
    if selected_state == "All":
        return pd.DataFrame()

    return run_query(
        """
        SELECT
            printf('%d-Q%d', Year, Quarter) AS period,
            SUM(Transaction_Count) AS insurance_transactions,
            ROUND(SUM(Transaction_Amount) / 10000000.0, 2) AS insurance_amount_crore
        FROM aggregated_insurance_state
        WHERE State = ?
        GROUP BY Year, Quarter
        ORDER BY Year, Quarter
        """,
        (selected_state,),
    )


def get_top_transaction_entities(entity_type, selected_year, selected_quarter):
    clauses = ["Type = ?"]
    params = [entity_type]
    if selected_year != "All":
        clauses.append("Year = ?")
        params.append(int(selected_year))
    if selected_quarter != "All":
        clauses.append("Quarter = ?")
        params.append(int(selected_quarter))

    query = f"""
        SELECT
            Entity_Name,
            SUM(Transaction_Count) AS total_transaction_count,
            ROUND(SUM(Transaction_Amount) / 1000000000.0, 2) AS total_transaction_amount_billion
        FROM top_transaction{build_where(clauses)}
        GROUP BY Entity_Name
        ORDER BY total_transaction_amount_billion DESC
        LIMIT 10
    """
    return run_query(query, tuple(params))


def get_top_user_entities(entity_type, selected_year, selected_quarter):
    clauses = ["Type = ?"]
    params = [entity_type]
    if selected_year != "All":
        clauses.append("Year = ?")
        params.append(int(selected_year))
    if selected_quarter != "All":
        clauses.append("Quarter = ?")
        params.append(int(selected_quarter))

    query = f"""
        SELECT
            Entity_Name,
            SUM(Registered_Users) AS total_registered_users
        FROM top_user{build_where(clauses)}
        GROUP BY Entity_Name
        ORDER BY total_registered_users DESC
        LIMIT 10
    """
    return run_query(query, tuple(params))


def get_top_insurance_entities(entity_type, selected_year, selected_quarter):
    clauses = ["Type = ?"]
    params = [entity_type]
    if selected_year != "All":
        clauses.append("Year = ?")
        params.append(int(selected_year))
    if selected_quarter != "All":
        clauses.append("Quarter = ?")
        params.append(int(selected_quarter))

    query = f"""
        SELECT
            Entity_Name,
            SUM(Transaction_Count) AS total_transaction_count,
            ROUND(SUM(Transaction_Amount) / 10000000.0, 2) AS total_transaction_amount_crore
        FROM top_insurance{build_where(clauses)}
        GROUP BY Entity_Name
        ORDER BY total_transaction_amount_crore DESC
        LIMIT 10
    """
    return run_query(query, tuple(params))


if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

st.title("PhonePe Transaction Insights Dashboard")
st.caption(
    "Interactive Streamlit dashboard powered by the SQLite database generated from the cleaned PhonePe project tables."
)

with st.sidebar:
    st.header("Dashboard Filters")
    selected_year = st.selectbox("Select Year", ["All"] + get_year_options())
    selected_quarter = st.selectbox(
        "Select Quarter", ["All"] + get_quarter_options(selected_year)
    )
    selected_state = st.selectbox("Select State", ["All"] + get_state_options())
    page = st.radio(
        "Choose Dashboard Section",
        [
            "Overview",
            "Transactions",
            "Geography",
            "Users",
            "Insurance",
            "Top Performers",
        ],
    )
    st.caption(f"Database file: {DB_PATH.name}")

st.caption(
    f"Current filter selection: {format_selection(selected_year, selected_quarter, selected_state)}"
)

if page == "Overview":
    st.subheader("Overview Metrics")
    txn_metrics = get_transaction_metrics(selected_year, selected_quarter, selected_state)
    user_snapshot = get_user_snapshot(selected_year, selected_quarter, selected_state)

    metric_cols = st.columns(4)
    metric_cols[0].metric(
        "Transaction Amount", fmt_trillion(txn_metrics["transaction_amount_trillion"])
    )
    metric_cols[1].metric(
        "Transaction Count", fmt_billion(txn_metrics["transaction_count_billion"])
    )
    metric_cols[2].metric(
        "Registered Users Snapshot", fmt_int(user_snapshot["Registered_Users"])
    )
    metric_cols[3].metric("App Opens Snapshot", fmt_int(user_snapshot["App_Opens"]))

    st.subheader("Yearly Transaction Growth")
    yearly_trend = get_yearly_trend(selected_state)
    if yearly_trend.empty:
        st.info("No yearly trend data available for the current selection.")
    else:
        st.line_chart(
            yearly_trend.set_index("Year")["transaction_amount_trillion"],
            width="stretch",
        )
        show_table(yearly_trend)

elif page == "Transactions":
    st.subheader("Payment Category Performance")
    type_summary = get_transaction_type_summary(
        selected_year, selected_quarter, selected_state
    )
    if type_summary.empty:
        st.info("No transaction category data available for the current selection.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Transaction Amount by Type")
            st.bar_chart(
                type_summary.set_index("Transaction_Type")["transaction_amount_trillion"],
                width="stretch",
            )
        with col2:
            st.markdown("#### Transaction Count by Type")
            st.bar_chart(
                type_summary.set_index("Transaction_Type")["transaction_count_billion"],
                width="stretch",
            )
        show_table(type_summary)

    st.subheader("Transaction Trend by Period")
    period_trend = get_transaction_period_trend(
        selected_year, selected_quarter, selected_state
    )
    if period_trend.empty:
        st.info("No time-trend data available for the current selection.")
    else:
        st.line_chart(
            period_trend.set_index("period")["transaction_amount_trillion"],
            width="stretch",
        )
        show_table(period_trend)

elif page == "Geography":
    st.subheader("Transaction Footprint Across India")
    transaction_map = get_transaction_state_footprint(selected_year, selected_quarter)
    top_states = get_top_states(selected_year, selected_quarter)
    clicked_state = None
    if transaction_map.empty:
        st.info("No state-level transaction data available for the current selection.")
    else:
        clicked_state = render_state_map(
            transaction_map,
            layer_id="transaction-footprint-layer",
            color=[15, 118, 110, 190],
            caption="Bubble size reflects total transaction value for each state in the current year and quarter selection.",
            tooltip_html="<b>{State}</b><br/>Transaction Value: {transaction_amount_label}<br/>Transactions: {transaction_count_label}",
            key="transaction-footprint-map",
        )
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("#### Top States by Transaction Value")
            st.bar_chart(
                top_states.set_index("State")["transaction_amount_trillion"],
                width="stretch",
            )
        with col2:
            leader = top_states.iloc[0]
            st.markdown("#### Leading State Snapshot")
            st.metric("State Leader", leader["State"], border=True)
            st.metric(
                "Transaction Value",
                fmt_trillion(leader["transaction_amount_trillion"]),
                border=True,
            )
            st.metric(
                "Transaction Volume",
                fmt_billion(leader["transaction_count_billion"]),
            )
        show_table(top_states)

    focused_state = selected_state if selected_state != "All" else clicked_state
    if focused_state:
        focused_row = transaction_map[transaction_map["State"] == focused_state]
        if not focused_row.empty:
            focused_row = focused_row.iloc[0]
            total_amount = transaction_map["transaction_amount_trillion"].sum()
            state_share = (
                (focused_row["transaction_amount_trillion"] / total_amount) * 100
                if total_amount
                else 0
            )
            st.subheader(f"{focused_state} Drill-down")
            metric_cols = st.columns(3)
            metric_cols[0].metric(
                "Current Transaction Value",
                fmt_trillion(focused_row["transaction_amount_trillion"]),
            )
            metric_cols[1].metric(
                "Current Transaction Volume",
                fmt_int(focused_row["transaction_count"]),
            )
            metric_cols[2].metric("Share of Visible Value", f"{state_share:.1f}%")

            state_trend = get_selected_state_trend(focused_state)
            state_type_mix = get_transaction_type_summary(
                selected_year, selected_quarter, focused_state
            )
            detail_left, detail_right = st.columns(2)
            with detail_left:
                st.markdown("#### Transaction Trend Over Time")
                if state_trend.empty:
                    st.info("No state trend data available for the focused state.")
                else:
                    st.line_chart(
                        state_trend.set_index("period")["transaction_amount_trillion"],
                        width="stretch",
                    )
                    show_table(state_trend)
            with detail_right:
                st.markdown("#### Payment Mix in Current Selection")
                if state_type_mix.empty:
                    st.info("No payment mix data available for the focused state.")
                else:
                    st.bar_chart(
                        state_type_mix.set_index("Transaction_Type")[
                            "transaction_amount_trillion"
                        ],
                        width="stretch",
                    )
                    show_table(state_type_mix)

    st.subheader("District and Pincode Leaders")
    district_col, pincode_col = st.columns(2)
    district_leaders = get_top_transaction_entities("District", selected_year, selected_quarter)
    pincode_leaders = get_top_transaction_entities("Pincode", selected_year, selected_quarter)
    with district_col:
        st.markdown("#### Top Districts")
        if district_leaders.empty:
            st.info("No district-level leaders available for the current selection.")
        else:
            st.bar_chart(
                district_leaders.set_index("Entity_Name")[
                    "total_transaction_amount_billion"
                ],
                width="stretch",
            )
            show_table(district_leaders)
    with pincode_col:
        st.markdown("#### Top Pincodes")
        if pincode_leaders.empty:
            st.info("No pincode-level leaders available for the current selection.")
        else:
            st.bar_chart(
                pincode_leaders.set_index("Entity_Name")[
                    "total_transaction_amount_billion"
                ],
                width="stretch",
            )
            show_table(pincode_leaders)

elif page == "Users":
    st.subheader("State-wise User Engagement Snapshot")
    user_snapshot = get_user_state_snapshot(selected_year, selected_quarter)
    if selected_state != "All":
        user_snapshot = user_snapshot[user_snapshot["State"] == selected_state]

    clicked_state = None
    if user_snapshot.empty:
        st.info("No user engagement data available for the current selection.")
    else:
        user_map = with_state_coordinates(user_snapshot.copy(), "Registered_Users")
        user_map["registered_users_label"] = user_map["Registered_Users"].map(fmt_int)
        user_map["app_opens_label"] = user_map["App_Opens"].map(fmt_int)
        user_map["snapshot_label"] = user_map.apply(
            lambda row: f"{int(row['Year'])} Q{int(row['Quarter'])}", axis=1
        )

        clicked_state = render_state_map(
            user_map,
            layer_id="user-engagement-layer",
            color=[37, 99, 235, 190],
            caption="Bubble size reflects the registered user base in the selected user snapshot.",
            tooltip_html="<b>{State}</b><br/>Registered Users: {registered_users_label}<br/>App Opens: {app_opens_label}<br/>Snapshot: {snapshot_label}",
            key="user-engagement-map",
        )
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Registered Users by State")
            st.bar_chart(
                user_snapshot.set_index("State")["Registered_Users"],
                width="stretch",
            )
        with col2:
            st.markdown("#### App Opens by State")
            st.bar_chart(
                user_snapshot.set_index("State")["App_Opens"],
                width="stretch",
            )
        show_table(user_snapshot)

    focused_state = selected_state if selected_state != "All" else clicked_state
    if focused_state:
        focused_row = user_snapshot[user_snapshot["State"] == focused_state]
        if not focused_row.empty:
            focused_row = focused_row.iloc[0]
            user_trend = get_user_state_trend(focused_state)
            opens_per_user = (
                focused_row["App_Opens"] / focused_row["Registered_Users"]
                if focused_row["Registered_Users"]
                else 0
            )
            st.subheader(f"{focused_state} User Detail")
            metric_cols = st.columns(4)
            metric_cols[0].metric(
                "Snapshot Period",
                f"{int(focused_row['Year'])} Q{int(focused_row['Quarter'])}",
            )
            metric_cols[1].metric(
                "Registered Users", fmt_int(focused_row["Registered_Users"])
            )
            metric_cols[2].metric("App Opens", fmt_int(focused_row["App_Opens"]))
            metric_cols[3].metric("App Opens per User", f"{opens_per_user:.1f}")

            if user_trend.empty:
                st.info("No user trend data available for the focused state.")
            else:
                trend_left, trend_right = st.columns(2)
                with trend_left:
                    st.markdown("#### Registered User Trend")
                    st.line_chart(
                        user_trend.set_index("period")["Registered_Users"],
                        width="stretch",
                    )
                with trend_right:
                    st.markdown("#### App Open Trend")
                    st.line_chart(
                        user_trend.set_index("period")["App_Opens"],
                        width="stretch",
                    )
                show_table(user_trend)

elif page == "Insurance":
    st.subheader("Insurance Adoption by State")
    insurance_summary = get_insurance_state_summary(selected_year, selected_quarter)
    insurance_map = get_insurance_state_map(selected_year, selected_quarter)
    if selected_state != "All":
        insurance_summary = insurance_summary[insurance_summary["State"] == selected_state]
        insurance_map = insurance_map[insurance_map["State"] == selected_state]

    clicked_state = None
    if insurance_summary.empty:
        st.info("No insurance data available for the current selection.")
    else:
        clicked_state = render_state_map(
            insurance_map,
            layer_id="insurance-activity-layer",
            color=[180, 83, 9, 190],
            caption="Bubble size reflects insurance transaction value across states for the selected period.",
            tooltip_html="<b>{State}</b><br/>Insurance Value: {insurance_amount_label}<br/>Transactions: {insurance_transactions_label}",
            key="insurance-activity-map",
        )
        st.bar_chart(
            insurance_summary.set_index("State")["insurance_amount_crore"],
            width="stretch",
        )
        show_table(insurance_summary)

    focused_state = selected_state if selected_state != "All" else clicked_state
    if focused_state:
        focused_row = insurance_map[insurance_map["State"] == focused_state]
        if not focused_row.empty:
            focused_row = focused_row.iloc[0]
            total_amount = insurance_map["insurance_amount_crore"].sum()
            state_share = (
                (focused_row["insurance_amount_crore"] / total_amount) * 100
                if total_amount
                else 0
            )
            insurance_state_trend = get_insurance_state_trend(focused_state)
            st.subheader(f"{focused_state} Insurance Detail")
            metric_cols = st.columns(3)
            metric_cols[0].metric(
                "Current Insurance Value",
                fmt_crore(focused_row["insurance_amount_crore"]),
            )
            metric_cols[1].metric(
                "Current Insurance Transactions",
                fmt_int(focused_row["insurance_transactions"]),
            )
            metric_cols[2].metric("Share of Visible Value", f"{state_share:.1f}%")

            if insurance_state_trend.empty:
                st.info("No insurance trend data available for the focused state.")
            else:
                trend_left, trend_right = st.columns(2)
                with trend_left:
                    st.markdown("#### Insurance Value Trend")
                    st.line_chart(
                        insurance_state_trend.set_index("period")[
                            "insurance_amount_crore"
                        ],
                        width="stretch",
                    )
                with trend_right:
                    st.markdown("#### Insurance Transaction Trend")
                    st.line_chart(
                        insurance_state_trend.set_index("period")[
                            "insurance_transactions"
                        ],
                        width="stretch",
                    )
                show_table(insurance_state_trend)

    st.subheader("Insurance Growth Trend")
    insurance_trend = get_insurance_yearly_trend()
    st.line_chart(
        insurance_trend.set_index("Year")["insurance_amount_crore"],
        width="stretch",
    )
    show_table(insurance_trend)

elif page == "Top Performers":
    st.subheader("Top Performing States, Districts, and Pincodes")
    entity_type = st.selectbox("Choose Entity Type", ["State", "District", "Pincode"])

    transaction_entities = get_top_transaction_entities(
        entity_type, selected_year, selected_quarter
    )
    user_entities = get_top_user_entities(entity_type, selected_year, selected_quarter)
    insurance_entities = get_top_insurance_entities(
        entity_type, selected_year, selected_quarter
    )

    txn_tab, user_tab, insurance_tab = st.tabs(
        ["Transactions", "Users", "Insurance"]
    )

    with txn_tab:
        st.markdown("#### Top Transaction Entities")
        if transaction_entities.empty:
            st.info("No transaction leaders available for the current selection.")
        else:
            show_table(transaction_entities)

    with user_tab:
        st.markdown("#### Top User Entities")
        if user_entities.empty:
            st.info("No user leaders available for the current selection.")
        else:
            show_table(user_entities)

    with insurance_tab:
        st.markdown("#### Top Insurance Entities")
        if insurance_entities.empty:
            st.info("No insurance leaders available for the current selection.")
        else:
            show_table(insurance_entities)
