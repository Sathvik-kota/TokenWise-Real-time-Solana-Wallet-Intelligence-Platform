# TokenWise-Real-time-Solana-Wallet-Intelligence-Platform
TokenWise is a **real-time wallet intelligence dashboard** for Solana tokens.  
It tracks the **top 60 wallets** of any SPL token, receives live transaction updates via Helius webhooks, stores the data locally, and visualizes it in a **Streamlit dashboard** with animations and AI-powered anomaly detection.

## Features
- Fetch **top 60 token holders** via Helius RPC.
- Real-time **transaction monitoring** using Ngrok + Flask webhook.
- **Protocol inference** (Jupiter, Raydium, Orca or unknown ).
- **AI-based anomaly detection** using Isolation Forest.
- Beautiful, interactive **Streamlit dashboard** with Lottie animations.
- Fully runnable inside **Jupyter Notebooks**.

## Workflow
1. **Fetch Top Wallets**  
   Use `1_fetch_top_wallets.ipynb` to call Helius RPC and save the top 60 holders to `data/top_wallets.txt`.

2. **Ngrok Setup**  
   Use `2_ngrok_auth_and_url.ipynb` to authenticate Ngrok and get a public webhook URL.

3. **Register Webhook**  
   Use `3_register_webhook.ipynb` to register the public URL and top wallet list with Helius.

4. **Run Flask Server**  
   Use `4_flask_webhook_server.ipynb` to receive and process transactions in real time.

5. **View Dashboard**  
   Use `5_streamlit_dashboard.ipynb` to launch the dashboard and explore token activity.
