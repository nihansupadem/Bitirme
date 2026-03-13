<?php
/**
 * OpTrade — Configuration
 * Edit the SMTP section before deploying if you want email alerts.
 */

// ── Database ─────────────────────────────────────────────────────────────────
define('DB_PATH', __DIR__ . '/../optrade.db');

// ── Email (Alerts) ────────────────────────────────────────────────────────────
// Sender identity
define('MAIL_FROM',  'noreply@optrade.app');   // change to your address
define('MAIL_NAME',  'OpTrade Alerts');

// SMTP — leave SMTP_HOST empty to fall back to PHP mail()
// Gmail example : 'ssl://smtp.gmail.com'  port 465
// Outlook example: 'ssl://smtp.live.com'  port 465
define('SMTP_HOST',  '');
define('SMTP_PORT',  465);
define('SMTP_USER',  '');    // your email address
define('SMTP_PASS',  '');    // app password (Gmail: generate in Google Account settings)

// ── App ───────────────────────────────────────────────────────────────────────
define('APP_URL',          'https://ibrahimaydinn-optrade-pro.hf.space');  // HuggingFace Space URL
define('APP_NAME',         'OpTrade');
define('ALERT_THRESHOLD',  75);    // minimum signal_strength % to trigger email
define('SIGNAL_CACHE_MIN', 60);    // minutes before a signal is considered stale
define('MAX_TRACKED',      20);    // max stocks a single user can track
define('RATE_LIMIT_MAX',   5);     // max failed login attempts
define('RATE_LIMIT_MIN',   15);    // minutes window for rate limiting
