#!/usr/bin/env python3
"""
OpTrade — BIST30 Stock Forecasting
HuggingFace Spaces entry point (Gradio)
"""

import gradio as gr
import subprocess, json, base64, sys, os
from PIL import Image
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT   = os.path.join(BASE_DIR, 'backend', 'train_model.py')
PYTHON   = sys.executable   # same Python that's running Gradio

STOCKS = [
    'AKBNK','ASELS','BIMAS','DOHOL','EKGYO','ENKAI','EREGL',
    'FROTO','GARAN','GUBRF','HALKB','ISCTR','KCHOL','KOZAA',
    'KOZAL','KRDMD','MGROS','ODAS','PETKM','PGSUS','SAHOL',
    'SASA','SISE','TAVHL','TCELL','THYAO','TKFEN','TOASO',
    'TUPRS','ULKER','VAKBN','VESTL','YKBNK',
]

# ── dark theme CSS ─────────────────────────────────────────────────────────────
DARK_CSS = """
body, .gradio-container {
    background: #0D1B2A !important;
    color: #ECEFF1 !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}
.header-band {
    background: linear-gradient(135deg, #0D1B2A 0%, #1A2B3C 100%);
    border-bottom: 2px solid #29B6F6;
    padding: 28px 32px 18px;
    margin-bottom: 24px;
    border-radius: 10px;
}
.header-band h1 {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg,#29B6F6,#AB47BC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 4px 0;
}
.header-band p { color:#78909C; margin:0; font-size:0.95rem; }
/* signal banner */
.signal-banner {
    padding: 20px 28px;
    border-radius: 12px;
    margin: 20px 0;
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 1.1rem;
    font-weight: 600;
}
.signal-STRONG-BUY  { background:#1B4332; border:2px solid #66BB6A; }
.signal-BUY         { background:#1B3D2A; border:2px solid #A5D6A7; }
.signal-HOLD        { background:#2C2800; border:2px solid #FFF176; }
.signal-SELL        { background:#3D1A1A; border:2px solid #EF9A9A; }
.signal-STRONG-SELL { background:#4A0A0A; border:2px solid #EF5350; }
/* info cards grid */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 16px 0;
}
.card {
    background: #1A2B3C;
    border: 1px solid #1E3A5F;
    border-radius: 10px;
    padding: 16px 20px;
}
.card .label { color:#78909C; font-size:0.78rem; text-transform:uppercase; letter-spacing:.06em; }
.card .value { font-size:1.6rem; font-weight:700; color:#29B6F6; margin:4px 0 2px; }
.card .sub   { font-size:0.82rem; color:#90A4AE; }
/* levels */
.levels-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 16px 0;
}
.level-card { background:#1A2B3C; border-radius:10px; padding:16px; text-align:center; }
.level-card .lc-label { color:#78909C; font-size:0.78rem; text-transform:uppercase; }
.level-card .lc-val   { font-size:1.5rem; font-weight:700; margin:4px 0; }
.lc-entry  { border:2px solid #29B6F6; }
.lc-target { border:2px solid #66BB6A; }
.lc-stop   { border:2px solid #EF5350; }
/* context cards */
.ctx-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
    margin: 16px 0;
}
.ctx-card { background:#1A2B3C; border:1px solid #1E3A5F; border-radius:10px; padding:16px 20px; }
.ctx-card .ctx-title { font-weight:700; font-size:1rem; margin-bottom:6px; }
.ctx-card .ctx-desc  { color:#90A4AE; font-size:0.87rem; line-height:1.55; }
/* summary box */
.summary-box {
    background: #1A2B3C;
    border-left: 4px solid #29B6F6;
    border-radius: 0 10px 10px 0;
    padding: 16px 22px;
    margin: 16px 0;
    color: #CFD8DC;
    font-size: 0.95rem;
    line-height: 1.65;
}
/* metric pills */
.metrics-row { display:flex; gap:12px; flex-wrap:wrap; margin:16px 0; }
.metric-pill {
    background:#1A2B3C;
    border:1px solid #1E3A5F;
    border-radius:8px;
    padding:10px 18px;
    text-align:center;
}
.metric-pill .mp-label { color:#78909C; font-size:0.73rem; text-transform:uppercase; }
.metric-pill .mp-val   { color:#29B6F6; font-size:1.15rem; font-weight:700; }
/* section titles */
.sec-title {
    color:#ECEFF1;
    font-size:1.1rem;
    font-weight:700;
    margin:24px 0 10px;
    padding-bottom:6px;
    border-bottom:1px solid #1E3A5F;
}
.disclaimer {
    background:#0D1B2A;
    border:1px solid #1E3A5F;
    border-radius:8px;
    padding:14px 20px;
    color:#78909C;
    font-size:0.8rem;
    margin-top:20px;
}
/* live data badge */
.live-badge {
    display: inline-block;
    background: #00C853;
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 0.04em;
    animation: pulse-live 2s infinite;
    vertical-align: middle;
    margin-left: 6px;
}
@keyframes pulse-live {
    0%, 100% { opacity:1; }
    50%      { opacity:0.5; }
}
.live-row {
    background: linear-gradient(90deg, #0D2818 0%, #1A2B3C 100%);
    border: 1px solid #00C853;
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
}
.live-row .live-item { text-align:center; min-width:80px; }
.live-row .live-label { color:#78909C; font-size:0.7rem; text-transform:uppercase; }
.live-row .live-val { color:#00E676; font-size:1.15rem; font-weight:700; }
/* Gradio overrides */
.gr-button-primary { background:#29B6F6 !important; border-color:#29B6F6 !important; }
label { color:#90A4AE !important; }
select, .gr-box { background:#1A2B3C !important; border-color:#1E3A5F !important; color:#ECEFF1 !important; }
"""

# ── helpers ────────────────────────────────────────────────────────────────────
def b64_to_pil(b64str):
    return Image.open(io.BytesIO(base64.b64decode(b64str)))

def error_html(msg):
    return f"""
    <div style="background:#3D1A1A;border:2px solid #EF5350;border-radius:12px;
                padding:24px;margin:20px 0;color:#ECEFF1;">
        <div style="font-size:1.3rem;font-weight:700;color:#EF5350;margin-bottom:8px;">
            ❌ Error
        </div>
        <div style="color:#CFD8DC;">{msg}</div>
        <div style="margin-top:12px;color:#78909C;font-size:0.85rem;">
            Tip: Data sources may be temporarily unavailable. Wait 30 seconds and try again,
            or try a different stock.
        </div>
    </div>"""

def action_color(action):
    return {
        'STRONG BUY':  '#66BB6A',
        'BUY':         '#A5D6A7',
        'HOLD':        '#FFF176',
        'SELL':        '#EF9A9A',
        'STRONG SELL': '#EF5350',
    }.get(action, '#29B6F6')

def action_emoji(action):
    return {
        'STRONG BUY':  '🚀',
        'BUY':         '📈',
        'HOLD':        '⏸️',
        'SELL':        '📉',
        'STRONG SELL': '🔴',
    }.get(action, '📊')

def build_html(data):
    sig   = data['signal']
    met   = data['metrics']
    trd   = data['trading']
    sym   = data['symbol']
    lp    = data['last_price']
    ndp   = data['next_day_price']
    pch   = data['price_change']
    ld    = data['last_date']
    action = sig['action']
    css_cls = 'signal-' + action.replace(' ', '-')
    ac  = action_color(action)
    emo = action_emoji(action)
    pch_sign = '+' if pch >= 0 else ''

    # Build live-price banner if BIST live data is available
    live_html = ''
    bl = data.get('bist_live')
    if bl and bl.get('live_price'):
        live_html = f"""
<div class="live-row">
  <div style="font-weight:700;color:#00E676;font-size:1rem;">
    BORSA ISTANBUL <span class="live-badge">LIVE</span>
  </div>
  <div class="live-item">
    <div class="live-label">Price</div>
    <div class="live-val">{bl['live_price']:.2f}</div>
  </div>
  <div class="live-item">
    <div class="live-label">Open</div>
    <div class="live-val" style="color:#29B6F6;">{bl['open']:.2f}</div>
  </div>
  <div class="live-item">
    <div class="live-label">High</div>
    <div class="live-val" style="color:#66BB6A;">{bl['high']:.2f}</div>
  </div>
  <div class="live-item">
    <div class="live-label">Low</div>
    <div class="live-val" style="color:#EF5350;">{bl['low']:.2f}</div>
  </div>
  <div class="live-item">
    <div class="live-label">Bid</div>
    <div class="live-val" style="color:#90A4AE;">{bl['bid']:.2f}</div>
  </div>
  <div class="live-item">
    <div class="live-label">Ask</div>
    <div class="live-val" style="color:#90A4AE;">{bl['ask']:.2f}</div>
  </div>
  <div style="color:#546E7A;font-size:0.7rem;margin-left:auto;">{bl.get('live_time','')}</div>
</div>"""

    return f"""
<div>

{live_html}

<!-- header row -->
<div class="cards-grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr))">
  <div class="card">
    <div class="label">Symbol</div>
    <div class="value" style="font-size:1.3rem;">{sym}</div>
    <div class="sub">As of {ld}</div>
  </div>
  <div class="card">
    <div class="label">Current Price</div>
    <div class="value">{lp:.2f}</div>
    <div class="sub">TRY (last close)</div>
  </div>
  <div class="card">
    <div class="label">Tomorrow's Forecast</div>
    <div class="value">{ndp:.2f}</div>
    <div class="sub" style="color:{'#66BB6A' if pch>=0 else '#EF5350'}">
      {pch_sign}{pch:.2f}% vs today
    </div>
  </div>
  <div class="card">
    <div class="label">Signal Strength</div>
    <div class="value" style="color:{ac}">{sig['strength']}%</div>
    <div class="sub">Score {sig['score']} / 6</div>
  </div>
</div>

<!-- signal banner -->
<div class="signal-banner {css_cls}">
  <span style="font-size:2.2rem;">{emo}</span>
  <div>
    <div style="font-size:1.5rem;font-weight:800;color:{ac};">{action}</div>
    <div style="font-size:0.9rem;font-weight:400;color:#90A4AE;margin-top:2px;">
      AI Recommendation based on LSTM · RSI · EMA · HMM
    </div>
  </div>
</div>

<!-- summary -->
<div class="summary-box">{sig['summary']}</div>

<!-- key levels -->
<div class="sec-title">📍 Key Trading Levels</div>
<div class="levels-grid">
  <div class="level-card lc-entry">
    <div class="lc-label">Entry Zone</div>
    <div class="lc-val" style="color:#29B6F6;">{sig['entry_low']:.2f} – {sig['entry_high']:.2f}</div>
    <div style="color:#78909C;font-size:0.8rem;">Suggested buy range (TRY)</div>
  </div>
  <div class="level-card lc-target">
    <div class="lc-label">Price Target</div>
    <div class="lc-val" style="color:#66BB6A;">{sig['target']:.2f}</div>
    <div style="color:#78909C;font-size:0.8rem;">Model's short-term target</div>
  </div>
  <div class="level-card lc-stop">
    <div class="lc-label">Stop Loss</div>
    <div class="lc-val" style="color:#EF5350;">{sig['stop_loss']:.2f}</div>
    <div style="color:#78909C;font-size:0.8rem;">Exit if price drops below</div>
  </div>
</div>

<!-- market context -->
<div class="sec-title">🔍 Market Context</div>
<div class="ctx-grid">
  <div class="ctx-card">
    <div class="ctx-title" style="color:#AB47BC;">📊 RSI — {sig['rsi_label']}</div>
    <div class="ctx-desc">{sig['rsi_desc']}</div>
  </div>
  <div class="ctx-card">
    <div class="ctx-title" style="color:#29B6F6;">📉 Trend — {sig['trend']}</div>
    <div class="ctx-desc">{sig['trend_desc']}</div>
  </div>
  <div class="ctx-card">
    <div class="ctx-title" style="color:#FFA726;">🤖 AI Regime — {sig['hmm_label']}</div>
    <div class="ctx-desc">{sig['hmm_desc']}</div>
  </div>
</div>

<!-- model metrics -->
<div class="sec-title">📐 Model Accuracy (Out-of-Sample, last 20% of data)</div>
<div class="metrics-row">
  <div class="metric-pill">
    <div class="mp-label">MAE</div>
    <div class="mp-val">{met['mae']:.4f}</div>
  </div>
  <div class="metric-pill">
    <div class="mp-label">RMSE</div>
    <div class="mp-val">{met['rmse']:.4f}</div>
  </div>
  <div class="metric-pill">
    <div class="mp-label">MAPE</div>
    <div class="mp-val">{met['mape']:.2f}%</div>
  </div>
  <div class="metric-pill">
    <div class="mp-label">MSE</div>
    <div class="mp-val">{met['mse']:.4f}</div>
  </div>
</div>
<div style="color:#546E7A;font-size:0.8rem;margin:-8px 0 12px;">
  ℹ️ Metrics computed on test data the model never trained on (honest out-of-sample evaluation)
</div>

<!-- backtest stats -->
<div class="sec-title">💼 Strategy Backtest ({trd['test_days']}-day out-of-sample)</div>
<div class="cards-grid">
  <div class="card">
    <div class="label">Starting Capital</div>
    <div class="value" style="font-size:1.2rem;">₺100,000</div>
  </div>
  <div class="card">
    <div class="label">Final Portfolio Value</div>
    <div class="value" style="font-size:1.2rem;color:{'#66BB6A' if trd['final_value']>=100000 else '#EF5350'}">
      ₺{trd['final_value']:,.0f}
    </div>
  </div>
  <div class="card">
    <div class="label">Profit / Loss</div>
    <div class="value" style="font-size:1.2rem;color:{'#66BB6A' if trd['total_profit']>=0 else '#EF5350'}">
      {'+' if trd['total_profit']>=0 else ''}{trd['total_profit']:,.0f} TRY
    </div>
    <div class="sub">{'+' if trd['profit_pct']>=0 else ''}{trd['profit_pct']:.1f}%</div>
  </div>
  <div class="card">
    <div class="label">Win Rate</div>
    <div class="value">{trd['success_rate']:.1f}%</div>
    <div class="sub">{trd['num_trades']} trades placed</div>
  </div>
</div>

<!-- disclaimer -->
<div class="disclaimer">
  ⚠️ <strong>Disclaimer:</strong> OpTrade is an AI research tool, not financial advice.
  All forecasts are probabilistic and can be wrong. Past backtest performance does not
  guarantee future results. Always do your own research and consult a licensed financial
  adviser before investing. Never invest money you cannot afford to lose.
</div>

</div>"""

# ── core analysis function ─────────────────────────────────────────────────────
def analyze_stock(symbol, progress=gr.Progress(track_tqdm=True)):
    full_sym = symbol + '.IS'

    progress(0.05, desc="📡 Connecting to Yahoo Finance...")

    try:
        result = subprocess.run(
            [PYTHON, SCRIPT, full_sym],
            capture_output=True,
            text=True,
            timeout=360,
            cwd=BASE_DIR
        )
        output = result.stdout

        progress(0.85, desc="🎨 Rendering results...")

        # Find JSON in output (skip any warning lines before/after)
        json_start = output.find('{')
        if json_start == -1:
            err = result.stderr[-500:] if result.stderr else "No output from model."
            return error_html(f"Model produced no JSON output. stderr: {err}"), None, None, None

        json_end = output.rfind('}')
        if json_end == -1:
            return error_html("Malformed JSON output from model."), None, None, None

        data = json.loads(output[json_start:json_end + 1])

        if 'error' in data:
            return error_html(data['error']), None, None, None

        # Build HTML panel
        html = build_html(data)

        # Convert base64 charts to PIL images
        c1 = b64_to_pil(data['charts']['last_100_days'])
        c2 = b64_to_pil(data['charts']['full_range'])
        c3 = b64_to_pil(data['charts']['trading_strategy'])

        progress(1.0, desc="✅ Done!")
        return html, c1, c2, c3

    except subprocess.TimeoutExpired:
        return error_html("Analysis timed out (>6 min). The server may be busy — please try again in a moment."), None, None, None
    except json.JSONDecodeError as e:
        return error_html(f"JSON parse error: {e}"), None, None, None
    except Exception as e:
        return error_html(str(e)), None, None, None

# ── Gradio UI ──────────────────────────────────────────────────────────────────
with gr.Blocks(title="OpTrade — BIST30 Forecasting") as demo:

    gr.HTML("""
    <div class="header-band">
      <h1>📈 OpTrade</h1>
      <p>AI-powered BIST30 stock forecasting · LSTM + HMM + Monte Carlo · for educational purposes only</p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            stock_dd = gr.Dropdown(
                choices=STOCKS,
                value='YKBNK',
                label='Select a BIST30 Stock',
                info='Pick any stock from the Istanbul Stock Exchange BIST30 index',
            )
        with gr.Column(scale=1):
            analyze_btn = gr.Button(
                '🔍 Analyze',
                variant='primary',
                size='lg',
            )

    gr.HTML("""
    <div style="background:#1A2B3C;border:1px solid #1E3A5F;border-radius:8px;
                padding:12px 20px;color:#78909C;font-size:0.85rem;margin-bottom:8px;">
      ⏳ <strong>First analysis takes 2–4 minutes</strong> — the AI trains fresh on each stock.
      Subsequent requests for the same stock use a 12-hour cache and are much faster.
    </div>
    """)

    results_html = gr.HTML(label="Analysis Results")

    gr.HTML('<div class="sec-title">📊 Charts</div>')

    with gr.Row():
        chart1 = gr.Image(
            label='Last 100 Days — Actual vs Predicted',
            type='pil',
            buttons=["download"],
        )
        chart2 = gr.Image(
            label='Full History — Actual vs Predicted',
            type='pil',
            buttons=["download"],
        )

    chart3 = gr.Image(
        label='Trading Strategy Backtest (▲ Buy · ▼ Sell signals)',
        type='pil',
        buttons=["download"],
    )

    gr.HTML("""
    <div style="color:#546E7A;font-size:0.78rem;text-align:center;padding:8px 0 16px;">
      Blue line = Actual price &nbsp;|&nbsp; Orange dashed = Model prediction &nbsp;|&nbsp;
      Green region = Out-of-sample test zone
    </div>
    """)

    analyze_btn.click(
        fn=analyze_stock,
        inputs=[stock_dd],
        outputs=[results_html, chart1, chart2, chart3],
        show_progress=True,
        api_name="predict",
    )

if __name__ == '__main__':
    demo.launch(css=DARK_CSS, server_name="0.0.0.0")
