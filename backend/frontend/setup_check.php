<?php
/**
 * OpTrade — Setup Check
 * Visit http://localhost:8080/setup_check.php to verify everything is working.
 * DELETE this file before going to production.
 */
require_once __DIR__ . '/db.php';

$checks = [];

// 1. PHP version
$checks[] = [
    'label' => 'PHP version',
    'ok'    => version_compare(PHP_VERSION, '8.0', '>='),
    'value' => PHP_VERSION,
    'note'  => 'Requires PHP 8.0+',
];

// 2. PDO SQLite
$checks[] = [
    'label' => 'PDO SQLite',
    'ok'    => extension_loaded('pdo_sqlite'),
    'value' => extension_loaded('pdo_sqlite') ? 'Available' : 'Missing',
    'note'  => 'Required for the database',
];

// 3. Database writable
$db_dir = dirname(DB_PATH);
$db_ok  = is_writable($db_dir);
try { get_db(); $db_created = true; } catch (Exception $e) { $db_created = false; }
$checks[] = [
    'label' => 'SQLite database',
    'ok'    => $db_created,
    'value' => $db_created ? 'Created at ' . DB_PATH : 'Failed to create',
    'note'  => 'Database file is auto-created on first visit',
];

// 4. Cache directory writable
$cache_dir = realpath(__DIR__ . '/../cache');
$checks[] = [
    'label' => 'Cache directory',
    'ok'    => $cache_dir && is_writable($cache_dir),
    'value' => $cache_dir ? ($cache_dir . (is_writable($cache_dir) ? ' (writable)' : ' (NOT writable)')) : 'Missing',
    'note'  => 'backend/cache/ must be writable for stock data caching',
];

// 5. Python interpreter
$project_root = realpath(__DIR__ . '/../..');
$py_candidates = [
    $project_root . '/venv/bin/python3',
    $project_root . '/.venv/bin/python3',
    '/opt/homebrew/bin/python3',
    '/usr/local/bin/python3',
    'python3',
];
$python = null;
foreach ($py_candidates as $c) {
    $test = shell_exec('command -v ' . escapeshellarg($c) . ' 2>/dev/null');
    if (!empty(trim($test ?? '')) || file_exists($c)) { $python = $c; break; }
}
$py_ver = $python ? trim(shell_exec(escapeshellcmd($python) . ' --version 2>&1') ?? '') : '';
$checks[] = [
    'label' => 'Python interpreter',
    'ok'    => $python !== null,
    'value' => $python ? "$python ($py_ver)" : 'Not found',
    'note'  => 'Required to run the AI model',
];

// 6. train_model.py exists
$script = realpath(__DIR__ . '/../train_model.py');
$checks[] = [
    'label' => 'train_model.py',
    'ok'    => $script && file_exists($script),
    'value' => $script ?: 'Not found',
    'note'  => 'Main ML pipeline',
];

// 7. Python packages (quick check)
if ($python) {
    $pkgs = ['numpy','pandas','tensorflow','hmmlearn','yfinance','sklearn'];
    $missing = [];
    foreach ($pkgs as $pkg) {
        $r = shell_exec(escapeshellcmd($python) . ' -c "import ' . $pkg . '" 2>&1');
        if (!empty(trim($r ?? ''))) $missing[] = $pkg;
    }
    $checks[] = [
        'label' => 'Python packages',
        'ok'    => empty($missing),
        'value' => empty($missing) ? 'All core packages found' : 'Missing: ' . implode(', ', $missing),
        'note'  => 'Install with: pip install -r requirements.txt',
    ];
}

// 8. Sessions writable
$sess_ok = session_start();
$_SESSION['_test'] = 1;
$checks[] = [
    'label' => 'PHP sessions',
    'ok'    => $sess_ok,
    'value' => $sess_ok ? 'Working' : 'Failed',
    'note'  => 'Required for login/auth',
];

// 9. Email config
$email_ok = SMTP_HOST !== '' || function_exists('mail');
$checks[] = [
    'label' => 'Email',
    'ok'    => $email_ok,
    'value' => SMTP_HOST !== '' ? 'SMTP configured (' . SMTP_HOST . ')' : (function_exists('mail') ? 'PHP mail() fallback' : 'No email method available'),
    'note'  => 'Configure SMTP in config.php for reliable email alerts',
];

$all_ok = array_reduce($checks, fn($carry, $c) => $carry && $c['ok'], true);
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Setup Check — OpTrade</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0D1B2A;color:#ECEFF1;font-family:'Segoe UI',system-ui,sans-serif;
  padding:32px 16px;min-height:100vh}
.wrap{max-width:700px;margin:0 auto}
h1{font-size:1.6rem;font-weight:700;margin-bottom:4px}
.sub{color:#78909C;font-size:.9rem;margin-bottom:28px}
.banner{padding:16px 22px;border-radius:10px;margin-bottom:24px;font-weight:600}
.ok{background:#1B4332;border:2px solid #66BB6A;color:#A5D6A7}
.fail{background:#3D1A1A;border:2px solid #EF5350;color:#EF9A9A}
.check{background:#1A2B3C;border:1px solid #1E3A5F;border-radius:10px;
  padding:14px 18px;margin-bottom:10px;display:flex;align-items:flex-start;gap:14px}
.badge{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:.85rem;flex-shrink:0;margin-top:2px}
.badge.ok{background:#1B4332;color:#66BB6A}
.badge.fail{background:#3D1A1A;color:#EF5350}
.cl{font-weight:600;font-size:.95rem}
.cv{color:#90A4AE;font-size:.85rem;margin-top:2px;word-break:break-all}
.cn{color:#546E7A;font-size:.75rem;margin-top:3px}
.btn{display:inline-block;background:#29B6F6;color:#0D1B2A;text-decoration:none;
  padding:10px 24px;border-radius:8px;font-weight:700;margin-top:20px;margin-right:10px}
.btn-outline{background:transparent;border:2px solid #29B6F6;color:#29B6F6}
.warning{background:#2C2800;border:1px solid #FFF17644;border-radius:8px;
  padding:12px 16px;color:#FFF176;font-size:.82rem;margin-top:20px}
</style>
</head>
<body>
<div class="wrap">
  <h1>📈 OpTrade Setup Check</h1>
  <p class="sub">Verifies that all required components are working correctly.</p>

  <div class="banner <?= $all_ok ? 'ok' : 'fail' ?>">
    <?= $all_ok ? '✅ All checks passed — your website is ready!' : '⚠️ Some checks failed — see details below' ?>
  </div>

  <?php foreach ($checks as $c): ?>
  <div class="check">
    <div class="badge <?= $c['ok'] ? 'ok' : 'fail' ?>"><?= $c['ok'] ? '✓' : '✗' ?></div>
    <div>
      <div class="cl"><?= htmlspecialchars($c['label']) ?></div>
      <div class="cv"><?= htmlspecialchars($c['value']) ?></div>
      <?php if (!$c['ok']): ?>
        <div class="cn">💡 <?= htmlspecialchars($c['note']) ?></div>
      <?php endif; ?>
    </div>
  </div>
  <?php endforeach; ?>

  <div style="margin-top:28px">
    <a class="btn" href="index.php">← Main Analysis</a>
    <a class="btn btn-outline" href="auth.php">Sign In / Sign Up</a>
    <a class="btn btn-outline" href="dashboard.php">Dashboard</a>
  </div>

  <div class="warning">
    ⚠️ <strong>Security:</strong> Delete or password-protect this file before deploying to production.
    It exposes server paths and configuration details.
  </div>
</div>
</body>
</html>
