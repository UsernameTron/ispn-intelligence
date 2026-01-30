#!/usr/bin/env python3
"""
ISPN Board Report Generator
Generates weekly and monthly reports in PPTX and DOCX formats
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from jinja2 import Template

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

from docx import Document
from docx.shared import Inches as DocxInches, Pt as DocxPt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from utils.thresholds import load_targets, get_status

# Paths
BASE_DIR = Path(__file__).parent.parent
METRICS_DIR = BASE_DIR / "data" / "metrics"
PARSED_DIR = BASE_DIR / "data" / "parsed"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"

# Colors
COLORS = {
    'GREEN': RgbColor(0x28, 0xA7, 0x45),
    'YELLOW': RgbColor(0xFF, 0xC1, 0x07),
    'RED': RgbColor(0xDC, 0x35, 0x45),
    'DARK': RgbColor(0x1A, 0x1A, 0x2E),
    'ACCENT': RgbColor(0x00, 0xD4, 0xFF)
}


def load_kpi_history():
    """Load KPI history from metrics file."""
    history_file = METRICS_DIR / "kpi_history.json"
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f)
    return {'periods': {}}


def get_latest_period(history: dict) -> tuple:
    """Get the most recent period and its data."""
    periods = history.get('periods', {})
    if not periods:
        return None, None
    
    latest = max(periods.keys())
    return latest, periods[latest]


def get_previous_period(history: dict, current: str) -> tuple:
    """Get the period before the current one."""
    periods = sorted(history.get('periods', {}).keys())
    if current in periods:
        idx = periods.index(current)
        if idx > 0:
            prev = periods[idx - 1]
            return prev, history['periods'][prev]
    return None, None


def calculate_deltas(current: dict, previous: dict) -> dict:
    """Calculate changes between periods."""
    if not previous:
        return {}
    
    deltas = {}
    current_kpis = current.get('kpis', {})
    prev_kpis = previous.get('kpis', {})
    
    for kpi, value in current_kpis.items():
        if kpi in prev_kpis and value is not None and prev_kpis[kpi] is not None:
            delta = value - prev_kpis[kpi]
            pct_change = (delta / prev_kpis[kpi] * 100) if prev_kpis[kpi] != 0 else 0
            deltas[kpi] = {
                'current': value,
                'previous': prev_kpis[kpi],
                'delta': delta,
                'pct_change': round(pct_change, 1)
            }
    
    return deltas


def generate_narrative(period: str, data: dict, deltas: dict, targets: dict) -> str:
    """Generate executive narrative for the report."""
    kpis = data.get('kpis', {})
    statuses = data.get('statuses', {})
    
    # Count by status
    status_counts = {'GREEN': 0, 'YELLOW': 0, 'RED': 0}
    for kpi, info in statuses.items():
        status = info.get('status', 'UNKNOWN')
        if status in status_counts:
            status_counts[status] += 1
    
    # Build narrative
    lines = []
    lines.append(f"# ISPN Tech Center Performance Report - {period}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    
    total = sum(status_counts.values())
    green_pct = (status_counts['GREEN'] / total * 100) if total > 0 else 0
    
    if status_counts['RED'] > 0:
        lines.append(f"**Overall Status: ATTENTION REQUIRED** - {status_counts['RED']} KPI(s) in RED status.")
    elif status_counts['YELLOW'] > 0:
        lines.append(f"**Overall Status: MONITORING** - {status_counts['YELLOW']} KPI(s) in YELLOW status.")
    else:
        lines.append(f"**Overall Status: ON TRACK** - All {total} KPIs meeting targets.")
    
    lines.append("")
    lines.append(f"- GREEN: {status_counts['GREEN']} ({green_pct:.0f}%)")
    lines.append(f"- YELLOW: {status_counts['YELLOW']}")
    lines.append(f"- RED: {status_counts['RED']}")
    lines.append("")

    lines.append("## KPI Details")
    lines.append("")
    
    kpi_names = {
        'aht': 'Average Handle Time',
        'awt': 'Average Wait Time', 
        'fcr': 'First Call Resolution',
        'escalation': 'Escalation Rate',
        'utilization': 'Utilization',
        'quality': 'Quality Score',
        'shrinkage': 'Shrinkage',
        'abandon': 'Abandon Rate',
        'calls_offered': 'Calls Offered',
        'headcount': 'Headcount'
    }
    
    for kpi, info in statuses.items():
        name = kpi_names.get(kpi, kpi.upper())
        value = info.get('value')
        target = info.get('target')
        status = info.get('status', 'UNKNOWN')
        
        delta_info = deltas.get(kpi, {})
        delta = delta_info.get('delta')
        
        line = f"- **{name}**: {value}"
        if target and target != 'N/A':
            line += f" (Target: {target})"
        if delta is not None:
            direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            line += f" {direction} {abs(delta):.1f}"
        line += f" [{status}]"
        
        lines.append(line)
    
    lines.append("")
    lines.append("---")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    return "\n".join(lines)


def create_pptx(period: str, data: dict, deltas: dict, output_path: Path):
    """Generate PowerPoint presentation."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Title slide
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Title
    title = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12), Inches(1.5))
    tf = title.text_frame
    p = tf.paragraphs[0]
    p.text = "ISPN Tech Center"
    p.font.size = Pt(44)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    subtitle = slide.shapes.add_textbox(Inches(0.5), Inches(4), Inches(12), Inches(1))
    tf = subtitle.text_frame
    p = tf.paragraphs[0]
    p.text = f"Performance Report - {period}"
    p.font.size = Pt(28)
    p.alignment = PP_ALIGN.CENTER
    
    # KPI Summary slide
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
    tf = title.text_frame
    p = tf.paragraphs[0]
    p.text = "KPI Summary"
    p.font.size = Pt(32)
    p.font.bold = True
    
    # KPI table
    kpis = data.get('kpis', {})
    statuses = data.get('statuses', {})
    
    kpi_names = {
        'aht': ('AHT', 'min'),
        'awt': ('AWT', 'sec'),
        'fcr': ('FCR', '%'),
        'escalation': ('Escalation', '%'),
        'utilization': ('Utilization', '%'),
        'quality': ('Quality', 'pts'),
        'shrinkage': ('Shrinkage', '%')
    }
    
    y_pos = 1.2
    for kpi, (name, unit) in kpi_names.items():
        if kpi in statuses:
            info = statuses[kpi]
            value = info.get('value', 'N/A')
            target = info.get('target', 'N/A')
            status = info.get('status', 'UNKNOWN')
            
            # KPI name
            box = slide.shapes.add_textbox(Inches(0.5), Inches(y_pos), Inches(3), Inches(0.5))
            tf = box.text_frame
            p = tf.paragraphs[0]
            p.text = name
            p.font.size = Pt(18)
            
            # Value
            box = slide.shapes.add_textbox(Inches(4), Inches(y_pos), Inches(2), Inches(0.5))
            tf = box.text_frame
            p = tf.paragraphs[0]
            p.text = f"{value} {unit}"
            p.font.size = Pt(18)
            p.font.bold = True
            
            # Status indicator
            color = COLORS.get(status, COLORS['DARK'])
            box = slide.shapes.add_textbox(Inches(7), Inches(y_pos), Inches(1.5), Inches(0.5))
            tf = box.text_frame
            p = tf.paragraphs[0]
            p.text = status
            p.font.size = Pt(16)
            p.font.color.rgb = color
            
            y_pos += 0.7
    
    prs.save(output_path)
    print(f"  Created: {output_path}")


def create_docx(period: str, narrative: str, output_path: Path):
    """Generate Word document."""
    doc = Document()
    
    # Title
    title = doc.add_heading('ISPN Tech Center Performance Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading(period, level=1)
    
    # Parse narrative and add content
    for line in narrative.split('\n'):
        if line.startswith('# '):
            continue  # Skip main title, we added it above
        elif line.startswith('## '):
            doc.add_heading(line[3:], level=2)
        elif line.startswith('- **'):
            # KPI line
            p = doc.add_paragraph(style='List Bullet')
            # Parse the bold portion
            parts = line[2:].split('**')
            if len(parts) >= 2:
                run = p.add_run(parts[1])
                run.bold = True
                p.add_run(parts[2] if len(parts) > 2 else '')
            else:
                p.add_run(line[2:])
        elif line.startswith('- '):
            doc.add_paragraph(line[2:], style='List Bullet')
        elif line.startswith('**'):
            p = doc.add_paragraph()
            parts = line.split('**')
            for i, part in enumerate(parts):
                if part:
                    run = p.add_run(part)
                    run.bold = (i % 2 == 1)
        elif line.startswith('*') and line.endswith('*'):
            p = doc.add_paragraph()
            run = p.add_run(line[1:-1])
            run.italic = True
        elif line.strip():
            doc.add_paragraph(line)
    
    doc.save(output_path)
    print(f"  Created: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='ISPN Board Report Generator')
    parser.add_argument('--period', choices=['weekly', 'monthly'], default='monthly',
                        help='Report period type')
    parser.add_argument('--month', type=str, help='Month (YYYY-MM) for monthly report')
    parser.add_argument('--week', type=str, help='Week (YYYY-Wxx) for weekly report')
    parser.add_argument('--format', choices=['pptx', 'docx', 'both'], default='both',
                        help='Output format')
    args = parser.parse_args()
    
    print("=" * 60)
    print("ISPN Board Report Generator")
    print("=" * 60)
    
    # Load data
    history = load_kpi_history()
    targets = load_targets()
    
    period, data = get_latest_period(history)
    if not period:
        print("\nNo KPI data found. Run ingest.py first.")
        return
    
    print(f"\nUsing data from period: {period}")
    
    # Get previous period for deltas
    prev_period, prev_data = get_previous_period(history, period)
    if prev_period:
        print(f"Comparing to previous: {prev_period}")
    
    # Calculate deltas
    deltas = calculate_deltas(data, prev_data) if prev_data else {}
    
    # Generate narrative
    narrative = generate_narrative(period, data, deltas, targets)
    
    # Create output directory
    if args.period == 'monthly':
        output_dir = REPORTS_DIR / "board" / period
    else:
        output_dir = REPORTS_DIR / "weekly" / (args.week or period)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate outputs
    print(f"\nGenerating reports in: {output_dir}")
    
    # Save narrative markdown
    md_path = output_dir / "narrative.md"
    with open(md_path, 'w') as f:
        f.write(narrative)
    print(f"  Created: {md_path}")
    
    if args.format in ['pptx', 'both']:
        pptx_path = output_dir / "board_report.pptx"
        create_pptx(period, data, deltas, pptx_path)
    
    if args.format in ['docx', 'both']:
        docx_path = output_dir / "board_report.docx"
        create_docx(period, narrative, docx_path)
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"\nReports saved to: {output_dir}")
    print("\nNext steps:")
    print("  1. Review generated reports")
    print("  2. git add . && git commit -m 'Add report'")
    print("  3. git push")


if __name__ == '__main__':
    main()
