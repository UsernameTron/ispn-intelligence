#!/usr/bin/env python3
"""
Genesys QA Analytics - Dashboard Builder
Generates Obsidian-aesthetic HTML dashboards from analysis results.
"""

from typing import Dict, List
from datetime import datetime


def generate_dashboard(results: Dict) -> str:
    """
    Generate complete HTML dashboard from analysis results.
    
    Args:
        results: Output from GenesysQAAnalyzer.analyze()
    
    Returns:
        Complete HTML document string
    """
    
    meta = results['metadata']
    tiers = results['tier_distribution']
    agents = results['agents']
    categories = results['categories']
    evaluators = results['evaluators']
    questions = results['questions'][:10]  # Top 10 failing
    
    # Calculate tier percentages for donut chart
    total_agents = sum(tiers.values())
    tier_pcts = {k: (v / total_agents * 100) if total_agents > 0 else 0 for k, v in tiers.items()}
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QA Performance Dashboard | {meta['date_range'][0]} - {meta['date_range'][1]}</title>
    <style>
        :root {{
            --bg-primary: #09090b;
            --bg-secondary: #18181b;
            --bg-tertiary: #27272a;
            --border: #3f3f46;
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --success: #4ade80;
            --cyan: #22d3ee;
            --amber: #fbbf24;
            --error: #ef4444;
            --font-mono: 'SF Mono', 'Cascadia Code', 'Roboto Mono', monospace;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }}
        
        .header-title {{
            font-size: 1.75rem;
            font-weight: 600;
            letter-spacing: -0.02em;
        }}
        
        .header-meta {{
            text-align: right;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        
        .header-meta .mono {{
            font-family: var(--font-mono);
            color: var(--text-muted);
        }}
        
        /* Grid Layout */
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .grid-full {{
            grid-column: 1 / -1;
        }}
        
        .grid-2col {{
            grid-column: span 2;
        }}
        
        /* Cards */
        .card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .card-title {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }}
        
        .card-value {{
            font-family: var(--font-mono);
            font-size: 2rem;
            font-weight: 700;
        }}
        
        .card-subtitle {{
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        
        /* Metric Cards */
        .metric-row {{
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
        }}
        
        .metric-label {{
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }}
        
        .metric-value {{
            font-family: var(--font-mono);
            font-size: 1.5rem;
            font-weight: 700;
        }}
        
        /* Tier Colors */
        .tier-exemplary {{ color: var(--success); }}
        .tier-standard {{ color: var(--cyan); }}
        .tier-development {{ color: var(--amber); }}
        .tier-critical {{ color: var(--error); }}
        
        .bg-exemplary {{ background: rgba(74, 222, 128, 0.1); border-color: rgba(74, 222, 128, 0.3); }}
        .bg-standard {{ background: rgba(34, 211, 238, 0.1); border-color: rgba(34, 211, 238, 0.3); }}
        .bg-development {{ background: rgba(251, 191, 36, 0.1); border-color: rgba(251, 191, 36, 0.3); }}
        .bg-critical {{ background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); }}
        
        /* Tier Distribution */
        .tier-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
        }}
        
        .tier-box {{
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }}
        
        .tier-count {{
            font-family: var(--font-mono);
            font-size: 2rem;
            font-weight: 700;
        }}
        
        .tier-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }}
        
        /* Gap Bars */
        .gap-item {{
            margin-bottom: 1rem;
        }}
        
        .gap-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.25rem;
            font-size: 0.875rem;
        }}
        
        .gap-name {{
            color: var(--text-secondary);
        }}
        
        .gap-value {{
            font-family: var(--font-mono);
            color: var(--text-primary);
        }}
        
        .gap-bar {{
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .gap-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        .gap-fill.good {{ background: var(--success); }}
        .gap-fill.warning {{ background: var(--amber); }}
        .gap-fill.critical {{ background: var(--error); }}
        
        /* Agent Table */
        .table-container {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        
        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
        }}
        
        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            color: var(--text-secondary);
        }}
        
        tr:hover td {{
            background: var(--bg-tertiary);
        }}
        
        .mono {{
            font-family: var(--font-mono);
        }}
        
        .tier-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        /* Evaluator Status */
        .status-calibrated {{
            color: var(--success);
        }}
        
        .status-warning {{
            color: var(--amber);
        }}
        
        /* Section Headers */
        .section-header {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        
        /* Footer */
        .footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.75rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div>
                <h1 class="header-title">QA Performance Dashboard</h1>
                <p class="header-meta">Evaluation Period: <span class="mono">{meta['date_range'][0]}</span> to <span class="mono">{meta['date_range'][1]}</span></p>
            </div>
            <div class="header-meta">
                <div><span class="mono">{meta['evaluation_count']}</span> evaluations</div>
                <div><span class="mono">{meta['agent_count']}</span> agents</div>
                <div><span class="mono">{meta['evaluator_count']}</span> evaluators</div>
            </div>
        </header>
        
        <!-- Key Metrics Row -->
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label">Team Average</div>
                <div class="metric-value" style="color: {'var(--success)' if meta['team_average'] >= 80 else 'var(--amber)' if meta['team_average'] >= 65 else 'var(--error)'};">{meta['team_average']}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Evaluations</div>
                <div class="metric-value">{meta['evaluation_count']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Agents Evaluated</div>
                <div class="metric-value">{meta['agent_count']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Needing Coaching</div>
                <div class="metric-value tier-critical">{tiers.get('Critical', 0) + tiers.get('Development', 0)}</div>
            </div>
        </div>
        
        <!-- Main Grid -->
        <div class="grid">
            <!-- Tier Distribution -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Performance Tiers</span>
                </div>
                <div class="tier-grid">
                    <div class="tier-box bg-exemplary">
                        <div class="tier-count tier-exemplary">{tiers.get('Exemplary', 0)}</div>
                        <div class="tier-label">Exemplary</div>
                    </div>
                    <div class="tier-box bg-standard">
                        <div class="tier-count tier-standard">{tiers.get('Standard', 0)}</div>
                        <div class="tier-label">Standard</div>
                    </div>
                    <div class="tier-box bg-development">
                        <div class="tier-count tier-development">{tiers.get('Development', 0)}</div>
                        <div class="tier-label">Development</div>
                    </div>
                    <div class="tier-box bg-critical">
                        <div class="tier-count tier-critical">{tiers.get('Critical', 0)}</div>
                        <div class="tier-label">Critical</div>
                    </div>
                </div>
            </div>
            
            <!-- Category Gaps -->
            <div class="card grid-2col">
                <div class="card-header">
                    <span class="card-title">Category Gap Analysis</span>
                </div>
                {_generate_gap_bars(categories)}
            </div>
        </div>
        
        <!-- Agent Performance Table -->
        <div class="card grid-full">
            <div class="card-header">
                <span class="card-title">Agent Performance Rankings</span>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Agent</th>
                            <th>Score</th>
                            <th>Evals</th>
                            <th>Consistency</th>
                            <th>Tier</th>
                            <th>Top Failure</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_generate_agent_rows(agents)}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Two Column: Questions + Evaluators -->
        <div class="grid" style="margin-top: 1.5rem;">
            <!-- Top Failing Questions -->
            <div class="card grid-2col">
                <div class="card-header">
                    <span class="card-title">Top Failing Behaviors (Coaching Priorities)</span>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Question</th>
                                <th>Category</th>
                                <th>Fail Rate</th>
                                <th>Impact</th>
                            </tr>
                        </thead>
                        <tbody>
                            {_generate_question_rows(questions)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Evaluator Calibration -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Evaluator Calibration</span>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Evaluator</th>
                                <th>Avg</th>
                                <th>σ</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {_generate_evaluator_rows(evaluators)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <footer class="footer">
            Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | Genesys QA Analytics | ISPN iGLASS Tech Center
        </footer>
    </div>
</body>
</html>"""
    
    return html


def _generate_gap_bars(categories: List[Dict]) -> str:
    """Generate category gap bar HTML"""
    html = ""
    for cat in categories[:6]:  # Top 6 categories
        # Skip auto-fail categories
        if 'Auto-Fail' in cat['name']:
            continue
            
        gap = cat['gap_percentage']
        fill_class = 'good' if gap <= 10 else 'warning' if gap <= 20 else 'critical'
        fill_width = min(100, gap * 5)  # Scale for visibility
        
        html += f"""
        <div class="gap-item">
            <div class="gap-header">
                <span class="gap-name">{cat['name']}</span>
                <span class="gap-value">{gap}% gap</span>
            </div>
            <div class="gap-bar">
                <div class="gap-fill {fill_class}" style="width: {fill_width}%;"></div>
            </div>
        </div>
        """
    return html


def _generate_agent_rows(agents: List[Dict]) -> str:
    """Generate agent table rows HTML"""
    html = ""
    for agent in agents:
        tier = agent['tier']
        tier_class = f"tier-{tier.lower()}"
        bg_class = f"bg-{tier.lower()}"
        
        # Get top failure
        top_failure = ""
        if agent['failure_patterns']:
            top_q = list(agent['failure_patterns'].keys())[0]
            top_failure = f"{top_q[:30]}... ({agent['failure_patterns'][top_q]}%)"
        
        html += f"""
        <tr>
            <td>{agent['name']}</td>
            <td class="mono {tier_class}">{agent['avg_percentage']}%</td>
            <td class="mono">{agent['eval_count']}</td>
            <td class="mono">{agent['std_dev'] if agent['std_dev'] else '—'}</td>
            <td><span class="tier-badge {tier_class} {bg_class}">{tier}</span></td>
            <td style="color: var(--text-muted);">{top_failure if top_failure else '—'}</td>
        </tr>
        """
    return html


def _generate_question_rows(questions: List[Dict]) -> str:
    """Generate question table rows HTML"""
    html = ""
    for q in questions:
        if q['failure_rate'] == 0:
            continue
            
        html += f"""
        <tr>
            <td>{q['question_text'][:40]}{'...' if len(q['question_text']) > 40 else ''}</td>
            <td style="color: var(--text-muted);">{q['group_name'][:15]}</td>
            <td class="mono" style="color: {'var(--error)' if q['failure_rate'] > 30 else 'var(--amber)' if q['failure_rate'] > 15 else 'var(--text-secondary)'};">{q['failure_rate']}%</td>
            <td class="mono">{q['points_lost']:.0f} pts</td>
        </tr>
        """
    return html


def _generate_evaluator_rows(evaluators: List[Dict]) -> str:
    """Generate evaluator table rows HTML"""
    html = ""
    for e in evaluators:
        status_class = 'status-calibrated' if e['status'] == 'Calibrated' else 'status-warning'
        
        html += f"""
        <tr>
            <td>{e['name']}</td>
            <td class="mono">{e['avg_score']}%</td>
            <td class="mono">{e['std_dev'] if e['std_dev'] else '—'}</td>
            <td class="{status_class}">{e['status']}</td>
        </tr>
        """
    return html


if __name__ == '__main__':
    # Test with sample data
    sample_results = {
        'metadata': {
            'date_range': ('2025-09-01', '2025-09-24'),
            'evaluation_count': 51,
            'agent_count': 26,
            'evaluator_count': 4,
            'team_average': 82.1
        },
        'tier_distribution': {
            'Exemplary': 8,
            'Standard': 10,
            'Development': 4,
            'Critical': 4
        },
        'agents': [],
        'categories': [],
        'evaluators': [],
        'questions': []
    }
    
    print(generate_dashboard(sample_results))
