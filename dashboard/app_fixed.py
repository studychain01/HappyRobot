import os, requests, pandas as pd, streamlit as st

# Try local API first, fall back to remote if needed
API_BASE = os.getenv("API_BASE", "https://happyrobot-trucking-loadsapi.onrender.com")
API_KEY = os.getenv("API_KEY", "mysecret")

# Set page config
st.set_page_config(
    page_title="HappyRobot Trucking",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 HappyRobot Trucking Platform")

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

    st.subheader("Loads")
    st.dataframe(df, use_container_width=True)

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
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            priority_filter = st.selectbox("Filter by Priority", ["All", "high", "medium", "low"])
        with col2:
            follow_up_filter = st.selectbox("Follow-up Needed", ["All", "Yes", "No"])
        with col3:
            customer_search = st.text_input("Search Customer Name", placeholder="Enter customer name...")

        # Apply filters
        filtered_conversations = conversations_data.copy()
        
        if priority_filter != "All":
            filtered_conversations = [c for c in filtered_conversations if c.get("customer_priority") == priority_filter]
        
        if follow_up_filter == "Yes":
            filtered_conversations = [c for c in filtered_conversations if c.get("follow_up_needed")]
        elif follow_up_filter == "No":
            filtered_conversations = [c for c in filtered_conversations if not c.get("follow_up_needed")]
        
        if customer_search:
            filtered_conversations = [c for c in filtered_conversations 
                                    if customer_search.lower() in (c.get("customer_name", "") or "").lower()]

        st.write(f"Showing {len(filtered_conversations)} conversations")

        # Display conversation cards
        for conv in filtered_conversations:
            with st.expander(f"🗣️ {conv.get('customer_name', 'Unknown Customer')} - {conv.get('conversation_id', 'N/A')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if conv.get('load_requirements'):
                        st.write("**Load Requirements:**")
                        st.write(conv.get('load_requirements'))
                    
                    if conv.get('agent_notes'):
                        st.write("**Agent Notes:**")
                        st.write(conv.get('agent_notes'))
                
                with col2:
                    # Customer details
                    if conv.get('customer_phone'):
                        st.write(f"📞 **Phone:** {conv.get('customer_phone')}")
                    if conv.get('customer_email'):
                        st.write(f"📧 **Email:** {conv.get('customer_email')}")
                    
                    # Load booking status
                    if conv.get('agent_notes') and 'Load Status:' in conv.get('agent_notes', ''):
                        import re
                        status_match = re.search(r'Load Status: (\w+)', conv.get('agent_notes', ''))
                        if status_match:
                            status = status_match.group(1).lower()
                            if status == 'successful':
                                st.write("✅ **Load: BOOKED**")
                            elif status == 'not':  # "not successful"
                                st.write("❌ **Load: NOT BOOKED**")
                    
                    # Load details
                    if conv.get('pickup_location') or conv.get('delivery_location'):
                        st.write("**Route:**")
                        if conv.get('pickup_location'):
                            st.write(f"📍 From: {conv.get('pickup_location')}")
                        if conv.get('delivery_location'):
                            st.write(f"📍 To: {conv.get('delivery_location')}")
                    
                    if conv.get('equipment_needed'):
                        st.write(f"**Equipment:** {conv.get('equipment_needed')}")
                    
                    if conv.get('miles'):
                        st.write(f"🛣️ **Miles:** {conv.get('miles'):,}")
                    
                    if conv.get('rate_discussed'):
                        st.write(f"**Rate Discussed:** ${conv.get('rate_discussed'):,}")
                    
                    # Follow-up info
                    if conv.get('follow_up_needed'):
                        st.write("🔔 **Follow-up Needed**")
                        if conv.get('follow_up_date'):
                            st.write(f"📅 Follow-up Date: {conv.get('follow_up_date')}")
                    
                    # Timestamp
                    if conv.get('timestamp'):
                        st.write(f"🕐 {conv.get('timestamp')[:19].replace('T', ' ')}")

        # Summary metrics
        if conversations_data:
            st.divider()
            st.subheader("📊 Conversation Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Conversations", len(conversations_data))
            with col2:
                follow_ups = len([c for c in conversations_data if c.get('follow_up_needed')])
                st.metric("Follow-ups Needed", follow_ups)
            with col3:
                high_priority = len([c for c in conversations_data if c.get('customer_priority') == 'high'])
                st.metric("High Priority", high_priority)
            with col4:
                avg_rate = sum([c.get('rate_discussed', 0) for c in conversations_data if c.get('rate_discussed')]) / max(1, len([c for c in conversations_data if c.get('rate_discussed')]))
                st.metric("Avg Rate Discussed", f"${avg_rate:,.0f}" if avg_rate > 0 else "N/A")

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
