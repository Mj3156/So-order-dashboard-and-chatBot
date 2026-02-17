import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Set page configuration
st.set_page_config(
    page_title="SO Order Ageing Viewer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:8000"

def get_summary():
    try:
        response = requests.get(f"{API_URL}/summary")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Error fetching summary: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return None

def get_details(status, page=1, page_size=1000):
    try:
        response = requests.get(f"{API_URL}/details/{status}?page={page}&page_size={page_size}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching details: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return None

def main():
    st.title("📊 SO Order Ageing Viewer")
    
    st.markdown("### Store Status Summary")
    
    # Fetch Summary
    with st.spinner("Fetching summary data..."):
        summary_df = get_summary()
    
    if summary_df is not None:
        # Configure AgGrid for Summary
        gb = GridOptionsBuilder.from_dataframe(summary_df)
        gb.configure_selection('single', use_checkbox=False)
        
        # Set column widths
        gb.configure_column("Store Status", width=200, minWidth=150)
        
        # Make numeric columns formatted nicely with fixed widths
        numeric_cols = ['Open Qty Pcs', 'Allocated Qty Pcs', 'Picked Qty Pcs', 'Unallocated Qty Pcs']
        for col in numeric_cols:
            gb.configure_column(
                col, 
                type=["numericColumn", "numberColumnFilter"], 
                precision=0,
                width=180,
                minWidth=150
            )
        
        # Disable auto-sizing
        gb.configure_grid_options(
            domLayout='normal',
            suppressColumnVirtualisation=False
        )

        gridOptions = gb.build()
        
        grid_response = AgGrid(
            summary_df,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            theme='streamlit',
            fit_columns_on_grid_load=False,
            height=400,
            width='100%'
        )
        
        # Check for selection
        selected = grid_response['selected_rows']
        
        if selected is not None and len(selected) > 0:
            # selected is a list of dicts (or rows)
            if isinstance(selected, pd.DataFrame):
                 selected_row = selected.iloc[0]
            else:
                 selected_row = selected[0]
                 
            status = selected_row.get('Store Status')
            
            if status:
                st.markdown(f"### Details for Status: **{status}**")
                
                # Initialize session state for pagination
                if 'current_page' not in st.session_state:
                    st.session_state.current_page = 1
                if 'current_status' not in st.session_state:
                    st.session_state.current_status = status
                
                # Reset page if status changed
                if st.session_state.current_status != status:
                    st.session_state.current_page = 1
                    st.session_state.current_status = status
                
                # Page size selector
                page_size = st.selectbox("Rows per page:", [100, 500, 1000, 2000], index=2)
                
                with st.spinner(f"Fetching details for {status}..."):
                    result = get_details(status, page=st.session_state.current_page, page_size=page_size)
                
                if result:
                    total_rows = result.get('total_rows', 0)
                    total_pages = result.get('total_pages', 1)
                    current_page = result.get('page', 1)
                    returned_rows = result.get('returned_rows', 0)
                    
                    # Show pagination info
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.info(f"📊 Total: **{total_rows:,}** rows | Page **{current_page}** of **{total_pages}**")
                    with col2:
                        pass
                    with col3:
                        # Pagination controls
                        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                        with pcol1:
                            if st.button("⏮️ First", disabled=(current_page == 1)):
                                st.session_state.current_page = 1
                                st.rerun()
                        with pcol2:
                            if st.button("◀️ Prev", disabled=(current_page == 1)):
                                st.session_state.current_page = max(1, current_page - 1)
                                st.rerun()
                        with pcol3:
                            if st.button("Next ▶️", disabled=(current_page >= total_pages)):
                                st.session_state.current_page = min(total_pages, current_page + 1)
                                st.rerun()
                        with pcol4:
                            if st.button("Last ⏭️", disabled=(current_page >= total_pages)):
                                st.session_state.current_page = total_pages
                                st.rerun()
                    
                    # Display data
                    if returned_rows > 0:
                        details_df = pd.DataFrame(result['data'])
                        
                        # Configure AgGrid for details with proper column sizing
                        gb_details = GridOptionsBuilder.from_dataframe(details_df)
                        
                        # Set default column properties
                        gb_details.configure_default_column(
                            width=150,  # Default width for all columns
                            minWidth=100,
                            resizable=True,
                            sortable=True,
                            filterable=True,
                            wrapText=False,
                            autoHeight=False
                        )
                        
                        # Disable auto-sizing that causes squeezing
                        gb_details.configure_grid_options(
                            suppressColumnVirtualisation=False,
                            enableRangeSelection=True
                        )
                        
                        gridOptions_details = gb_details.build()
                        
                        AgGrid(
                            details_df, 
                            gridOptions=gridOptions_details,
                            height=500, 
                            theme='streamlit',
                            fit_columns_on_grid_load=False,
                            allow_unsafe_jscode=True,
                            width='100%'
                        )
                    else:
                        st.warning("No data on this page")
        else:
            st.info("Select a row in the summary table to see details.")

if __name__ == "__main__":
    main()
