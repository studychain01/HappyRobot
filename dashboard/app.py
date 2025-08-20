import os, requests, pandas as pd, streamlit as st

# Try local API first, fall back to remote if needed
API_BASE = os.getenv("API_BASE", "https://happyrobot-trucking-loadsapi.onrender.com")
API_KEY = os.getenv("API_KEY", "mysecret")

# Set page config with simple title
st.set_page_config(
    page_title="Dashboard",
    page_icon="🚛", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom header with branding
st.markdown("""
<div style="padding: 1rem 0; border-bottom: 2px solid #1f77b4; margin-bottom: 2rem;">
    <h1 style="margin: 0; color: #1f77b4;">🚛 HappyRobot Trucking Platform</h1>
    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 1.1rem;">Load Management & Customer Conversation Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📊 Loads Dashboard", "💬 Customer Conversations"])

with tab1:
    st.header("Inbound Loads Dashboard")
    
    st.caption(f"API_BASE={API_BASE}")
    try:
        resp = requests.get(f"{API_BASE}/loads", headers={"x-api-key": API_KEY}, timeout=15)
        if not resp.ok:
            st.error(f"Request failed: {resp.status_code} {resp.reason}")
            st.code(resp.text)
            data = []
        else:
            payload = resp.json()
            data = payload.get("results", [])
            st.success(f"Found {len(data)} loads")
    except Exception as e:
        st.exception(e)
        data = []

    df = pd.DataFrame(data)

    st.subheader("Available Loads")
    st.dataframe(df, use_container_width=True)
    
    # Booked Loads Section
    st.divider()
    st.subheader("Booked Loads")
    
    # For now, show placeholder - this will be populated when loads are booked
    booked_df = pd.DataFrame()  # Empty for now
    if booked_df.empty:
        st.info("No loads have been booked yet. Booked loads will appear here when customers confirm loads.")
    else:
        st.dataframe(booked_df, use_container_width=True)

    if not df.empty:
        st.subheader("Equipment mix")
        st.bar_chart(df["equipment_type"].value_counts())

        st.subheader("Avg miles by origin (top 10)")
        st.bar_chart(df.groupby("origin")["miles"].mean().sort_values(ascending=False).head(10))

    # Load Management Section
    st.divider()
    st.header("Load Management")

    # Initialize session state for form clearing
    if 'form_clear_trigger' not in st.session_state:
        st.session_state.form_clear_trigger = 0

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Add New Load")
        with st.form("add_load_form", clear_on_submit=True):
            load_id = st.text_input("Load ID*", placeholder="L-2001", key=f"load_id_{st.session_state.form_clear_trigger}")
            origin = st.text_input("Origin*", placeholder="Dallas, TX", key=f"origin_{st.session_state.form_clear_trigger}")
            destination = st.text_input("Destination*", placeholder="Los Angeles, CA", key=f"destination_{st.session_state.form_clear_trigger}")
            pickup_datetime = st.text_input("Pickup DateTime*", placeholder="2025-08-30T10:00:00Z", key=f"pickup_{st.session_state.form_clear_trigger}")
            delivery_datetime = st.text_input("Delivery DateTime*", placeholder="2025-08-31T16:00:00Z", key=f"delivery_{st.session_state.form_clear_trigger}")
            equipment_type = st.selectbox("Equipment Type*", ["Dry Van", "Reefer", "Flatbed", "Box Truck"], key=f"equipment_{st.session_state.form_clear_trigger}")
            loadboard_rate = st.number_input("Rate*", min_value=0, value=2000, key=f"rate_{st.session_state.form_clear_trigger}")
            notes = st.text_area("Notes", placeholder="Additional information", key=f"notes_{st.session_state.form_clear_trigger}")
            weight = st.number_input("Weight (lbs)", min_value=0, value=0, key=f"weight_{st.session_state.form_clear_trigger}")
            commodity_type = st.text_input("Commodity Type", placeholder="Electronics", key=f"commodity_{st.session_state.form_clear_trigger}")
            num_of_pieces = st.number_input("Number of Pieces", min_value=0, value=0, key=f"pieces_{st.session_state.form_clear_trigger}")
            miles = st.number_input("Miles", min_value=0, value=0, key=f"miles_{st.session_state.form_clear_trigger}")
            dimensions = st.text_input("Dimensions", placeholder="48x40 pallets", key=f"dimensions_{st.session_state.form_clear_trigger}")
            
            submitted = st.form_submit_button("Add Load")
            if submitted:
                if load_id and origin and destination and pickup_datetime and delivery_datetime:
                    new_load = {
                        "load_id": load_id,
                        "origin": origin,
                        "destination": destination,
                        "pickup_datetime": pickup_datetime,
                        "delivery_datetime": delivery_datetime,
                        "equipment_type": equipment_type,
                        "loadboard_rate": loadboard_rate,
                        "notes": notes if notes else None,
                        "weight": weight if weight > 0 else None,
                        "commodity_type": commodity_type if commodity_type else None,
                        "num_of_pieces": num_of_pieces if num_of_pieces > 0 else None,
                        "miles": miles if miles > 0 else None,
                        "dimensions": dimensions if dimensions else None
                    }
                    
                    try:
                        resp = requests.post(f"{API_BASE}/loads", 
                                           json=new_load, 
                                           headers={"x-api-key": API_KEY}, 
                                           timeout=15)
                        if resp.ok:
                            st.success(f"Load {load_id} added successfully!")
                            st.session_state.form_clear_trigger += 1  # Clear form by changing keys
                            st.rerun()
                        else:
                            st.error(f"Failed to add load: {resp.status_code} {resp.text}")
                    except Exception as e:
                        st.error(f"Error adding load: {str(e)}")
                else:
                    st.error("Please fill in all required fields (*)")

    with col2:
        st.subheader("Delete Load")
        with st.form("delete_load_form", clear_on_submit=True):
            delete_load_id = st.text_input("Load ID to Delete", placeholder="L-1001", key=f"delete_id_{st.session_state.form_clear_trigger}")
            
            delete_submitted = st.form_submit_button("Delete Load", type="secondary")
            if delete_submitted:
                if delete_load_id:
                    try:
                        resp = requests.delete(f"{API_BASE}/loads/{delete_load_id}", 
                                             headers={"x-api-key": API_KEY}, 
                                             timeout=15)
                        if resp.ok:
                            st.success(f"Load {delete_load_id} deleted successfully!")
                            st.session_state.form_clear_trigger += 1  # Clear form by changing keys
                            st.rerun()
                        elif resp.status_code == 404:
                            st.error(f"Load {delete_load_id} not found")
                        else:
                            st.error(f"Failed to delete load: {resp.status_code} {resp.text}")
                    except Exception as e:
                        st.error(f"Error deleting load: {str(e)}")
                else:
                    st.error("Please enter a Load ID to delete")

with tab2:
    st.header("💬 Customer Conversations")
    
    # Fetch conversations from API
    st.caption(f"API_BASE={API_BASE}")
    try:
        resp = requests.get(f"{API_BASE}/conversations", headers={"x-api-key": API_KEY}, timeout=15)
        if not resp.ok:
            st.error(f"Request failed: {resp.status_code} {resp.reason}")
            st.code(resp.text)
            conversations_data = []
        else:
            payload = resp.json()
            conversations_data = payload.get("results", [])
            st.success(f"Found {len(conversations_data)} conversations")
    except Exception as e:
        st.exception(e)
        conversations_data = []

    # Display conversations
    if conversations_data:
        # Filter options with better styling
        st.markdown("### 🔍 Filter & Search")
        col1, col2 = st.columns([1, 1])
        with col1:
            mc_number_search = st.text_input("🚛 Search by MC Number", placeholder="Enter MC number...")
        with col2:
            # Keep the load status filter
            status_filter = st.selectbox("📊 Load Status", ["All", "Booked", "Not Booked", "Unknown"])

        # Apply filters
        filtered_conversations = conversations_data.copy()
        
        # Apply MC number filter
        if mc_number_search:
            filtered_conversations = [c for c in filtered_conversations 
                                    if mc_number_search.lower() in str(c.get("mc_number", "")).lower()]
        
        # Apply status filter using agent notes
        if status_filter != "All":
            if status_filter == "Booked":
                filtered_conversations = [c for c in filtered_conversations 
                                        if c.get('agent_notes') and 'Load Status: Successful' in c.get('agent_notes', '')]
            elif status_filter == "Not Booked":
                filtered_conversations = [c for c in filtered_conversations 
                                        if c.get('agent_notes') and ('Load Status: Not' in c.get('agent_notes', '') or 'Load Status: Unsuccessful' in c.get('agent_notes', ''))]
            elif status_filter == "Unknown":
                filtered_conversations = [c for c in filtered_conversations 
                                        if not (c.get('agent_notes') and 'Load Status:' in c.get('agent_notes', ''))]

        # Show results count with better styling
        st.markdown(f"### 📋 Conversations ({len(filtered_conversations)} found)")
        st.divider()

        # Display conversation cards
        for conv in filtered_conversations:
            with st.expander("•"):
                # Create a more balanced 3-column layout
                col1, col2, col3 = st.columns([1.2, 1, 1])
                
                with col1:
                    # Conversation Content Section
                    st.markdown("**💬 Conversation Details**")
                    if conv.get('load_requirements'):
                        st.write("**Load Requirements:**")
                        st.write(conv.get('load_requirements'))
                    
                    if conv.get('agent_notes'):
                        st.write("**Agent Notes:**")
                        st.write(conv.get('agent_notes'))
                    
                    # Add timestamp at bottom of left column
                    if conv.get('timestamp'):
                        st.caption(f"🕐 {conv.get('timestamp')[:19].replace('T', ' ')}")
                
                with col2:
                    # Customer & Contact Information
                    st.markdown("**👤 Customer Info**")
                    if conv.get('customer_phone'):
                        st.write(f"📞 {conv.get('customer_phone')}")
                    if conv.get('customer_email'):
                        st.write(f"📧 {conv.get('customer_email')}")
                    if conv.get('mc_number'):
                        st.write(f"🚛 MC: {conv.get('mc_number')}")
                    
                    # Load booking status from agent notes
                    if conv.get('agent_notes') and 'Load Status:' in conv.get('agent_notes', ''):
                        if 'Load Status: Successful' in conv.get('agent_notes', ''):
                            st.success("✅ Load: BOOKED")
                        elif 'Load Status: Not' in conv.get('agent_notes', '') or 'Load Status: Unsuccessful' in conv.get('agent_notes', ''):
                            st.error("❌ Load: NOT BOOKED")
                    
                    # Follow-up information
                    if conv.get('follow_up_needed'):
                        st.warning("🔔 Follow-up Needed")
                        if conv.get('follow_up_date'):
                            st.write(f"📅 {conv.get('follow_up_date')}")
                
                with col3:
                    # Load & Route Details
                    st.markdown("**🚛 Load Details**")
                    
                    # Route information with better formatting
                    if conv.get('pickup_location') or conv.get('delivery_location'):
                        st.write("**📍 Route:**")
                        if conv.get('pickup_location'):
                            st.write(f"▶️ {conv.get('pickup_location')}")
                        if conv.get('delivery_location'):
                            st.write(f"🏁 {conv.get('delivery_location')}")
                    
                    if conv.get('equipment_needed'):
                        st.write(f"**🚛 Equipment:** {conv.get('equipment_needed')}")
                    
                    if conv.get('miles'):
                        st.write(f"**🛣️ Miles:** {conv.get('miles'):,}")
                    
                    if conv.get('rate_discussed'):
                        st.write(f"**💰 Rate:** ${conv.get('rate_discussed'):,}")

        # Summary metrics
        if conversations_data:
            st.divider()
            st.subheader("📊 Conversation Metrics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Conversations", len(conversations_data))
            with col2:
                # Count successful vs unsuccessful loads from agent notes
                successful_loads = len([c for c in conversations_data 
                                      if c.get('agent_notes') and 'Load Status: Successful' in c.get('agent_notes', '')])
                st.metric("Customer Classification", f"{successful_loads}/{len(conversations_data)}")
            
            # Add bar chart for load classification
            st.subheader("Load Classification Results")
            unsuccessful_loads = len([c for c in conversations_data 
                                    if c.get('agent_notes') and ('Load Status: Not' in c.get('agent_notes', '') or 'Load Status: Unsuccessful' in c.get('agent_notes', ''))])
            unknown_loads = len(conversations_data) - successful_loads - unsuccessful_loads
            
            # Create data for bar chart
            import pandas as pd
            classification_data = pd.DataFrame({
                'Status': ['Successful', 'Unsuccessful', 'Unknown'],
                'Count': [successful_loads, unsuccessful_loads, unknown_loads]
            })
            
            # Display bar chart
            st.bar_chart(classification_data.set_index('Status'))

    else:
        st.info("No customer conversations found. Your agents can start submitting conversation data using the `/conversations` API endpoint.")
        
        # Show example API usage
        with st.expander("📋 API Usage Example"):
            st.code('''
# Example: Agent submitting conversation data
import requests

conversation_data = {
    "conversation_id": "conv_20250115_001",
    "customer_name": "John Smith Trucking",
    "customer_phone": "+1-555-123-4567",
    "customer_email": "john@smithtrucking.com",
    "conversation_summary": "Customer needs reefer transport from Dallas to Miami",
    "load_requirements": "Temperature controlled, 48ft trailer, 40,000 lbs",
    "equipment_needed": "Reefer",
    "pickup_location": "Dallas, TX",
    "delivery_location": "Miami, FL",
    "pickup_date": "2025-01-20",
    "delivery_date": "2025-01-22",
    "rate_discussed": 3500,
    "customer_priority": "high",
    "follow_up_needed": true,
    "follow_up_date": "2025-01-16",
    "agent_notes": "Customer is a repeat client, very price sensitive"
}

response = requests.post(
    "http://localhost:8000/conversations",
    json=conversation_data,
    headers={"x-api-key": "mysecret"}
)
            ''', language='python')
