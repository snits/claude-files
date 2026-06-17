export const meta = {
  name: 'project-insights',
  description: 'Map-reduce a project\'s Claude Code session transcripts into an insights report (markdown)',
  phases: [
    { title: 'Map', detail: 'extract structured facets per session transcript (haiku)' },
    { title: 'Facets', detail: '7 aggregate facet generators + at-a-glance synthesis' },
  ],
}

// ---------------------------------------------------------------------------
// Inputs (from args): { projectName, outPath, files: [absolute jsonl paths] }
// Returns: { projectName, outPath, sessionCount, totals, markdown }
// The orchestrator (SKILL.md) discovers the file list and writes the markdown;
// this script is pure compute — Workflow scripts have no filesystem access.
// ---------------------------------------------------------------------------

// args may arrive as an object or as a JSON-encoded string depending on harness.
let input = args
if (typeof input === 'string') { try { input = JSON.parse(input) } catch (e) { input = {} } }
if (!input || typeof input !== 'object') input = {}

const projectName = input.projectName || 'project'
const outPath = input.outPath || ''
const files = input.files || []

if (!files.length) {
  return { projectName, outPath, sessionCount: 0, totals: {}, markdown: `# Insights: ${projectName}\n\nNo session transcripts found.\n` }
}

// ---- Schemas -------------------------------------------------------------

// Canonical key sets (from the built-in /insights label set). The count maps are
// constrained to these so the reduce stage sums clean buckets instead of the
// fragmented free-text keys an unconstrained schema invites.
const GOAL_KEYS = ['debug_investigate', 'implement_feature', 'fix_bug', 'write_script_tool', 'refactor_code', 'configure_system', 'create_pr_commit', 'analyze_data', 'understand_codebase', 'write_tests', 'write_docs', 'deploy_infra', 'warmup_minimal']
const SATISFACTION_KEYS = ['happy', 'satisfied', 'likely_satisfied', 'dissatisfied', 'frustrated']
const FRICTION_KEYS = ['misunderstood_request', 'wrong_approach', 'buggy_code', 'user_rejected_action', 'excessive_changes']

function countMap(keys) {
  const properties = {}
  for (const k of keys) properties[k] = { type: 'number' }
  return { type: 'object', additionalProperties: false, properties }
}

const SESSION_SCHEMA = {
  type: 'object',
  required: ['underlying_goal', 'outcome', 'brief_summary', 'goal_categories', 'user_satisfaction_counts', 'friction_counts'],
  additionalProperties: false,
  properties: {
    underlying_goal: { type: 'string', description: 'What the user was actually trying to accomplish this session' },
    outcome: { type: 'string', description: 'achieved | partially_achieved | not_achieved, plus a few words' },
    brief_summary: { type: 'string', description: '1-3 sentences: what was asked, what Claude did, any friction, the result' },
    goal_categories: countMap(GOAL_KEYS),
    user_satisfaction_counts: countMap(SATISFACTION_KEYS),
    friction_counts: countMap(FRICTION_KEYS),
  },
}

const AREAS_SCHEMA = {
  type: 'object', required: ['areas'], additionalProperties: false,
  properties: { areas: { type: 'array', items: {
    type: 'object', required: ['name', 'session_count', 'description'], additionalProperties: false,
    properties: { name: { type: 'string' }, session_count: { type: 'number' }, description: { type: 'string' } },
  } } },
}

const STYLE_SCHEMA = {
  type: 'object', required: ['narrative', 'key_pattern'], additionalProperties: false,
  properties: { narrative: { type: 'string' }, key_pattern: { type: 'string' } },
}

const WORKS_SCHEMA = {
  type: 'object', required: ['intro', 'impressive_workflows'], additionalProperties: false,
  properties: { intro: { type: 'string' }, impressive_workflows: { type: 'array', items: {
    type: 'object', required: ['title', 'description'], additionalProperties: false,
    properties: { title: { type: 'string' }, description: { type: 'string' } },
  } } },
}

const FRICTION_SCHEMA = {
  type: 'object', required: ['intro', 'categories'], additionalProperties: false,
  properties: { intro: { type: 'string' }, categories: { type: 'array', items: {
    type: 'object', required: ['category', 'description', 'examples'], additionalProperties: false,
    properties: { category: { type: 'string' }, description: { type: 'string' }, examples: { type: 'array', items: { type: 'string' } } },
  } } },
}

const SUGGEST_SCHEMA = {
  type: 'object', required: ['claude_md_additions', 'features_to_try', 'usage_patterns'], additionalProperties: false,
  properties: {
    claude_md_additions: { type: 'array', items: {
      type: 'object', required: ['addition', 'why', 'prompt_scaffold'], additionalProperties: false,
      properties: { addition: { type: 'string' }, why: { type: 'string' }, prompt_scaffold: { type: 'string' } },
    } },
    features_to_try: { type: 'array', items: {
      type: 'object', required: ['feature', 'one_liner', 'why_for_you', 'example_code'], additionalProperties: false,
      properties: { feature: { type: 'string' }, one_liner: { type: 'string' }, why_for_you: { type: 'string' }, example_code: { type: 'string' } },
    } },
    usage_patterns: { type: 'array', items: {
      type: 'object', required: ['title', 'suggestion', 'detail', 'copyable_prompt'], additionalProperties: false,
      properties: { title: { type: 'string' }, suggestion: { type: 'string' }, detail: { type: 'string' }, copyable_prompt: { type: 'string' } },
    } },
  },
}

const HORIZON_SCHEMA = {
  type: 'object', required: ['intro', 'opportunities'], additionalProperties: false,
  properties: { intro: { type: 'string' }, opportunities: { type: 'array', items: {
    type: 'object', required: ['title', 'whats_possible', 'how_to_try', 'copyable_prompt'], additionalProperties: false,
    properties: { title: { type: 'string' }, whats_possible: { type: 'string' }, how_to_try: { type: 'string' }, copyable_prompt: { type: 'string' } },
  } } },
}

const FUN_SCHEMA = {
  type: 'object', required: ['headline', 'detail'], additionalProperties: false,
  properties: { headline: { type: 'string' }, detail: { type: 'string' } },
}

const GLANCE_SCHEMA = {
  type: 'object', required: ['whats_working', 'whats_hindering', 'quick_wins', 'ambitious_workflows'], additionalProperties: false,
  properties: { whats_working: { type: 'string' }, whats_hindering: { type: 'string' }, quick_wins: { type: 'string' }, ambitious_workflows: { type: 'string' } },
}

// ---- Stage 1: Map (one cheap agent per transcript) -----------------------

const MAP_GUIDE = `Analyze this Claude Code session transcript and extract structured facets.
CRITICAL GUIDELINES:
1. **goal_categories**: Count ONLY what the USER explicitly asked for.
   - DO NOT count Claude's autonomous codebase exploration
   - DO NOT count work Claude decided to do on its own
   - ONLY count when user says "can you...", "please...", "I need...", "let's..."
   - Use ONLY these keys (no others): debug_investigate, implement_feature, fix_bug,
     write_script_tool, refactor_code, configure_system, create_pr_commit, analyze_data,
     understand_codebase, write_tests, write_docs, deploy_infra, warmup_minimal
   - For user_satisfaction_counts use ONLY: happy, satisfied, likely_satisfied, dissatisfied, frustrated
   - For friction_counts use ONLY: misunderstood_request, wrong_approach, buggy_code, user_rejected_action, excessive_changes
2. **user_satisfaction_counts**: Base ONLY on explicit user signals.
   - "Yay!", "great!", "perfect!" -> happy
   - "thanks", "looks good", "that works" -> satisfied
   - "ok, now let's..." (continuing without complaint) -> likely_satisfied
   - "that's not right", "try again" -> dissatisfied
   - "this is broken", "I give up" -> frustrated
3. **friction_counts**: Be specific. Keys:
   - misunderstood_request: Claude interpreted incorrectly
   - wrong_approach: Right goal, wrong solution method
   - buggy_code: Code didn't work correctly
   - user_rejected_action: User said no/stop to a tool call
   - excessive_changes: Over-engineered or changed too much
4. If very short or just a cache warmup, use warmup_minimal as the only goal_category.`

phase('Map')
const mapped = (await parallel(files.map((path, i) => () =>
  agent(
    `${MAP_GUIDE}\n\nThe session transcript is a JSONL file (one event per line) at:\n${path}\n\n` +
    `Read it with the Read tool. If it is very large, sample the first ~400 lines, a middle slice, ` +
    `and the last ~200 lines rather than reading the whole thing. Then return the facets.`,
    { label: `map:${i}`, phase: 'Map', model: 'haiku', effort: 'low', schema: SESSION_SCHEMA },
  ).then((r) => (r ? { ...r, __path: path } : null)),
))).filter(Boolean)

// ---- Reduce (pure JS) ----------------------------------------------------

function mergeCounts(target, src) {
  if (!src || typeof src !== 'object') return
  for (const k of Object.keys(src)) target[k] = (target[k] || 0) + (Number(src[k]) || 0)
}
function onlyWarmup(gc) {
  if (!gc) return false
  const active = Object.keys(gc).filter((k) => (Number(gc[k]) || 0) > 0)
  return active.length === 1 && active[0] === 'warmup_minimal'
}

const realSessions = mapped.filter((s) => !onlyWarmup(s.goal_categories))
const droppedPaths = mapped.filter((s) => onlyWarmup(s.goal_categories)).map((s) => s.__path)
const totals = { goal: {}, satisfaction: {}, friction: {} }
const summaries = []
for (const s of realSessions) {
  mergeCounts(totals.goal, s.goal_categories)
  mergeCounts(totals.satisfaction, s.user_satisfaction_counts)
  mergeCounts(totals.friction, s.friction_counts)
  summaries.push(`- (${s.outcome}) goal: ${s.underlying_goal} — ${s.brief_summary}`)
}

log(`Mapped ${mapped.length} sessions, ${realSessions.length} after dropping ${droppedPaths.length} warmup-only`)
if (droppedPaths.length) log(`Dropped (warmup-only): ${droppedPaths.map((p) => String(p).split('/').pop()).join(', ')}`)

function countsBlock(title, m) {
  const entries = Object.entries(m).sort((a, b) => b[1] - a[1])
  return `## ${title}\n` + (entries.length ? entries.map(([k, v]) => `${k}: ${v}`).join('\n') : '(none)')
}

const usageData = [
  `## Project: ${projectName}`,
  `## Sessions analyzed: ${realSessions.length}`,
  countsBlock('Goal categories (counts)', totals.goal),
  countsBlock('User satisfaction (counts)', totals.satisfaction),
  countsBlock('Friction (counts)', totals.friction),
  `## Session summaries:\n${summaries.join('\n')}`,
].join('\n\n')

// ---- Stage 2: aggregate facet prompts (verbatim from the built-in) -------

const FEATURES_REF = [
  '## CC FEATURES REFERENCE (pick from these for features_to_try):',
  '1. **MCP Servers**: Connect Claude to external tools, databases, and APIs via Model Context Protocol.',
  '   - How to use: Run \\`claude mcp add <server-name> -- <command>\\`',
  '   - Good for: database queries, Slack integration, GitHub issue lookup, connecting to internal APIs',
  '2. **Custom Skills**: Reusable prompts you define as markdown files that run with a single /command.',
  '   - How to use: Create \\`.claude/skills/commit/SKILL.md\\` with instructions. Then type \\`/commit\\` to run it.',
  '   - Good for: repetitive workflows - /commit, /review, /test, /deploy, /pr, or complex multi-step workflows',
  '3. **Hooks**: Shell commands that auto-run at specific lifecycle events.',
  '   - How to use: Add to \\`.claude/settings.json\\` under "hooks" key.',
  '   - Good for: auto-formatting code, running type checks, enforcing conventions',
  '4. **Headless Mode**: Run Claude non-interactively from scripts and CI/CD.',
  '   - How to use: \\`claude -p "fix lint errors" --allowedTools "Edit,Read,Bash"\\`',
  '   - Good for: CI/CD integration, batch code fixes, automated reviews',
  '5. **Task Agents**: Claude spawns focused subagents for complex exploration or parallel work.',
  '   - How to use: Claude auto-invokes when helpful, or ask "use an agent to explore X"',
  '   - Good for: codebase exploration, understanding complex systems',
].join('\n')

const FACETS = [
  { key: 'project_areas', schema: AREAS_SCHEMA, prompt:
    `Analyze this Claude Code usage data and identify project areas. Include 4-5 areas. Skip internal CC operations. For each: a name, the session_count, and a 2-3 sentence description of what was worked on and how Claude Code was used.` },
  { key: 'interaction_style', schema: STYLE_SCHEMA, prompt:
    `Analyze this Claude Code usage data and describe the user's interaction style. Write a 2-3 paragraph narrative analyzing HOW the user interacts with Claude Code. Use second person "you". Describe patterns: iterate quickly vs detailed upfront specs? Interrupt often or let Claude run? Include specific examples. Use **bold** for key insights. Then give a one-sentence key_pattern summarizing the most distinctive interaction style.` },
  { key: 'what_works', schema: WORKS_SCHEMA, prompt:
    `Analyze this Claude Code usage data and identify what's working well for this user. Use second person ("you"). Give a 1-sentence intro, then 3 impressive_workflows, each with a short title (3-6 words) and a 2-3 sentence description.` },
  { key: 'friction_analysis', schema: FRICTION_SCHEMA, prompt:
    `Analyze this Claude Code usage data and identify friction points for this user. Use second person ("you"). Give a 1-sentence intro summarizing friction patterns, then 3 categories, each with a concrete category name, a 1-2 sentence description of what could be done differently, and 2 specific examples (each naming a consequence).` },
  { key: 'suggestions', schema: SUGGEST_SCHEMA, prompt:
    `Analyze this Claude Code usage data and suggest improvements.\n${FEATURES_REF}\n\nProduce three lists:\n- claude_md_additions: specific lines/blocks to add to CLAUDE.md based on workflow patterns, each with why (1 sentence) and prompt_scaffold (where to add it). PRIORITIZE instructions that appear MULTIPLE TIMES in the data — if the user told Claude the same thing in 2+ sessions, that's a PRIME candidate.\n- features_to_try: pick 2-3 from the CC FEATURES REFERENCE above, each with one_liner, why_for_you (based on the sessions), and example_code to copy.\n- usage_patterns: 2-3 items, each with a short title, a 1-2 sentence suggestion, a 3-4 sentence detail tied to the user's work, and a copyable_prompt to try.` },
  { key: 'on_the_horizon', schema: HORIZON_SCHEMA, prompt:
    `Analyze this Claude Code usage data and identify future opportunities. Give a 1-sentence intro about evolving AI-assisted development, then 3 opportunities. Think BIG — autonomous workflows, parallel agents, iterating against tests. Each opportunity: a short title (4-8 words), whats_possible (2-3 ambitious sentences), how_to_try (1-2 sentences mentioning relevant tooling), and a detailed copyable_prompt.` },
  { key: 'fun_ending', schema: FUN_SCHEMA, prompt:
    `Analyze this Claude Code usage data and find a memorable moment. Return a headline describing a memorable QUALITATIVE moment from the sessions — not a statistic — something human, funny, or surprising, plus a detail giving brief context about when/where it happened.` },
]

phase('Facets')
const facetResults = await parallel(FACETS.map((fd) => () =>
  agent(`${fd.prompt}\n\nUSAGE DATA:\n${usageData}`, { label: fd.key, phase: 'Facets', model: 'haiku', schema: fd.schema })
    .then((r) => ({ key: fd.key, value: r })),
))

const facets = {}
for (const r of facetResults) if (r && r.value) facets[r.key] = r.value

// at_a_glance runs last, consuming the other facets
function facetDigest(f) {
  const parts = []
  if (f.project_areas) parts.push('## Project Areas\n' + (f.project_areas.areas || []).map((a) => `- ${a.name} (${a.session_count}): ${a.description}`).join('\n'))
  if (f.what_works) parts.push('## Big Wins\n' + (f.what_works.impressive_workflows || []).map((w) => `- ${w.title}: ${w.description}`).join('\n'))
  if (f.friction_analysis) parts.push('## Friction Categories\n' + (f.friction_analysis.categories || []).map((c) => `- ${c.category}: ${c.description}`).join('\n'))
  if (f.suggestions) parts.push('## Features to Try\n' + (f.suggestions.features_to_try || []).map((x) => `- ${x.feature}: ${x.why_for_you}`).join('\n'))
  if (f.suggestions) parts.push('## Usage Patterns to Adopt\n' + (f.suggestions.usage_patterns || []).map((x) => `- ${x.title}: ${x.suggestion}`).join('\n'))
  if (f.on_the_horizon) parts.push('## On the Horizon\n' + (f.on_the_horizon.opportunities || []).map((o) => `- ${o.title}: ${o.whats_possible}`).join('\n'))
  return parts.join('\n\n')
}

const GLANCE_PROMPT =
  `You're writing an "At a Glance" summary for a Claude Code usage insights report. The goal is to help the user understand their usage and improve how they use Claude, especially as models improve. Use this 4-part structure:\n` +
  `1. **What's working** - the user's unique style of interacting with Claude and a couple of impactful things they've done. Keep it high level; don't be fluffy; don't focus on tool calls.\n` +
  `2. **What's hindering you** - split into (a) Claude's fault (misunderstandings, wrong approaches, bugs) and (b) user-side friction (not enough context, environment issues — more general than one project). Honest but constructive.\n` +
  `3. **Quick wins to try** - specific Claude Code features or a compelling workflow technique. Avoid generic advice like "ask Claude to confirm before acting" or "type out more context".\n` +
  `4. **Ambitious workflows for better models** - as models get much more capable over the next 3-6 months, what should they prepare for? What seems impossible now but will become possible?\n` +
  `Keep each section to 2-3 sentences. Don't overwhelm. Don't cite numeric stats. Coaching tone.`

phase('Facets')
const glance = await agent(`${GLANCE_PROMPT}\n\nSESSION DATA:\n${facetDigest(facets)}`, { label: 'at_a_glance', phase: 'Facets', model: 'haiku', schema: GLANCE_SCHEMA })
facets.at_a_glance = glance

// ---- Render markdown (pure JS; orchestrator writes the file) -------------

function bullets(items, fn) { return (items || []).map(fn).join('\n') }
// Flatten a field to a single line (agent fields may contain newlines that would
// otherwise break inline markdown or leak '#' lines to column 0).
function oneline(s) { return String(s || '').replace(/\s*\n\s*/g, ' ').trim() }
// Fence agent-provided code/prompts so embedded markdown can't pollute structure.
// Tilde fence avoids collision with backticks inside the content.
function codeBlock(content) { return ['~~~~', String(content || '').replace(/~~~~/g, '~~~'), '~~~~'] }

function renderMarkdown() {
  const g = facets.at_a_glance || {}
  const pa = facets.project_areas || {}
  const is = facets.interaction_style || {}
  const ww = facets.what_works || {}
  const fa = facets.friction_analysis || {}
  const sg = facets.suggestions || {}
  const oh = facets.on_the_horizon || {}
  const fe = facets.fun_ending || {}
  const lines = []
  lines.push(`# Claude Code Insights: ${projectName}`)
  lines.push('')
  lines.push(`_${realSessions.length} sessions analyzed (of ${mapped.length} mapped)._`)
  lines.push('')
  lines.push('## At a Glance')
  lines.push('')
  lines.push(`**What's working:** ${g.whats_working || ''}`)
  lines.push('')
  lines.push(`**What's hindering you:** ${g.whats_hindering || ''}`)
  lines.push('')
  lines.push(`**Quick wins to try:** ${g.quick_wins || ''}`)
  lines.push('')
  lines.push(`**Ambitious workflows:** ${g.ambitious_workflows || ''}`)
  lines.push('')
  lines.push('## Project Areas')
  lines.push('')
  lines.push(bullets(pa.areas, (a) => `- **${a.name}** (${a.session_count} sessions) — ${a.description}`))
  lines.push('')
  lines.push('## Interaction Style')
  lines.push('')
  if (is.key_pattern) { lines.push(`> ${oneline(is.key_pattern)}`); lines.push('') }
  lines.push(is.narrative || '')
  lines.push('')
  lines.push('## What Works')
  lines.push('')
  if (ww.intro) { lines.push(ww.intro); lines.push('') }
  lines.push(bullets(ww.impressive_workflows, (w) => `- **${w.title}** — ${w.description}`))
  lines.push('')
  lines.push('## Where Things Go Wrong')
  lines.push('')
  if (fa.intro) { lines.push(fa.intro); lines.push('') }
  for (const c of fa.categories || []) {
    lines.push(`### ${c.category}`)
    lines.push(c.description || '')
    for (const ex of c.examples || []) lines.push(`- ${ex}`)
    lines.push('')
  }
  lines.push('## Suggestions')
  lines.push('')
  lines.push('### CLAUDE.md additions')
  lines.push('')
  for (const a of sg.claude_md_additions || []) {
    lines.push(`- **${oneline(a.addition)}**`)
    lines.push(`  - _Why:_ ${oneline(a.why)}`)
    lines.push(`  - _Where:_ ${oneline(a.prompt_scaffold)}`)
  }
  lines.push('')
  lines.push('### Features to try')
  lines.push('')
  for (const x of sg.features_to_try || []) {
    lines.push(`**${oneline(x.feature)}** — ${oneline(x.one_liner)}`)
    lines.push('')
    lines.push(`_Why for you:_ ${oneline(x.why_for_you)}`)
    lines.push('')
    lines.push(...codeBlock(x.example_code))
    lines.push('')
  }
  lines.push('### Usage patterns')
  lines.push('')
  for (const x of sg.usage_patterns || []) {
    lines.push(`**${oneline(x.title)}** — ${oneline(x.suggestion)}`)
    lines.push('')
    lines.push(oneline(x.detail))
    lines.push('')
    lines.push('_Try this prompt:_')
    lines.push(...codeBlock(x.copyable_prompt))
    lines.push('')
  }
  lines.push('## On the Horizon')
  lines.push('')
  if (oh.intro) { lines.push(oh.intro); lines.push('') }
  for (const o of oh.opportunities || []) {
    lines.push(`### ${oneline(o.title)}`)
    lines.push('')
    lines.push(o.whats_possible || '')
    lines.push('')
    if (o.how_to_try) { lines.push(`_How to try:_ ${oneline(o.how_to_try)}`); lines.push('') }
    if (o.copyable_prompt) { lines.push('_Prompt to try:_'); lines.push(...codeBlock(o.copyable_prompt)); lines.push('') }
  }
  lines.push('## One More Thing')
  lines.push('')
  lines.push(`**${fe.headline || ''}**`)
  lines.push('')
  lines.push(fe.detail || '')
  lines.push('')
  return lines.join('\n')
}

const markdown = renderMarkdown()
return { projectName, outPath, sessionCount: realSessions.length, mappedCount: mapped.length, totals, markdown }
