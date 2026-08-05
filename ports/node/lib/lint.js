'use strict';
/*
 * SmartPrompt — native Node port.
 * Reproduces the Python reference (smartprompt.core.lint): same rule IDs, issue
 * and fix strings, ordering, weights, and clarity score. Zero dependencies.
 */
const RULES = [
  ['PROMPT-ROLE', 'No role/persona set',
    t => !/\b(you are|act as|role:)\b/i.test(t), "Open with a role: 'You are a <expert> ...'."],
  ['PROMPT-GOAL', 'Vague or missing goal',
    t => !/\b(write|summariz|analyz|list|compare|generate|fix|explain|classif)/i.test(t), 'State one concrete verb+object.'],
  ['PROMPT-FORMAT', 'No output format',
    t => !/\b(json|markdown|table|bullet|list|format|schema)\b/i.test(t), 'Name the output shape.'],
  ['PROMPT-CONSTRAINTS', 'No constraints',
    t => !/\b(word|sentence|tone|audience|concise|under \d)/i.test(t), 'Add limits: length, tone, audience.'],
  ['PROMPT-PII', 'Secret/PII in prompt',
    t => /(sk-[A-Za-z0-9]{12,}|AKIA[0-9A-Z]{12,})/.test(t), 'Remove the secret \u2014 see SmartPangolin.'],
];
const WEIGHT = { 'PROMPT-PII': 35, 'PROMPT-GOAL': 20, 'PROMPT-ROLE': 12, 'PROMPT-FORMAT': 12, 'PROMPT-CONSTRAINTS': 10 };

function lint(text) {
  const defects = [];
  for (const [rule, issue, test, fix] of RULES) if (test(text)) defects.push({ rule, issue, fix });
  const score = Math.max(0, 100 - defects.reduce((s, d) => s + (WEIGHT[d.rule] ?? 6), 0));
  return { clarity: score, defects };
}
module.exports = { lint };
