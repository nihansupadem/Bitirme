import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

MAIL_FROM = os.environ.get('MAIL_FROM', 'noreply@optrade.app')
MAIL_NAME = os.environ.get('MAIL_NAME', 'OpTrade Alerts')
SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
APP_URL   = os.environ.get('APP_URL', 'http://localhost:8080')

def send_email(to_email, to_name, subject, html_body):
    if not SMTP_HOST:
        print(f"Skipping email to {to_email} (SMTP_HOST not set). Subject: {subject}")
        return True # Mock success
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{MAIL_NAME} <{MAIL_FROM}>"
        msg['To'] = f"{to_name} <{to_email}>"
        
        # text part (fallback)
        from bs4 import BeautifulSoup
        try:
            text_part = BeautifulSoup(html_body, "html.parser").get_text()
        except Exception:
            text_part = "Please view this email in an HTML compatible client."
        
        msg.attach(MIMEText(text_part, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Assuming SSL port 465 as default
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            
        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
            
        server.sendmail(MAIL_FROM, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return str(e)

def email_signal_alert(to_email, to_name, ticker, signal_type, strength, price, next_price, summary):
    color = '#66BB6A' if signal_type in ['STRONG BUY', 'BUY'] else '#EF5350'
    emoji = '📈' if signal_type in ['STRONG BUY', 'BUY'] else '📉'
    
    pch = 0
    if price > 0:
        pch = round(((next_price - price) / price) * 100, 2)
    pch_sign = '+' if pch >= 0 else ''
    
    subject = f"{emoji} {signal_type} Alert – {ticker} | OpTrade"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8">
    <style>
      body{{font-family:'Segoe UI',Arial,sans-serif;background:#0D1B2A;color:#ECEFF1;margin:0;padding:0;}}
      .wrap{{max-width:580px;margin:40px auto;background:#1A2B3C;border-radius:12px;overflow:hidden;}}
      .hdr{{background:linear-gradient(135deg,#0D1B2A,#1A2B3C);padding:28px 32px;border-bottom:3px solid {color};}}
      .hdr h1{{margin:0;font-size:1.5rem;color:#ECEFF1;}}
      .hdr p{{margin:6px 0 0;color:#78909C;font-size:0.88rem;}}
      .body{{padding:28px 32px;}}
      .signal-badge{{display:inline-block;background:{color}22;border:2px solid {color};
        color:{color};padding:10px 22px;border-radius:30px;font-size:1.3rem;
        font-weight:800;letter-spacing:.05em;margin-bottom:20px;}}
      .row{{display:flex;justify-content:space-between;padding:10px 0;
        border-bottom:1px solid #1E3A5F;}}
      .row:last-child{{border-bottom:none;}}
      .row .lbl{{color:#78909C;font-size:.85rem;}}
      .row .val{{color:#ECEFF1;font-weight:600;}}
      .summary{{background:#0D1B2A;border-left:4px solid #29B6F6;border-radius:0 8px 8px 0;
        padding:14px 18px;margin:20px 0;color:#CFD8DC;font-size:.9rem;line-height:1.6;}}
      .footer{{padding:18px 32px;background:#0D1B2A;font-size:.78rem;color:#546E7A;
        border-top:1px solid #1E3A5F;}}
      .btn{{display:inline-block;background:#29B6F6;color:#0D1B2A;text-decoration:none;
        padding:12px 28px;border-radius:8px;font-weight:700;margin-top:16px;}}
    </style>
    </head>
    <body>
    <div class="wrap">
      <div class="hdr">
        <h1>{emoji} OpTrade Signal Alert</h1>
        <p>AI-powered BIST30 signal for {ticker}</p>
      </div>
      <div class="body">
        <div class="signal-badge">{signal_type}</div>
        <div class="row"><span class="lbl">Stock</span><span class="val">{ticker}</span></div>
        <div class="row"><span class="lbl">Signal Strength</span><span class="val" style="color:{color};">{strength}%</span></div>
        <div class="row"><span class="lbl">Current Price</span><span class="val">₺{price}</span></div>
        <div class="row"><span class="lbl">Forecast (next day)</span><span class="val">₺{next_price} <small style="color:{color};">({pch_sign}{pch}%)</small></span></div>
        <div class="summary">{summary}</div>
        <a class="btn" href="{APP_URL}">View Full Analysis</a>
        <p style="color:#546E7A;font-size:.8rem;margin-top:20px;">
          You're receiving this because you track {ticker} on OpTrade.
        </p>
      </div>
      <div class="footer">
        ⚠️ <strong>Disclaimer:</strong> This is an educational AI tool, not financial advice.
        Forecasts can be wrong. Always do your own research before investing.<br><br>
        OpTrade
      </div>
    </div>
    </body>
    </html>
    """
    
    return send_email(to_email, to_name, subject, html_body)
