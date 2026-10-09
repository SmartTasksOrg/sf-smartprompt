<?php
/* SmartPrompt - native PHP port. Reproduces sf_smartprompt.core.lint exactly. No deps. */
$RULES = [
  ['PROMPT-ROLE', 'No role/persona set', '/\b(you are|act as|role:)\b/i', false, "Open with a role: 'You are a <expert> ...'."],
  ['PROMPT-GOAL', 'Vague or missing goal', '/\b(write|summariz|analyz|list|compare|generate|fix|explain|classif)/i', false, 'State one concrete verb+object.'],
  ['PROMPT-FORMAT', 'No output format', '/\b(json|markdown|table|bullet|list|format|schema)\b/i', false, 'Name the output shape.'],
  ['PROMPT-CONSTRAINTS', 'No constraints', '/\b(word|sentence|tone|audience|concise|under \d)/i', false, 'Add limits: length, tone, audience.'],
  ['PROMPT-PII', 'Secret/PII in prompt', '/(sk-[A-Za-z0-9]{12,}|AKIA[0-9A-Z]{12,})/', true, "Remove the secret \u{2014} see SmartPangolin."],
];
$WEIGHT = ['PROMPT-PII' => 35, 'PROMPT-GOAL' => 20, 'PROMPT-ROLE' => 12, 'PROMPT-FORMAT' => 12, 'PROMPT-CONSTRAINTS' => 10];

function lint(string $text, array $RULES, array $WEIGHT): array {
    $defects = []; $total = 0;
    foreach ($RULES as [$rule, $issue, $re, $positive, $fix]) {
        $m = preg_match($re, $text) === 1;
        $fires = $positive ? $m : !$m;
        if ($fires) { $defects[] = ['rule' => $rule, 'issue' => $issue, 'fix' => $fix]; $total += $WEIGHT[$rule] ?? 6; }
    }
    return ['clarity' => max(0, 100 - $total), 'defects' => $defects];
}

$argv1 = $argv[1] ?? null;
if ($argv1 === '--text') { echo json_encode(lint($argv[2] ?? '', $RULES, $WEIGHT), JSON_UNESCAPED_UNICODE), "\n"; exit(0); }
$vpath = $argv1 ?? __DIR__ . '/../conformance/vectors.json';
$v = json_decode(file_get_contents($vpath), true);
$results = [];
foreach ($v['cases'] as $c) $results[] = array_merge(['name' => $c['name']], lint($c['text'] ?? '', $RULES, $WEIGHT));
echo json_encode(['results' => $results], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), "\n";
