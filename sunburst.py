#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MC2 · Fishing‑Cycle Sunburst (Enhanced v1.6.4)
- Bigger sunburst: 1200 × 700, centered
- Added dbg() prints for every major step to trace data reduction
"""

from pathlib import Path
import json, sys, warnings, webbrowser
import numpy as np, pandas as pd, networkx as nx
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, to_tree
import plotly.express as px

warnings.filterwarnings("ignore")

# ───────── 参数区 ─────────
DATA_FILE   = Path("data/mc2.json")
OUTPUT_HTML = "sunburst-11-enhanced-1-6-4.html"
FG_KIND     = "ecological preserve"
EP_KIND     = "ecological preserve"
MIN_PINGS   = 3
SAMPLE_CYCLES = None
COLOR_RANGE = [0, 0.4]

# Sunburst 尺寸
FIG_WIDTH  = 1200
FIG_HEIGHT = 700

dbg = lambda m: print(f"[DBG] {m}")

# 1. 读图 ---------------------------------------------------------------
if not DATA_FILE.exists():
    sys.exit(f"❌ {DATA_FILE} 不存在")
G = nx.node_link_graph(json.loads(DATA_FILE.read_text()),
                       directed=True, multigraph=True)
dbg(f"Nodes: {G.number_of_nodes():,}  Edges: {G.number_of_edges():,}")

nodes = (pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient="index")
         .reset_index().rename(columns={'index': 'id'}))
edges = pd.DataFrame([{'source': u, 'target': v, **d}
                      for u, v, k, d in G.edges(keys=True, data=True)])
edges['type'] = edges['type'].astype(str).str.strip()

# 2. 基础集合 -----------------------------------------------------------
vessel_ids = set(nodes.loc[nodes['type'].str.startswith('Entity.Vessel'), 'id'])
loc_meta = nodes[nodes['type'].str.startswith('Entity.Location')][
    ['id', 'kind', 'Name']]
loc_meta['kind'] = loc_meta['kind'].astype(str).str.lower().str.strip()
PORT_IDS = set(loc_meta.loc[loc_meta['kind'] == 'city', 'id'])
dbg(f"Ports(city): {len(PORT_IDS)}")

# SouthSeafood Express Corp vessels
SSE_VESSELS = set(nodes[
    (nodes['type'].str.startswith('Entity.Vessel')) &
    (nodes['company'].fillna("").str.contains("SouthSeafood Express Corp"))
]['id'])
dbg(f"SouthSeafood Express Corp vessels: {len(SSE_VESSELS)}")

# 3. 解析 Ping ----------------------------------------------------------
ping_raw = edges[edges['type'].str.contains("TransponderPing", case=False)]
def parse_ping(r):
    s, t = r['source'], r['target']
    if s in vessel_ids and t not in vessel_ids:  return s, t
    if t in vessel_ids and s not in vessel_ids:  return t, s
    return None, None

records = []
for _, r in ping_raw.iterrows():
    vid, lid = parse_ping(r)
    if vid:
        records.append([vid, lid,
                        pd.to_datetime(r['time'], errors='coerce'),
                        float(r.get('dwell', 0))])
pings = pd.DataFrame(records, columns=['vessel_id','location_id','time','dwell'])
dbg(f"Valid pings: {len(pings):,}")

# 4. 切分周期 -----------------------------------------------------------
def split_cycles(df):
    cycles, buf, in_trip = [], [], False
    for _, row in df.iterrows():
        is_port = row.location_id in PORT_IDS
        if not in_trip and not is_port: buf=[row]; in_trip=True
        elif in_trip and not is_port:  buf.append(row)
        elif in_trip and is_port:
            if len(buf) >= MIN_PINGS: cycles.append(pd.DataFrame(buf))
            in_trip=False; buf=[]
    return cycles

cycle_frames=[]
for vid, grp in pings.groupby('vessel_id', sort=False):
    for i, cyc in enumerate(split_cycles(grp.sort_values('time')),1):
        cyc['cycle_id']=f"{vid}_{i}"; cycle_frames.append(cyc)
if not cycle_frames:
    sys.exit("❌ 0 周期")

cycles_df = pd.concat(cycle_frames, ignore_index=True)
dbg(f"All cycles before sampling: {cycles_df.cycle_id.nunique():,}")

# —— 抽样 —— -----------------------------------------------------------
if SAMPLE_CYCLES and cycles_df.cycle_id.nunique() > SAMPLE_CYCLES:
    keep = np.random.choice(cycles_df.cycle_id.unique(),
                            SAMPLE_CYCLES, replace=False)
    cycles_df = cycles_df[cycles_df.cycle_id.isin(keep)]
    dbg(f"Cycles after random sampling to {SAMPLE_CYCLES}: "
        f"{cycles_df.cycle_id.nunique():,}")

# 5. 过滤阶段 -----------------------------------------------------------
# 5‑1 去掉没有 fishing‑ground 的周期
FG_IDS = set(loc_meta.loc[loc_meta['kind'] == 'fishing ground', 'id'])
before_fg = cycles_df.cycle_id.nunique()
has_fg = cycles_df.groupby('cycle_id')['location_id'] \
                  .apply(lambda col: col.isin(FG_IDS).any())
cycles_df = cycles_df[cycles_df.cycle_id.isin(has_fg[has_fg].index)].copy()
dbg(f"Cycles with fishing‑ground: {cycles_df.cycle_id.nunique():,} "
    f"(filtered {before_fg - cycles_df.cycle_id.nunique():,})")

# 5‑2 去掉没有 preserve 的周期
PRESERVE_IDS = set(loc_meta.loc[loc_meta['kind'] == 'ecological preserve', 'id'])
before_ep = cycles_df.cycle_id.nunique()
has_ep = cycles_df.groupby('cycle_id')['location_id'] \
                  .apply(lambda col: col.isin(PRESERVE_IDS).any())
cycles_df = cycles_df[cycles_df.cycle_id.isin(has_ep[has_ep].index)].copy()
dbg(f"Cycles with preserve: {cycles_df.cycle_id.nunique():,} "
    f"(filtered {before_ep - cycles_df.cycle_id.nunique():,})")

dbg(f"Final rows in cycles_df: {len(cycles_df):,}")

# 6. 特征矩阵 -----------------------------------------------------------
feat = (cycles_df.groupby(['cycle_id', 'location_id'])['dwell']
        .sum().reset_index()
        .merge(loc_meta, left_on='location_id', right_on='id', how='left')
        .pivot_table(index='cycle_id', columns='kind', values='dwell',
                     aggfunc='sum', fill_value=0))
dbg(f"Feature matrix shape: {feat.shape}")

feat['fg_ratio'] = feat.get(FG_KIND, 0) / feat.sum(axis=1)
feat['ep_ratio'] = feat.get(EP_KIND, 0) / feat.sum(axis=1)

feat['vessel_id'] = feat.index.str.split('_').str[0]
feat['is_sse'] = feat['vessel_id'].isin(SSE_VESSELS)
dbg(f"Distinct vessels in final cycles: {feat['vessel_id'].nunique():,}")

# 7. 风险船只 -----------------------------------------------------------
vessel_stats = (cycles_df.groupby('vessel_id')
                .apply(lambda g: pd.Series({
                    'ep_dwell': g[g['location_id'].isin(PRESERVE_IDS)]['dwell'].sum(),
                    'total_dwell': g['dwell'].sum()
                }), include_groups=False)
                .assign(ep_ratio=lambda x: x['ep_dwell'] / x['total_dwell'])
                .sort_values('ep_ratio', ascending=False))
dbg(f"Vessels after risk calc: {len(vessel_stats):,}")

# 8. 聚类 & Sunburst 数据 -----------------------------------------------
X = StandardScaler().fit_transform(feat.select_dtypes(float))
dbg("StandardScaler done.")
Z = linkage(X, method="ward")
dbg("Hierarchical clustering done.")

labels = feat.index.to_list()

def build(node):
    if node.left is None and node.right is None:
        idx = node.id
        return dict(name=labels[idx],
                    value=1,
                    weight=1,
                    color=float(feat.iloc[idx]['fg_ratio']),
                    ep=float(feat.iloc[idx]['ep_ratio']))
    left  = build(node.left)
    right = build(node.right)
    w_sum = left['weight'] + right['weight']
    return dict(children=[left, right],
                weight=w_sum,
                color=(left['color']*left['weight'] + right['color']*right['weight'])/w_sum,
                ep=(left['ep']*left['weight'] + right['ep']*right['weight'])/w_sum)

sun = build(to_tree(Z))
dbg("Sunburst hierarchy built.")

def flat(n, parent=""):
    nid = n.get('name') or f"cluster_{id(n)}"
    rows = [dict(id=nid, parent=parent,
                 value=n.get('value', 1),
                 color=n.get('color', np.nan),
                 ep=n.get('ep', np.nan))]
    for ch in n.get('children', []):
        rows += flat(ch, nid)
    return rows

flat_df = pd.DataFrame(flat(sun))
dbg(f"Flattened nodes for sunburst: {len(flat_df):,}")

# 9. cluster → cycles / vessels 映射 ------------------------------------
cycle_ids = set(cycles_df.cycle_id)
children_map = {}
for row in flat_df.itertuples():
    children_map.setdefault(row.parent, []).append(row.id)

def collect_leaves(node_id):
    leaves, stack = [], [node_id]
    while stack:
        n = stack.pop()
        if n in cycle_ids:
            leaves.append(n)
        stack.extend(children_map.get(n, []))
    return leaves

cluster_cycles = {}
cluster_vessels = {}
for node_id in flat_df['id']:
    if node_id in cycle_ids:
        continue
    leaves = collect_leaves(node_id)
    if leaves:
        cluster_cycles[node_id] = leaves
        cluster_vessels[node_id] = sorted({c.split('_')[0] for c in leaves})
dbg(f"Total non‑leaf clusters: {len(cluster_cycles):,}")

# ───────── HTML 构建辅助函数（同上一版） ─────────
def risky_table(stats):
    risky = stats[stats['ep_ratio'] > 0.2]
    rows = []
    for vid, row in risky.iterrows():
        is_sse = "Yes" if vid in SSE_VESSELS else "No"
        level  = "High" if row['ep_ratio'] >= 0.4 else "Medium"
        dot    = "#FF0000" if row['ep_ratio'] >= 0.4 else "#FFFF00"
        rows.append(
            f"<tr><td><span class='risk-dot' style='background-color:{dot};'></span>{level}</td>"
            f"<td>{vid}</td><td>{row['ep_ratio']:.4f}</td><td>{is_sse}</td></tr>")
    if not rows:
        return ""
    return ("<h3>Top Potentially Risky Vessels</h3>"
            "<table class='styled-table'><thead><tr><th>Risk</th><th>Vessel</th>"
            "<th>EP Ratio</th><th>SSE?</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")

def sse_info():
    sse_cycles = cycles_df[cycles_df['vessel_id'].isin(SSE_VESSELS)]['cycle_id'].nunique()
    lis = "".join(f"<li>{v}</li>" for v in sorted(SSE_VESSELS))
    return (f"<h3>SouthSeafood Express Corp Vessels</h3>"
            f"<p>Total SSE Vessels: {len(SSE_VESSELS)}</p>"
            f"<p>Cycles in visualization: {sse_cycles}</p>"
            f"<ul class='styled-list'>{lis}</ul>")

def sse_chains():
    parent_map = {row.id: row.parent for row in flat_df.itertuples()}
    def chain(cyc):
        ch, cur = [], cyc
        while cur:
            ch.append(cur)
            cur = parent_map.get(cur, "")
        return " → ".join(ch[::-1])
    html = "<h3>Cluster Lineages for SSE Vessels</h3>"
    for vid in sorted(SSE_VESSELS):
        cycles = cycles_df.loc[cycles_df['vessel_id'] == vid, 'cycle_id'].unique()
        if cycles.size == 0:
            continue
        html += (f"<h4>{vid}</h4><ul class='styled-list'>"
                 + "".join(f"<li>{chain(c)}</li>" for c in cycles) + "</ul>")
    return html

# 10. Sunburst ----------------------------------------------------------
fig = px.sunburst(
    flat_df,
    names="id", parents="parent", values="value",
    color='color', color_continuous_scale='RdYlBu_r',
    range_color=COLOR_RANGE,
    hover_data={'color':':.2f', 'ep':':.2f'}
)
fig.update_traces(textinfo='none')
fig.update_layout(
    title="Fishing Cycle Sunburst — Cluster Explorer",
    width=FIG_WIDTH, height=FIG_HEIGHT,
    margin=dict(t=50, l=0, r=0, b=0)
)
dbg("Plotly figure ready.")

# 11. 输出 HTML ---------------------------------------------------------
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Fishing Cycle Sunburst — Cluster Explorer</title>
<style>
body {{font-family: Arial, Helvetica, sans-serif;}}
.styled-table {{width:100%;max-width:800px;border-collapse:collapse;margin:20px 0;font-size:16px;
               box-shadow:0 0 20px rgba(0,0,0,0.1);}}
.styled-table thead tr {{background-color:#009879;color:#fff;text-align:left;}}
.styled-table th,.styled-table td {{padding:12px 15px;border-bottom:1px solid #ddd;}}
.styled-table tbody tr:nth-of-type(even) {{background:#f3f3f3;}}
.styled-table tbody tr:hover {{background:#f1f1f1;}}
.styled-list {{list-style:none;padding:0;margin:20px 0;max-width:800px;}}
.styled-list li {{padding:10px;margin-bottom:5px;background:#f9f9f9;border-left:5px solid #009879;border-radius:3px;}}
.risk-dot {{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:8px;vertical-align:middle;}}
#cluster-info {{margin:20px 0;max-width:800px;}}
#search-box  {{margin:20px 0;}}
#plotly-div {{margin:0 auto;}}
</style>
</head>
<body>
{fig.to_html(include_plotlyjs="inline", full_html=False, div_id='plotly-div')}
<div style="margin:20px;">
{sse_info()}
{sse_chains()}

<div id="cluster-info">
  <h3>Cluster Information</h3>
  <p>Type a cluster ID and click “Search” (or press Enter) to see its vessels and cycles.</p>
</div>

<div id="search-box">
  <input type="text" id="cluster-input" placeholder="Enter cluster ID (e.g., cluster_1234)" style="padding:6px;width:300px;">
  <button id="cluster-search" style="padding:6px 10px;">Search</button>
</div>

{risky_table(vessel_stats)}
</div>

<script>
const clusterCycles  = {json.dumps(cluster_cycles)};
const clusterVessels = {json.dumps(cluster_vessels)};
const infoDiv  = document.getElementById('cluster-info');
const inputBox = document.getElementById('cluster-input');
const searchBtn= document.getElementById('cluster-search');

function showCluster(id) {{
    if (!(id in clusterCycles)) {{
        infoDiv.innerHTML = `<p style="color:red;">Cluster “${{id}}” not found.</p>`;
        return;
    }}
    const cycles  = clusterCycles[id];
    const vessels = clusterVessels[id];
    let html = `<h4>Cluster: ${{id}}</h4>`;
    html += `<p><strong>Vessels (${{vessels.length}}):</strong> ${{vessels.join(', ')}}</p>`;
    html += `<details open><summary>Cycles (${{cycles.length}})</summary><ul>`;
    cycles.forEach(c => {{ html += `<li>${{c}}</li>`; }});
    html += `</ul></details>`;
    infoDiv.innerHTML = html;
}}

searchBtn.addEventListener('click', () => {{
    const id = inputBox.value.trim();
    if (id) showCluster(id);
}});
inputBox.addEventListener('keydown', (e) => {{
    if (e.key === 'Enter') {{
        e.preventDefault();
        const id = inputBox.value.trim();
        if (id) showCluster(id);
    }}
}});
</script>
</body>
</html>
"""

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

dbg(f"HTML written to {OUTPUT_HTML}")
webbrowser.open(OUTPUT_HTML)