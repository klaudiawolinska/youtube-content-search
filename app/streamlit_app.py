import streamlit as st
from snowflake.core import Root
from snowflake.snowpark.context import get_active_session


DB = "youtube_trends"
SCHEMA = "public"

SERVICES = {
    "Comments": "youtube_comments_svc",
    "Videos": "youtube_videos_svc"
}


def get_column_specification(service_name):
    """
    Fetch column and attribute info for the Cortex search service dynamically
    """
    session = get_active_session()
    
    result = session.sql(
        f"DESC CORTEX SEARCH SERVICE {DB}.{SCHEMA}.{service_name}"
    ).collect()[0]

    st.session_state.search_column = result.search_column    
    st.session_state.columns = result.columns.split(",")
    st.session_state.attribute_columns = result.attribute_columns.split(",") if result.attribute_columns else []

def init_layout(service_key):
    st.title("📺 YouTube Trends Explorer (Cortex Search)")
    st.markdown(f"Querying service: `{DB}.{SCHEMA}.{SERVICES[service_key]}`".replace('"', ''))

def query_cortex_search_service(query, service_key, filter={}):
    """
    Queries the selected Cortex Search Service and returns results
    """
    session = get_active_session()
    service_name = SERVICES[service_key]

    cortex_search_service = (
        Root(session)
        .databases[DB]
        .schemas[SCHEMA]
        .cortex_search_services[service_name]
    )

    context_documents = cortex_search_service.search(
        query,
        columns=st.session_state.columns,
        filter=filter,
        limit=st.session_state.limit
    )
    return context_documents.results

def init_search_input():
    st.session_state.query = st.text_input("🔍 Enter your natural language query", placeholder="e.g. self development, AI, music...")

def init_limit_input():
    st.session_state.limit = st.number_input("Results limit", min_value=1, value=10)

def distinct_values_for_attribute(base_table, col_name):
    session = get_active_session()
    values = session.sql(f"SELECT DISTINCT {col_name} AS VALUE FROM {base_table}").collect()
    return [row["VALUE"] for row in values if row["VALUE"] is not None]

def display_search_results(results):
    """
    Display results
    """
    st.subheader("Search results")
    for i, result in enumerate(results):
        result = dict(result)
        container = st.expander(f"[Result {i+1}]", expanded=True)

        # Show the main text/title
        container.markdown(result.get(st.session_state.search_column, ""))

        # Show other attributes
        for column, column_value in sorted(result.items()):
            if column == st.session_state.search_column:
                continue
            container.markdown(f"**{column}**: {column_value}")

def create_filter_object(attributes):
    """
    Simple filter builder for Cortex search queries
    """
    and_clauses = []
    for column, column_values in attributes.items():
        if len(column_values) == 0:
            continue
        or_clauses = [{"@eq": {column: attr_value}} for attr_value in column_values]
        and_clauses.append({"@or": or_clauses })

    return {"@and": and_clauses} if and_clauses else {}


def main():
    service_key = st.radio("Search in:", list(SERVICES.keys()))

    init_layout(service_key)
    get_column_specification(SERVICES[service_key])

    st.session_state.attributes = {}
    for col in st.session_state.attribute_columns:
        options = distinct_values_for_attribute(f"{DB}.{SCHEMA}.{service_key.lower()}", col)
        st.session_state.attributes[col] = st.multiselect(col, options)


    init_limit_input()
    init_search_input()


    if not st.session_state.query:
        return

    results = query_cortex_search_service(
        st.session_state.query,
        service_key,
        filter=create_filter_object(st.session_state.attributes)
    )

    display_search_results(results)


if __name__ == "__main__":
    st.set_page_config(page_title="YouTube Cortex Search", layout="wide")
    main()
