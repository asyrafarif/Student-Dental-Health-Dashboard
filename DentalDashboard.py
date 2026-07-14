import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Child Tooth Healthcare Tracker",
    page_icon="🦷",
    layout="wide"
)

# 2. Mock Initial Data (Simulating a database)
if 'dental_data' not in st.session_state:
    st.session_state.dental_data = pd.DataFrame([
        {
            "Child Name": "Liam Smith", 
            "Parent Contact": "liam.p@example.com", 
            "Condition Status": "Healthy", 
            "Last Brushed Check": "Excellent", 
            "Needs Dentist Visit": "No",
            "Notes": "No visible issues. Doing well!", 
            "Last Updated": "2026-07-10"
        },
        {
            "Child Name": "Emma Johnson", 
            "Parent Contact": "emma.j@example.com", 
            "Condition Status": "Requires Attention", 
            "Last Brushed Check": "Needs Improvement", 
            "Needs Dentist Visit": "Yes",
            "Notes": "Small dark spot noticed on top right molar.", 
            "Last Updated": "2026-07-11"
        },
        {
            "Child Name": "Noah Garcia", 
            "Parent Contact": "noah.g@example.com", 
            "Condition Status": "Urgent Care Needed", 
            "Last Brushed Check": "Poor", 
            "Needs Dentist Visit": "Yes",
            "Notes": "Complaining of minor toothache when drinking cold water.", 
            "Last Updated": "2026-07-09"
        }
    ])

# Title and App Intro
st.title("🦷 Children's Dental Health Live Dashboard")
st.markdown("""
Welcome to the School Dental Tracker! This application allows parents to easily update their 
child's oral health status, enabling quick actions and timely dental visits.
""")
st.write("---")

# Layout: Form on the Left Side, Dashboard Reports on the Right Side
col1, col2 = st.columns([1, 2], gap="large")

# ==========================================
# COLUMN 1: PARENT UPDATE PORTAL
# ==========================================
with col1:
    st.header("📋 Parent Update Portal")
    st.subheader("Submit or Update Student Status")
    
    with st.form(key="parent_submission_form", clear_on_submit=True):
        child_name = st.text_input("Student's Full Name*", placeholder="e.g., Sophia Martinez")
        parent_email = st.text_input("Parent Contact Email*", placeholder="name@example.com")
        
        condition = st.selectbox(
            "Overall Mouth/Tooth Condition*",
            options=["Healthy", "Requires Attention", "Urgent Care Needed"]
        )
        
        brushing = st.select_slider(
            "Recent Routine Brushing Behavior",
            options=["Poor", "Needs Improvement", "Good", "Excellent"],
            value="Good"
        )
        
        dentist_needed = st.radio("Does your child need a dentist visit?", options=["No", "Yes"])
        
        notes = st.text_area("Additional Observations/Notes", placeholder="Describe any pain, discoloration, or loose teeth...")
        
        submit_button = st.form_submit_button(label="🚀 Update Child Status")
        
    if submit_button:
        if not child_name or not parent_email:
            st.error("Please fill out both the Student Name and Parent Contact fields.")
        else:
            # Create a dictionary for the new entry
            new_report = {
                "Child Name": child_name.strip(),
                "Parent Contact": parent_email.strip(),
                "Condition Status": condition,
                "Last Brushed Check": brushing,
                "Needs Dentist Visit": dentist_needed,
                "Notes": notes.strip() if notes else "None",
                "Last Updated": datetime.today().strftime('%Y-%m-%d')
            }
            
            # Remove old record if child exists, then append new record
            df = st.session_state.dental_data
            df = df[df["Child Name"].str.lower() != child_name.strip().lower()]
            df = pd.concat([df, pd.DataFrame([new_report])], ignore_index=True)
            
            # Save back to state
            st.session_state.dental_data = df
            st.success(f"Success! Re-entered or updated record for {child_name}.")

# ==========================================
# COLUMN 2: LIVE REPORTING & CHARTS
# ==========================================
with col2:
    st.header("📊 Dental Health Status & Analytics")
    current_df = st.session_state.dental_data
    
    # Quick KPI Summary Cards
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Tracked Students", len(current_df))
    kpi1.caption("Total records submitted")
    
    urgent_count = len(current_df[current_df["Condition Status"] == "Urgent Care Needed"])
    kpi2.metric("Urgent Actions Required", urgent_count, delta=f"{urgent_count} Critical cases", delta_color="inverse")
    kpi2.caption("Needs immediate attention")
    
    dentist_count = len(current_df[current_df["Needs Dentist Visit"] == "Yes"])
    kpi3.metric("Dentist Visits Recommended", dentist_count)
    kpi3.caption("Bookings advised")
    
    st.write("---")
    
    # Data Visualization Section
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Condition Overview")
        if not current_df.empty:
            fig_condition = px.pie(
                current_df, 
                names="Condition Status", 
                color="Condition Status",
                color_discrete_map={
                    "Healthy": "#2ECC71", 
                    "Requires Attention": "#F1C40F", 
                    "Urgent Care Needed": "#E74C3C"
                },
                hole=0.4
            )
            fig_condition.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_condition, use_container_width=True)
        else:
            st.info("No charts to display yet.")
            
    with chart_col2:
        st.subheader("Brushing Routines")
        if not current_df.empty:
            brushing_counts = current_df["Last Brushed Check"].value_counts().reset_index()
            brushing_counts.columns = ["Brushing Behavior", "Count"]
            
            fig_brushing = px.bar(
                brushing_counts, 
                x="Brushing Behavior", 
                y="Count",
                color="Brushing Behavior",
                category_orders={"Brushing Behavior": ["Poor", "Needs Improvement", "Good", "Excellent"]}
            )
            fig_brushing.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_brushing, use_container_width=True)
            
    st.write("---")
    
    # Searchable Live Raw Data View
    st.subheader("🔍 Active Student Records")
    search_query = st.text_input("Filter records by Child's Name:", "")
    
    if search_query:
        filtered_df = current_df[current_df["Child Name"].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = current_df
        
    st.dataframe(
        filtered_df.style.map(
            lambda v: 'color:red; font-weight:bold;' if v == 'Urgent Care Needed' else (
                      'color:orange;' if v == 'Requires Attention' else (
                      'color:green;' if v == 'Healthy' else '')),
            subset=['Condition Status']
        ), 
        use_container_width=True,
        hide_index=True
    )