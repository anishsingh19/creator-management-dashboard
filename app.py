import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Creator Dashboard", layout="wide")
st.title("🎬 Creator Campaign Dashboard")

# ============================================
# 1. SAMPLE DATA (Replace this later with Google Sheet)
# ============================================
@st.cache_data
def load_creators():
    """Load and clean creator data"""
    data = {
        'Creator_ID': [1, 2, 3, 4, 5],
        'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Lee', 'Diana Prince', 'Evan Dark'],
        'Platform': ['Instagram', 'YouTube', 'TikTok', 'Instagram', 'YouTube'],
        'Primary_Niche': ['Tech', 'Gaming', 'Fitness', 'Tech', 'Gaming'],
        'Secondary_Niche': ['AI', 'Streaming', 'Health', 'Web3', 'Esports'],
        'Followers': [50000, 100000, 75000, 120000, 95000],
        'Engagement_Rate_%': [5.2, 3.1, 6.8, 4.5, 3.9],
        'Contact_Email': ['alice@email.com', 'bob@email.com', 'charlie@email.com', 'diana@email.com', 'evan@email.com'],
        'Contact_Number': [9876543210, 9876543211, 9876543212, 9876543213, 9876543214],
        'City': ['Mumbai', 'Bangalore', 'Delhi', 'Mumbai', 'Hyderabad'],
        'Language': ['English', 'Hindi', 'English', 'English', 'Hindi'],
        'Cost_Per_Post': [5000, 8000, 3000, 7000, 6000]
    }
    return pd.DataFrame(data)

# Load data
creators_df = load_creators()

# ============================================
# 2. HELPER FUNCTIONS
# ============================================
def get_all_niches(df):
    """Get all unique niches from data"""
    niches = set(df['Primary_Niche'].dropna().unique())
    return sorted(list(niches))

def filter_creators_by_niche(df, selected_niches):
    """Filter creators by niche"""
    return df[df['Primary_Niche'].isin(selected_niches)]

def detect_incomplete_profiles(df):
    """Flag creators with missing data - AI FEATURE"""
    incomplete = []
    for idx, row in df.iterrows():
        missing_fields = []
        if pd.isna(row['Contact_Email']) or row['Contact_Email'] == '':
            missing_fields.append('Email')
        if pd.isna(row['Contact_Number']) or row['Contact_Number'] == '':
            missing_fields.append('Phone')
        if pd.isna(row['City']) or row['City'] == '':
            missing_fields.append('City')
        
        if missing_fields:
            incomplete.append({
                'Creator_ID': row['Creator_ID'],
                'Name': row['Name'],
                'Missing_Fields': ', '.join(missing_fields)
            })
    return pd.DataFrame(incomplete)

# ============================================
# 3. SIDEBAR - CAMPAIGN MODE
# ============================================
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio("Select Mode", ["Create Campaign", "View All Creators", "Data Quality Check"])

# ============================================
# 4. PAGE 1: CREATE CAMPAIGN
# ============================================
if page == "Create Campaign":
    st.subheader("Create New Campaign")
    
    col1, col2 = st.columns(2)
    with col1:
        campaign_code = st.text_input("Campaign Code (mandatory)", placeholder="e.g., CAMP_Q2_2026")
    with col2:
        campaign_name = st.text_input("Campaign Name (mandatory)", placeholder="e.g., Summer Gaming Collab")
    
    # Niche selection
    all_niches = get_all_niches(creators_df)
    selected_niches = st.multiselect(
        "Select Niches (mandatory)",
        all_niches,
        help="Choose one or more niches to filter creators"
    )
    
    if st.button("🚀 Create Campaign & Filter Creators", type="primary"):
        # Validation
        if not campaign_code:
            st.error("❌ Campaign Code is mandatory!")
        elif not campaign_name:
            st.error("❌ Campaign Name is mandatory!")
        elif not selected_niches:
            st.error("❌ Please select at least one niche!")
        else:
            st.success(f"✅ Campaign '{campaign_name}' created with code '{campaign_code}'")
            st.divider()
            
            # Filter creators
            filtered = filter_creators_by_niche(creators_df, selected_niches)
            st.subheader(f"📊 Found {len(filtered)} creators in {', '.join(selected_niches)}")
            
            # Classification section
            st.subheader("👥 Creator Classification")
            st.caption("Mark creators as Shortlisted, Backup, or Rejected")
            
            # Store classifications
            if 'classifications' not in st.session_state:
                st.session_state.classifications = {}
            
            for idx, row in filtered.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
                
                with col1:
                    st.write(f"**{row['Name']}**")
                    st.caption(f"{row['Platform']} | {row['Followers']:,} followers | ₹{row['Cost_Per_Post']:,}/post")
                
                with col2:
                    if st.checkbox("✅ Shortlist", key=f"short_{idx}"):
                        st.session_state.classifications[int(row['Creator_ID'])] = "Shortlisted"
                
                with col3:
                    if st.checkbox("⏸️ Backup", key=f"back_{idx}"):
                        st.session_state.classifications[int(row['Creator_ID'])] = "Backup"
                
                with col4:
                    if st.checkbox("❌ Reject", key=f"rej_{idx}"):
                        st.session_state.classifications[int(row['Creator_ID'])] = "Rejected"
                
                with col5:
                    st.caption(f"Email: {row['Contact_Email']}")
            
            # Show summary
            if st.session_state.classifications:
                st.divider()
                st.subheader("📈 Campaign Summary")
                
                summary_data = []
                for creator_id, status in st.session_state.classifications.items():
                    creator = creators_df[creators_df['Creator_ID'] == creator_id].iloc[0]
                    summary_data.append({
                        'Creator': creator['Name'],
                        'Status': status,
                        'Platform': creator['Platform'],
                        'Engagement %': creator['Engagement_Rate_%'],
                        'Cost/Post': f"₹{creator['Cost_Per_Post']}"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)

# ============================================
# PAGE 2: VIEW ALL CREATORS
# ============================================
elif page == "View All Creators":
    st.subheader("📊 All Creators Database")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        niche_filter = st.multiselect("Filter by Niche", get_all_niches(creators_df))
    with col2:
        platform_filter = st.multiselect("Filter by Platform", creators_df['Platform'].unique())
    
    # Apply filters
    filtered = creators_df.copy()
    if niche_filter:
        filtered = filtered[filtered['Primary_Niche'].isin(niche_filter)]
    if platform_filter:
        filtered = filtered[filtered['Platform'].isin(platform_filter)]
    
    st.write(f"Showing {len(filtered)} creators out of {len(creators_df)}")
    st.dataframe(filtered, use_container_width=True)

# ============================================
# PAGE 3: DATA QUALITY CHECK (AI FEATURE)
# ============================================
elif page == "Data Quality Check":
    st.subheader("🔍 Data Quality & Incomplete Profiles")
    
    incomplete = detect_incomplete_profiles(creators_df)
    
    if len(incomplete) > 0:
        st.warning(f"⚠️ Found {len(incomplete)} creators with incomplete profiles")
        st.dataframe(incomplete, use_container_width=True)
    else:
        st.success("✅ All creator profiles are complete!")
    
    # Data summary
    st.subheader("📋 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Creators", len(creators_df))
    col2.metric("Platforms", creators_df['Platform'].nunique())
    col3.metric("Niches", creators_df['Primary_Niche'].nunique())
    col4.metric("Avg Followers", f"{creators_df['Followers'].mean():.0f}")