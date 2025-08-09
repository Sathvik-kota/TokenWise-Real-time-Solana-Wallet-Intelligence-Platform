import os
import joblib
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import psycopg2
from datetime import datetime, time
from zoneinfo import ZoneInfo
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Set page config
st.set_page_config(page_title="TokenWise", layout="wide")

# ----------------- SESSION STATE -----------------
if "started" not in st.session_state:
    st.session_state["started"] = False

# ----------------- LOTTIE ANIMATION -----------------
def load_lottie(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

lottie_json = load_lottie("https://lottie.host/fb0587c8-fbd2-43ce-b3f5-7cb49c5bdb21/HTbrRQkfpY.json")

# ----------------- LANDING PAGE -----------------
if not st.session_state["started"]:
    st.markdown("""
        <style>
        html, body { overflow: hidden; }
        .main {
            background: linear-gradient(135deg, #1e1e2f, #151520);
            color: white;
            height: 100vh;
            padding: 3rem 2rem 1rem;
        }
        .top-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            height: 100%;
            text-align: center;
        }
        .title {
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(to right, #00FFA3, #DC1FFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            font-size: 1.6rem;
            color: #ccc;
            margin-bottom: 0.5rem;
        }
        .description {
            font-size: 1.1rem;
            color: #aaa;
            max-width: 750px;
            margin-bottom: 2rem;
        }
        .stButton > button {
            font-size: 1rem;
            padding: 0.75rem 2rem;
            border-radius: 10px;
            background: linear-gradient(90deg, #00FFA3, #DC1FFF);
            color: white;
            border: none;
            transition: 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #DC1FFF, #00FFA3);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="top-container">', unsafe_allow_html=True)
    st.markdown('<div class="title">🚀 TokenWise</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Real-Time Wallet Intelligence on Solana</div>', unsafe_allow_html=True)
    st.markdown('<div class="description">Gain deep insights into top wallets, protocol flow, and token movements with live data from the Solana blockchain.</div>', unsafe_allow_html=True)

    if lottie_json:
        st_lottie(lottie_json, height=250, key="rocket")

    if st.button("Enter Dashboard"):
        st.session_state["started"] = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- DASHBOARD PAGE -----------------
if st.session_state["started"]:

    AUTO_REFRESH_SEC = 660
    st.markdown(f'<meta http-equiv="refresh" content="{AUTO_REFRESH_SEC}">', unsafe_allow_html=True)

    st.markdown("""
        <style>
        .block-container { padding-top: 1rem !important; }
        h2 { margin-top: 0rem !important; }
        .stAlert { margin-top: 0rem !important; margin-bottom: 0.5rem !important; }
        </style>
    """, unsafe_allow_html=True)

    @st.cache_resource
    def get_connection():
        return psycopg2.connect(
            host="localhost",
            dbname="transactions",
            user="postgres",
            password="25@Sathvik",
            port=5432
        )

    @st.cache_data(ttl=10)
    def load_data():
        conn = get_connection()
        query = """
            SELECT timestamp, wallet, amount, direction, protocol, mint
            FROM transactions
            ORDER BY timestamp DESC
        """
        df = pd.read_sql(query, conn)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df["timestamp"] = df["timestamp"].dt.tz_convert(ZoneInfo("Asia/Kolkata"))
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()
        df["direction"] = df["direction"].astype(str).str.upper().str.strip()
        df["signed_amount"] = df.apply(lambda r: r["amount"] if r["direction"] == "BUY" else -r["amount"], axis=1)
        return df

    df = load_data()

    total_buys = df[df["direction"] == "BUY"]["amount"].sum()
    total_sells = df[df["direction"] == "SELL"]["amount"].sum()
    net = total_buys - total_sells

    text_color = "#0f0" if total_buys > total_sells else "#f33" if total_sells > total_buys else "#000"
    banner_msg = "✅ More buying than selling activity" if total_buys > total_sells else \
                 "⚠️ More selling than buying activity" if total_sells > total_buys else \
                 "➖ Equal buying and selling activity"

    st.title("📊 TokenWise Dashboard")
    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        color: {text_color};
        padding: 10px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 8px;
        overflow: hidden;
    ">
      <marquee behavior="scroll" direction="right" scrollamount="15">
        {banner_msg}
      </marquee>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.header("Filters")
    wallets = df["wallet"].unique().tolist()
    selected_wallet = st.sidebar.selectbox("Filter by Wallet", ["All"] + wallets)
    if selected_wallet != "All":
        df = df[df["wallet"] == selected_wallet]

    if not df.empty:
        min_date = df["timestamp"].dt.date.min()
        max_date = df["timestamp"].dt.date.max()
        start_date, end_date = st.sidebar.date_input("Date range", value=(min_date, max_date), format="YYYY-MM-DD")
        start_time = st.sidebar.time_input("Start time", value=time(0, 0))
        end_time = st.sidebar.time_input("End time", value=time(23, 59))
        start_dt = datetime.combine(start_date, start_time).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        end_dt = datetime.combine(end_date, end_time).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
        st.sidebar.markdown(f"**Total Transactions:** {len(df)}")

    top_wallet = df.groupby("wallet")["amount"].sum().nlargest(1).index[0]
    st.sidebar.markdown(f"**Most Active Wallet:** {top_wallet}")

    W_DIR = os.path.join("models", top_wallet)
    SCALER_FILE = os.path.join(W_DIR, "scaler.pkl")
    IF_FILE = os.path.join(W_DIR, "iso.pkl")
    TS_FILE = os.path.join(W_DIR, "last_ts.txt")
    os.makedirs(W_DIR, exist_ok=True)

    w_df = df[df["wallet"] == top_wallet].sort_values("timestamp")

    if not os.path.exists(SCALER_FILE):
        scaler = StandardScaler().fit(w_df[["amount"]])
        joblib.dump(scaler, SCALER_FILE)
        X = scaler.transform(w_df[["amount"]])
        iso = IsolationForest(contamination=0.05, random_state=42).fit(X)
        joblib.dump(iso, IF_FILE)
        with open(TS_FILE, "w") as f:
            f.write(w_df["timestamp"].iloc[-1].isoformat())
    else:
        scaler = joblib.load(SCALER_FILE)
        iso = joblib.load(IF_FILE)

    last_ts = pd.to_datetime(open(TS_FILE).read()) if os.path.exists(TS_FILE) else w_df["timestamp"].min()
    new_txn = w_df[w_df["timestamp"] > last_ts]

    anomalies = pd.DataFrame()
    if not new_txn.empty:
        X_new = scaler.transform(new_txn[["amount"]])
        preds = iso.predict(X_new)
        new_txn = new_txn.assign(anomaly=(preds == -1))
        anomalies = new_txn[new_txn["anomaly"]]
        with open(TS_FILE, "w") as f:
            f.write(w_df["timestamp"].iloc[-1].isoformat())

    st.subheader("Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Total Bought", f"{total_buys:,.2f}")
    c2.metric("🔴 Total Sold", f"{total_sells:,.2f}")
    c3.metric("⚖️ Net Direction", f"{net:,.2f}", delta=f"{net:,.2f}")

    tab_summary, tab_ai, tab_whale, tab_raw, tab_time_trend = st.tabs([
        "📊 Summary", "🤖 Wallet AI", "🐋 Whale Alerts", "📄 Raw Data", "📈 Transactions Over Time"
    ])

    with tab_summary:
        st.subheader("📊 Summary Visualizations")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**🟢 Buys vs 🔴 Sells (Volume)**")
            volume_df = df.copy()
            volume_df["abs_amount"] = volume_df["amount"].abs()
            buy_sell_volume = volume_df.groupby("direction")["abs_amount"].sum().reset_index()
            fig1 = px.bar(buy_sell_volume, x="direction", y="abs_amount", color="direction", height=300)
            fig1.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("**🔁 Protocol Usage Count**")
            protocol_count = df["protocol"].value_counts().reset_index()
            protocol_count.columns = ["Protocol", "Count"]
            fig2 = px.bar(protocol_count, x="Protocol", y="Count", color="Protocol", height=300)
            fig2.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**🏦 Top Active Wallets**")
        wallet_df = df.groupby("wallet")["amount"].sum().abs().sort_values(ascending=False).head(10).reset_index()
        fig3 = px.bar(wallet_df, x="wallet", y="amount", color="wallet", height=350)
        fig3.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    with tab_ai:
        st.subheader(f"🔍 Anomaly Detection for {top_wallet}")
        if anomalies.empty:
            st.success("No new anomalous transactions for this wallet.")
        else:
            st.error(f"{len(anomalies)} new anomalies!")
            st.dataframe(anomalies[["timestamp", "amount", "direction", "protocol"]], use_container_width=True)

        hist = w_df.assign(anomaly=iso.predict(scaler.transform(w_df[["amount"]])) == -1)
        fig = px.scatter(hist, x="timestamp", y="amount", color=hist["anomaly"].map({True: "Anomaly", False: "Normal"}),
                         title=f"All Transactions for {top_wallet}", labels={"color": "Status"})
        st.plotly_chart(fig, use_container_width=True)

    with tab_whale:
        st.markdown("### Whale Alerts")
        whale_thresh = st.sidebar.slider("Whale Threshold", min_value=100.0, max_value=10000.0, value=1000.0, step=100.0)
        whales = df[df["amount"] > whale_thresh]
        if not whales.empty:
            st.warning(f"{len(whales)} whale transactions detected!")
            st.dataframe(whales)
        else:
            st.info("No whale activity in current filter range.")

    with tab_raw:
        st.markdown("### Raw Transactions")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "transactions_filtered.csv", "text/csv")

    with tab_time_trend:
        st.markdown("### Transactions Over Time")
        trend_df = df.set_index("timestamp").resample("1H").size().reset_index(name="transaction_count")
        fig = px.line(trend_df, x="timestamp", y="transaction_count", markers=True, height=350)
        fig.update_layout(xaxis_title="Time", yaxis_title="Number of Transactions", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)




