import streamlit as st
import pandas as pd

st.set_page_config(page_title="Org Tree", layout="wide")
st.title("🌳 Organization Tree")

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df["DEPTH"] = df["DEPTH"].astype(int)
    df["ORGANIZATION_ID"] = df["ORGANIZATION_ID"].astype(str)
    df["ORGANIZATION_ID_PARENT"] = df["ORGANIZATION_ID_PARENT"].astype(str)
    df["ORGANIZATION_ID_PARENT"] = df["ORGANIZATION_ID_PARENT"].replace({"nan": "", "None": "", "0": ""})
    return df

uploaded_file = st.sidebar.file_uploader("Upload Org_H.csv", type=["csv"])
if not uploaded_file:
    st.info("👈 CSV upload karo")
    st.stop()

df = load_data(uploaded_file)
max_depth = st.sidebar.slider("Max Level", 1, int(df["DEPTH"].max()), 4)
df = df[df["DEPTH"] <= max_depth].sort_values("DEPTH")

# Build tree - Auto root detection
node_map = {row["ORGANIZATION_ID"]: row for _, row in df.iterrows()}
children = {}

# Root = DEPTH 1 OR parent not found in data
roots = []
for _, row in df.iterrows():
    pid = row["ORGANIZATION_ID_PARENT"]
    if pid == "" or pid not in node_map:
        roots.append(row["ORGANIZATION_ID"])
    else:
        children.setdefault(pid, []).append(row["ORGANIZATION_ID"])

def print_tree(node_id, prefix="", is_last=True):
    node = node_map[node_id]
    connector = "└── " if is_last else "├── "
    st.text(f"{prefix}{connector}{node['HIERARCHY']}")
    
    kids = children.get(node_id, [])
    new_prefix = prefix + ("    " if is_last else "│   ")
    for i, kid in enumerate(kids):
        print_tree(kid, new_prefix, i == len(kids) - 1)

st.subheader("Organization Structure")
if not roots:
    st.error("Root node nahi mila. CSV me DEPTH=1 wali row check karo.")
else:
    for i, root in enumerate(roots):
        print_tree(root, "", i == len(roots) - 1)
        
st.sidebar.caption(f"Total: {len(df)} departments | Roots: {len(roots)}")