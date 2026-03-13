<?php
/**
 * OpTrade — Database layer (SQLite via PDO)
 */
require_once __DIR__ . '/config.php';

function get_db(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        $pdo = new PDO('sqlite:' . DB_PATH);
        $pdo->setAttribute(PDO::ATTR_ERRMODE,            PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        _init_db($pdo);
    }
    return $pdo;
}

function _init_db(PDO $pdo): void {
    $pdo->exec("PRAGMA journal_mode = WAL");
    $pdo->exec("PRAGMA foreign_keys = ON");
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            email         TEXT     UNIQUE NOT NULL,
            password_hash TEXT     NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

        CREATE TABLE IF NOT EXISTS tracked_stocks (
            id         INTEGER  PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER  NOT NULL,
            ticker     TEXT     NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, ticker)
        );
        CREATE INDEX IF NOT EXISTS idx_ts_user   ON tracked_stocks(user_id);
        CREATE INDEX IF NOT EXISTS idx_ts_ticker ON tracked_stocks(ticker);

        CREATE TABLE IF NOT EXISTS signals (
            id              INTEGER  PRIMARY KEY AUTOINCREMENT,
            ticker          TEXT     NOT NULL,
            signal_type     TEXT     NOT NULL,
            signal_strength INTEGER  NOT NULL,
            score           INTEGER,
            last_price      REAL,
            next_day_price  REAL,
            price_change    REAL,
            rsi             REAL,
            trend           TEXT,
            hmm_label       TEXT,
            summary         TEXT,
            checked_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_sig_ticker ON signals(ticker);

        CREATE TABLE IF NOT EXISTS email_log (
            id              INTEGER  PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER  NOT NULL,
            ticker          TEXT     NOT NULL,
            signal_type     TEXT     NOT NULL,
            signal_strength INTEGER  NOT NULL,
            sent_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS login_attempts (
            id         INTEGER  PRIMARY KEY AUTOINCREMENT,
            ip         TEXT     NOT NULL,
            email      TEXT     NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ");
}

// ── Users ─────────────────────────────────────────────────────────────────────
function db_create_user(string $email, string $password): int|false {
    $pdo  = get_db();
    $hash = password_hash($password, PASSWORD_DEFAULT);
    try {
        $stmt = $pdo->prepare("INSERT INTO users (email, password_hash) VALUES (?, ?)");
        $stmt->execute([$email, $hash]);
        return (int) $pdo->lastInsertId();
    } catch (PDOException $e) {
        return false;   // likely duplicate email
    }
}

function db_find_user_by_email(string $email): array|null {
    $stmt = get_db()->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function db_find_user_by_id(int $id): array|null {
    $stmt = get_db()->prepare("SELECT id, email, created_at FROM users WHERE id = ?");
    $stmt->execute([$id]);
    $row = $stmt->fetch();
    return $row ?: null;
}

// ── Tracked stocks ────────────────────────────────────────────────────────────
function db_add_tracked(int $user_id, string $ticker): bool {
    try {
        $stmt = get_db()->prepare(
            "INSERT OR IGNORE INTO tracked_stocks (user_id, ticker) VALUES (?, ?)"
        );
        $stmt->execute([$user_id, strtoupper($ticker)]);
        return true;
    } catch (PDOException) { return false; }
}

function db_remove_tracked(int $user_id, string $ticker): void {
    $stmt = get_db()->prepare(
        "DELETE FROM tracked_stocks WHERE user_id = ? AND ticker = ?"
    );
    $stmt->execute([$user_id, strtoupper($ticker)]);
}

function db_get_tracked(int $user_id): array {
    $stmt = get_db()->prepare(
        "SELECT ticker, created_at FROM tracked_stocks WHERE user_id = ? ORDER BY created_at DESC"
    );
    $stmt->execute([$user_id]);
    return $stmt->fetchAll();
}

function db_count_tracked(int $user_id): int {
    $stmt = get_db()->prepare("SELECT COUNT(*) FROM tracked_stocks WHERE user_id = ?");
    $stmt->execute([$user_id]);
    return (int) $stmt->fetchColumn();
}

function db_all_unique_tickers(): array {
    $rows = get_db()->query("SELECT DISTINCT ticker FROM tracked_stocks")->fetchAll();
    return array_column($rows, 'ticker');
}

function db_users_tracking(string $ticker): array {
    $stmt = get_db()->prepare("
        SELECT u.id, u.email
        FROM tracked_stocks ts
        JOIN users u ON u.id = ts.user_id
        WHERE ts.ticker = ?
    ");
    $stmt->execute([strtoupper($ticker)]);
    return $stmt->fetchAll();
}

// ── Signals ───────────────────────────────────────────────────────────────────
function db_save_signal(array $d): void {
    // keep only the latest signal per ticker
    get_db()->prepare("DELETE FROM signals WHERE ticker = ?")->execute([$d['ticker']]);
    $stmt = get_db()->prepare("
        INSERT INTO signals
            (ticker, signal_type, signal_strength, score, last_price, next_day_price,
             price_change, rsi, trend, hmm_label, summary)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ");
    $stmt->execute([
        $d['ticker'], $d['signal_type'], $d['signal_strength'], $d['score'] ?? null,
        $d['last_price'] ?? null, $d['next_day_price'] ?? null,
        $d['price_change'] ?? null, $d['rsi'] ?? null,
        $d['trend'] ?? null, $d['hmm_label'] ?? null, $d['summary'] ?? null,
    ]);
}

function db_get_signal(string $ticker): array|null {
    $stmt = get_db()->prepare("SELECT * FROM signals WHERE ticker = ? LIMIT 1");
    $stmt->execute([strtoupper($ticker)]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function db_signal_is_fresh(string $ticker): bool {
    $sig = db_get_signal($ticker);
    if (!$sig) return false;
    $age_min = (time() - strtotime($sig['checked_at'])) / 60;
    return $age_min < SIGNAL_CACHE_MIN;
}

// ── Email log ─────────────────────────────────────────────────────────────────
/** Returns true if we already sent an alert to this user/ticker today. */
function db_already_notified(int $user_id, string $ticker, string $signal_type): bool {
    $stmt = get_db()->prepare("
        SELECT COUNT(*) FROM email_log
        WHERE user_id = ? AND ticker = ? AND signal_type = ?
          AND sent_at >= datetime('now', '-24 hours')
    ");
    $stmt->execute([$user_id, strtoupper($ticker), $signal_type]);
    return (int) $stmt->fetchColumn() > 0;
}

function db_log_email(int $user_id, string $ticker, string $signal_type, int $strength): void {
    $stmt = get_db()->prepare("
        INSERT INTO email_log (user_id, ticker, signal_type, signal_strength)
        VALUES (?,?,?,?)
    ");
    $stmt->execute([$user_id, strtoupper($ticker), $signal_type, $strength]);
}

// ── Rate limiting ─────────────────────────────────────────────────────────────
function db_rate_limited(string $ip, string $email): bool {
    $pdo  = get_db();
    $pdo->prepare("
        DELETE FROM login_attempts
        WHERE created_at < datetime('now', '-" . RATE_LIMIT_MIN . " minutes')
    ")->execute();
    $stmt = $pdo->prepare("
        SELECT COUNT(*) FROM login_attempts
        WHERE ip = ? AND email = ?
    ");
    $stmt->execute([$ip, $email]);
    return (int) $stmt->fetchColumn() >= RATE_LIMIT_MAX;
}

function db_record_attempt(string $ip, string $email): void {
    get_db()->prepare(
        "INSERT INTO login_attempts (ip, email) VALUES (?,?)"
    )->execute([$ip, $email]);
}
