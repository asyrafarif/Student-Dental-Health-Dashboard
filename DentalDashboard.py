import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib
import io

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
            "Last Updated": "2026-07-10",
            "Dentist Report": "Routine checkup completed. All teeth healthy.",
            "Dentist Name": "Dr. Emily Chen",
            "Visit Date": "2026-07-10"
        },
        {
            "Child Name": "Emma Johnson", 
            "Parent Contact": "emma.j@example.com", 
            "Condition Status": "Requires Attention", 
            "Last Brushed Check": "Needs Improvement", 
            "Needs Dentist Visit": "Yes",
            "Notes": "Small dark spot noticed on top right molar.", 
            "Last Updated": "2026-07-11",
            "Dentist Report": "Small cavity detected on molar. Recommend filling.",
            "Dentist Name": "Dr. Michael Rodriguez",
            "Visit Date": "2026-07-08"
        },
        {
            "Child Name": "Noah Garcia", 
            "Parent Contact": "noah.g@example.com", 
            "Condition Status": "Urgent Care Needed", 
            "Last Brushed Check": "Poor", 
            "Needs Dentist Visit": "Yes",
            "Notes": "Complaining of minor toothache when drinking cold water.", 
            "Last Updated": "2026-07-09",
            "Dentist Report": "Tooth sensitivity present. Suggests toothpaste for sensitivity and follow-up visit.",
            "Dentist Name": "Dr. Sarah Kim",
            "Visit Date": "2026-07-09"
        }
    ])

# 3. Simple Dentist Authentication (can be replaced with proper authentication)
def verify_dentist_password(password):
    """Simple password verification for dentist access (use proper authentication in production)"""
    DENTIST_PASSWORD_HASH = hashlib.sha256("DentistSecure123!".encode()).hexdigest()
    return hashlib.sha256(password.encode()).hexdigest() == DENTIST_PASSWORD_HASH

# 4. Process uploaded Excel file
def process_excel_file(uploaded_file):
    """Process the uploaded Excel file and add new patients to the database"""
    try:
        df_excel = pd.read_excel(uploaded_file)
        
        # Validate required column
        if "Child Name" not in df_excel.columns:
            st.error("❌ Excel file must contain a 'Child Name' column.")
            return None
        
        # Create new records for each child in the Excel file
        new_records = []
        existing_children = st.session_state.dental_data["Child Name"].unique().tolist()
        
        added_count = 0
        skipped_count = 0
        
        for idx, row in df_excel.iterrows():
            child_name = row.get("Child Name", "").strip()
            parent_contact = row.get("Parent Contact", "Not provided")
            
            if not child_name:
                skipped_count += 1
                continue
            
            # Check if child already exists
            if child_name in existing_children:
                skipped_count += 1
                continue
            
            new_record = {
                "Child Name": child_name,
                "Parent Contact": parent_contact,
                "Condition Status": "Pending",
                "Last Brushed Check": "Not assessed",
                "Needs Dentist Visit": "Pending",
                "Notes": "Imported from Excel file",
                "Last Updated": datetime.today().strftime('%Y-%m-%d'),
                "Dentist Report": "Awaiting dentist review",
                "Dentist Name": "Not yet assigned",
                "Visit Date": "N/A"
            }
            
            new_records.append(new_record)
            added_count += 1
        
        if new_records:
            new_df = pd.DataFrame(new_records)
            st.session_state.dental_data = pd.concat(
                [st.session_state.dental_data, new_df], 
                ignore_index=True
            )
        
        return {
            "added": added_count,
            "skipped": skipped_count,
            "total": len(df_excel)
        }
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        return None

# 5. App Title and Navigation
st.title("🦷 Children's Dental Health Dashboard")

# Create tabs for Dentist and Parent access
tab_dentist, tab_parent = st.tabs(["🏥 Dentist Portal", "👨‍👩‍👧 Parent Portal"])

# ==========================================
# DENTIST PORTAL (CONFIDENTIAL)
# ==========================================
with tab_dentist:
    st.header("🏥 Dentist's Confidential Portal")
    st.markdown("**This portal is for registered dentists only. All information here is confidential.**")
    st.write("---")
    
    # Dentist Authentication
    dentist_auth_container = st.container(border=True)
    with dentist_auth_container:
        st.subheader("🔐 Dentist Authentication")
        col_auth1, col_auth2 = st.columns([2, 1])
        
        with col_auth1:
            dentist_password = st.text_input(
                "Enter Dentist Password",
                type="password",
                key="dentist_pwd",
                placeholder="Enter your secure password"
            )
        
        with col_auth2:
            authenticate_btn = st.button("Authenticate", key="auth_btn")
        
        if authenticate_btn:
            if verify_dentist_password(dentist_password):
                st.session_state.dentist_authenticated = True
                st.success("✅ Authentication successful! Access granted.")
            else:
                st.session_state.dentist_authenticated = False
                st.error("❌ Invalid password. Access denied.")
    
    # Display dentist features only if authenticated
    if st.session_state.get('dentist_authenticated', False):
        st.write("---")
        
        # ========== EXCEL FILE UPLOAD SECTION ==========
        st.subheader("📤 Import Patient List from Excel")
        st.markdown("Upload an Excel file with patient names to add them to the system.")
        
        upload_container = st.container(border=True)
        with upload_container:
            col_upload1, col_upload2 = st.columns([3, 1])
            
            with col_upload1:
                uploaded_file = st.file_uploader(
                    "Choose an Excel file (.xlsx or .xls)",
                    type=["xlsx", "xls"],
                    key="excel_upload"
                )
            
            with col_upload2:
                if uploaded_file is not None:
                    if st.button("📥 Process File", key="process_btn"):
                        result = process_excel_file(uploaded_file)
                        if result:
                            st.success(
                                f"✅ File processed successfully!\n\n"
                                f"• Added: {result['added']} new patients\n"
                                f"• Skipped: {result['skipped']} (already exist or invalid)\n"
                                f"• Total rows: {result['total']}"
                            )
                            st.rerun()
            
            # Show template info
            st.info(
                "📋 **Excel File Format:**\n\n"
                "Your Excel file should have the following columns:\n"
                "- **Child Name** (required): Full name of the student\n"
                "- **Parent Contact** (optional): Parent email or phone\n\n"
                "Example:\n"
                "| Child Name | Parent Contact |\n"
                "|---|---|\n"
                "| Sophia Martinez | sophia.m@example.com |\n"
                "| James Wilson | james.w@example.com |"
            )
        
        st.write("---")
        
        # Two columns: Form on left, Dashboard on right
        col_dentist_form, col_dentist_dashboard = st.columns([1, 2], gap="large")
        
        # ========== DENTIST FORM ==========
        with col_dentist_form:
            st.subheader("📝 Submit Dental Report")
            
            with st.form(key="dentist_report_form", clear_on_submit=True):
                child_name = st.text_input("Student's Full Name*", placeholder="Search existing student...")
                
                # Provide a dropdown of existing children
                existing_children = st.session_state.dental_data["Child Name"].unique().tolist()
                selected_child = st.selectbox(
                    "Or select from existing records*",
                    options=[""] + existing_children,
                    key="select_child"
                )
                
                if selected_child:
                    child_name = selected_child
                
                dentist_name = st.text_input("Your Name (Dentist)*", placeholder="Dr. John Doe")
                visit_date = st.date_input("Visit Date*")
                
                condition = st.selectbox(
                    "Overall Dental Condition Assessment*",
                    options=["Healthy", "Requires Attention", "Urgent Care Needed"]
                )
                
                dentist_report = st.text_area(
                    "Detailed Dental Report*",
                    placeholder="Describe findings, treatments, recommendations, etc...",
                    height=150
                )
                
                brushing = st.select_slider(
                    "Observed Brushing Habits",
                    options=["Poor", "Needs Improvement", "Good", "Excellent"],
                    value="Good"
                )
                
                needs_followup = st.radio("Needs Follow-up Visit?", options=["No", "Yes"])
                
                submit_btn = st.form_submit_button(label="📤 Submit Dental Report")
            
            if submit_btn:
                if not child_name or not dentist_name or not dentist_report:
                    st.error("Please fill out all required fields (marked with *).")
                else:
                    df = st.session_state.dental_data
                    # Check if child exists
                    child_exists = df[df["Child Name"].str.lower() == child_name.strip().lower()]
                    
                    if not child_exists.empty:
                        # Update existing record with dentist report
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Condition Status"] = condition
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Last Brushed Check"] = brushing
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Dentist Report"] = dentist_report.strip()
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Dentist Name"] = dentist_name.strip()
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Visit Date"] = str(visit_date)
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Needs Dentist Visit"] = "Yes" if needs_followup == "Yes" else "No"
                        df.loc[df["Child Name"].str.lower() == child_name.strip().lower(), "Last Updated"] = datetime.today().strftime('%Y-%m-%d')
                        
                        st.session_state.dental_data = df
                        st.success(f"✅ Dental report updated for {child_name}!")
                    else:
                        st.warning(f"⚠️ No record found for '{child_name}'. Please import the patient first or contact administration.")
        
        # ========== DENTIST DASHBOARD ==========
        with col_dentist_dashboard:
            st.subheader("📊 All Patient Records (Confidential)")
            current_df = st.session_state.dental_data
            
            # KPI Cards
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            with kpi1:
                st.metric("Total Patients", len(current_df))
            
            with kpi2:
                urgent_count = len(current_df[current_df["Condition Status"] == "Urgent Care Needed"])
                st.metric("Urgent Cases", urgent_count, delta=f"{urgent_count} Critical", delta_color="inverse")
            
            with kpi3:
                followup_count = len(current_df[current_df["Needs Dentist Visit"] == "Yes"])
                st.metric("Follow-ups Needed", followup_count)
            
            with kpi4:
                healthy_count = len(current_df[current_df["Condition Status"] == "Healthy"])
                st.metric("Healthy", healthy_count)
            
            st.write("---")
            
            # Charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Condition Distribution")
                if not current_df.empty:
                    fig_condition = px.pie(
                        current_df,
                        names="Condition Status",
                        color="Condition Status",
                        color_discrete_map={
                            "Healthy": "#2ECC71",
                            "Requires Attention": "#F1C40F",
                            "Urgent Care Needed": "#E74C3C",
                            "Pending": "#95A5A6"
                        },
                        hole=0.4
                    )
                    fig_condition.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_condition, use_container_width=True)
            
            with chart_col2:
                st.subheader("Brushing Habits Overview")
                if not current_df.empty:
                    brushing_counts = current_df["Last Brushed Check"].value_counts().reset_index()
                    brushing_counts.columns = ["Brushing Behavior", "Count"]
                    
                    fig_brushing = px.bar(
                        brushing_counts,
                        x="Brushing Behavior",
                        y="Count",
                        color="Brushing Behavior",
                        category_orders={"Brushing Behavior": ["Poor", "Needs Improvement", "Good", "Excellent", "Not assessed"]}
                    )
                    fig_brushing.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_brushing, use_container_width=True)
            
            st.write("---")
            
            # Detailed Records Table
            st.subheader("📋 Detailed Patient Records")
            search_query = st.text_input("Filter by Child Name:", "")
            
            if search_query:
                filtered_df = current_df[current_df["Child Name"].str.contains(search_query, case=False, na=False)]
            else:
                filtered_df = current_df
            
            # Display all columns for dentist
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
    else:
        st.info("🔒 Please authenticate with your dentist credentials to access this portal.")

# ==========================================
# PARENT PORTAL (READ-ONLY ACCESS)
# ==========================================
with tab_parent:
    st.header("👨‍👩‍👧 Parent Portal")
    st.markdown("Welcome parents! Enter your child's name to view their dental health records.")
    st.write("---")
    
    # ========== PARENT VIEW (READ-ONLY) ==========
    st.subheader("👶 Your Child's Dental Records")
    
    # Search for child's record
    search_name = st.text_input("Enter your child's name to view records:", "", key="parent_search")
    
    if search_name:
        current_df = st.session_state.dental_data
        matching_records = current_df[current_df["Child Name"].str.contains(search_name, case=False, na=False)]
        
        if not matching_records.empty:
            for idx, record in matching_records.iterrows():
                st.write("---")
                st.subheader(f"📄 {record['Child Name']}'s Record")
                
                # Display parent-friendly information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Overall Condition:** {record['Condition Status']}")
                    if record['Condition Status'] == "Healthy":
                        st.success("✅ Keep up the good work!")
                    elif record['Condition Status'] == "Requires Attention":
                        st.warning("⚠️ Please schedule a dental visit soon")
                    elif record['Condition Status'] == "Urgent Care Needed":
                        st.error("🚨 Urgent attention needed - Contact dentist immediately!")
                    else:
                        st.info("ℹ️ Assessment pending - your dentist will review soon")
                
                with col2:
                    st.write(f"**Brushing Habits:** {record['Last Brushed Check']}")
                    st.write(f"**Dentist Visit Needed:** {record['Needs Dentist Visit']}")
                
                st.write("---")
                
                st.write(f"**Last Updated:** {record['Last Updated']}")
                
                # Dentist's Report (if available)
                if record['Dentist Report'] not in ["Pending dentist review", "Awaiting dentist review"]:
                    st.info("📋 **Latest Dentist Report:**")
                    st.write(f"{record['Dentist Report']}")
                    st.write(f"*By {record['Dentist Name']} on {record['Visit Date']}*")
                else:
                    st.info("ℹ️ Awaiting dentist's review and report.")
        
        else:
            st.warning(f"❌ No records found for '{search_name}'. Please contact your dentist's office for more information.")
    
    else:
        st.info("🔍 Enter your child's name above to view their dental records.")
