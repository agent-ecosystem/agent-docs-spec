<?php
// Agent signal tracker.
// Logs full request headers for requests that are likely from agents:
// content-negotiated markdown, direct .md requests, and llms.txt.
// Logging is best-effort; failures never block content delivery.

$path = preg_replace('#/+#', '/', $_GET['path'] ?? '');
$trigger = $_GET['trigger'] ?? 'unknown';

// Validate: only serve .md and .txt files, prevent directory traversal
if (str_contains($path, '..')) {
    http_response_code(400);
    exit;
}

$allowedExtensions = ['.md', '.txt'];
$validExtension = false;
foreach ($allowedExtensions as $ext) {
    if (str_ends_with($path, $ext)) {
        $validExtension = true;
        break;
    }
}
if (!$validExtension) {
    http_response_code(400);
    exit;
}

$file = $_SERVER['DOCUMENT_ROOT'] . '/' . ltrim($path, '/');

if (!file_exists($file)) {
    http_response_code(404);
    exit;
}

// Determine content type from extension
$contentType = str_ends_with($path, '.md') ? 'text/markdown' : 'text/plain';

// Best-effort logging — never block content delivery
// Config file lives in the user's home directory, outside any repo.
// PHP-FPM doesn't set HOME, so derive it from DOCUMENT_ROOT (e.g.
// /home/user/example.com -> /home/user)
$homeDir = dirname($_SERVER['DOCUMENT_ROOT'] ?? '');
$config = @include($homeDir . '/agent-signal-config.php');
$logDir = ($config['log_dir'] ?? null);

if ($logDir) {
    if (!is_dir($logDir)) {
        @mkdir($logDir, 0750, true);
    }

    // Collect all request headers
    $allHeaders = getallheaders() ?: [];

    // Build a JSON log entry for rich, parseable data
    $entry = [
        'timestamp' => gmdate('Y-m-d\TH:i:s\Z'),
        'domain' => $_SERVER['HTTP_HOST'] ?? '-',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? '-',
        'method' => $_SERVER['REQUEST_METHOD'] ?? '-',
        'path' => $path,
        'trigger' => $trigger,
        'headers' => $allHeaders,
    ];

    @file_put_contents(
        $logDir . '/agent-signals.jsonl',
        json_encode($entry, JSON_UNESCAPED_SLASHES) . "\n",
        FILE_APPEND | LOCK_EX
    );
}

// Serve the file — remove any server-level cache headers first
header_remove('Cache-Control');
header_remove('Expires');
header('Content-Type: ' . $contentType . '; charset=utf-8');
header('Cache-Control: max-age=3600, must-revalidate');
readfile($file);
