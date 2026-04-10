"""
Diverging Bar Chart — Behavioral Presence by Tool
--------------------------------------------------
Works with files that have separate Participant and Tool columns.

Expected format:
Participant | Tool    | Prompt / Query Revision | Note Construction | ...
1           | ChatGPT | 1                       | 0                 | ...
1           | Google  | 1                       | 0                 | ...

Steps to run:
1. Install: pip install matplotlib numpy pandas openpyxl
2. Put this script in the same folder as your Excel file
3. Update PRESENCE_FILE below if your filename differs
4. Run: python generate_diverging_bar.py
5. Output saved as diverging_bar_chart.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ── CONFIG ────────────────────────────────────────────────────────────────────
PRESENCE_FILE = 'Code_Presence_DedooseChartExport_xlsx.xlsx'
GPT_COLOR = '#534AB7'
GOO_COLOR = '#0F9B8E'
GRAY      = '#888780'
# ── END CONFIG ─────────────────────────────────────────────────────────────────


def main():
    df = pd.read_excel(PRESENCE_FILE)
    df.columns = [c.strip() for c in df.columns]

    # Identify participant and tool columns
    participant_col = df.columns[0]
    tool_col = df.columns[1]
    code_cols = [c for c in df.columns[2:]]

    df = df.rename(columns={participant_col: 'participant', tool_col: 'tool'})
    df['participant'] = df['participant'].astype(str)
    df['tool'] = df['tool'].astype(str).str.strip()

    # Convert code columns to numeric
    for col in code_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Friendly labels
    label_map = {
        'Prompt / Query Revision':        'Prompt revision',
        'Note Construction (Typing)':      'Note construction',
        'Copy\u2013Paste':                 'Copy-paste',
        'Integration / Editing of Notes':  'Note integration',
        'Pause / Hesitation':              'Pause / hesitation',
    }

    # Compute presence per participant per tool
    results = {}
    for col in code_cols:
        label = label_map.get(col, col)
        pivot = df.pivot_table(
            index='participant', columns='tool',
            values=col, aggfunc='sum').fillna(0)
        gpt_n = int((pivot.get('ChatGPT', pd.Series(dtype=float)) > 0).sum())
        goo_n = int((pivot.get('Google',  pd.Series(dtype=float)) > 0).sum())
        results[label] = (gpt_n, goo_n)

    # Sort: ChatGPT-dominant first, Google-dominant last
    sorted_results = sorted(results.items(), key=lambda x: -(x[1][0] - x[1][1]))
    behaviors = [b for b, _ in sorted_results]
    gpt_vals  = [v[0] for _, v in sorted_results]
    goo_vals  = [v[1] for _, v in sorted_results]
    N = 20

    # Draw
    y = np.arange(len(behaviors))
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.barh(y, [-v for v in gpt_vals], color=GPT_COLOR,
            alpha=0.85, height=0.55, zorder=3)
    ax.barh(y, goo_vals, color=GOO_COLOR,
            alpha=0.85, height=0.55, zorder=3)

    for i, v in enumerate(gpt_vals):
        if v > 0:
            ax.text(-v - 0.3, i, str(v), va='center', ha='right',
                    fontsize=9.5, color=GPT_COLOR, fontweight='bold')
    for i, v in enumerate(goo_vals):
        if v > 0:
            ax.text(v + 0.3, i, str(v), va='center', ha='left',
                    fontsize=9.5, color=GOO_COLOR, fontweight='bold')

    ax.axvline(0, color=GRAY, linewidth=0.8, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(behaviors, fontsize=11, color='#3d3d3a')
    ax.yaxis.set_tick_params(length=0)

    ticks = list(range(0, N + 2, 5))
    ax.set_xticks([-t for t in ticks] + ticks)
    ax.set_xticklabels([str(t) for t in ticks] + [str(t) for t in ticks],
                       fontsize=9, color=GRAY)
    ax.set_xlabel('Number of participants (n/20)', fontsize=10,
                  color=GRAY, labelpad=8)

    ax.text(-N/2, len(behaviors) + 0.2, 'ChatGPT', ha='center',
            fontsize=12, fontweight='bold', color=GPT_COLOR)
    ax.text( N/2, len(behaviors) + 0.2, 'Google',  ha='center',
            fontsize=12, fontweight='bold', color=GOO_COLOR)

    ax.axvline(-20, color=GPT_COLOR, linewidth=0.5, linestyle=':', alpha=0.4)
    ax.axvline( 20, color=GOO_COLOR, linewidth=0.5, linestyle=':', alpha=0.4)

    ax.grid(axis='x', color='#d3d1c7', linewidth=0.5, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#d3d1c7')
    ax.set_xlim(-N - 2, N + 2)
    ax.set_ylim(-0.6, len(behaviors) + 0.5)

    plt.title(
        'Behavioral presence by tool — learning sessions (n = 20 per condition)',
        fontsize=12, color='#3d3d3a', pad=14, loc='left')
    plt.tight_layout()

    out = 'diverging_bar_chart.png'
    plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    print('\nCounts:')
    for b, gpt, goo in zip(behaviors, gpt_vals, goo_vals):
        print(f'  {b}: ChatGPT={gpt}, Google={goo}')


if __name__ == '__main__':
    main()
    