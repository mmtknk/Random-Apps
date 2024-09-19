import streamlit as st
import pandas as pd
import pycountry
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration to wide mode
st.set_page_config(layout="wide", page_title="Author Career and Publications Search App")

# Generate a mapping of short codes to full country names using pycountry
country_mapping = {country.alpha_3.lower(): country.name for country in pycountry.countries}

# Function to load data from Google Drive using the direct download link
@st.cache_resource  # Updated to use st.cache_resource for resource caching
def load_data_from_drive():
    google_drive_csv_url = 'https://drive.google.com/uc?id=1Eyaz5WozXoqHu-6X82Dc5GlwHbI99-7g'

    try:
        data = pd.read_csv(google_drive_csv_url, encoding='utf-8')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

    # Handle NaN values by replacing them with 'Unknown' for the relevant columns
    data['inst_name'] = data['inst_name'].fillna('Unknown')
    data['cntry'] = data['cntry'].fillna('Unknown')
    data['authfull'] = data['authfull'].fillna('Unknown')
    
    return data

# Load the data
data = load_data_from_drive()

# Set the title of the app
st.title("Author Career and Publications Search App")



# Define the table data
table_data = {
    "FIELD": ["authfull", "inst_name", "cntry", "np6023", "firstyr", "lastyr", "rank (ns)", "nc9623 (ns)", "h23 (ns)", "hm23 (ns)", "nps (ns)", "ncs (ns)", "cpsf (ns)", "ncsf (ns)", "npsfl (ns)", "ncsfl (ns)", "c (ns)", "npciting (ns)", "cprat (ns)", "np6023 cited9623 (ns)", "self%", "rank", "nc9623", "h23", "hm23", "nps", "ncs", "cpsf", "ncsf", "npsfl", "ncsfl", "c", "npciting", "cprat", "np6023 cited9623", "np6023_rw", "nc9623_to_rw", "nc9623_rw", "sm-subfield-1", "sm-subfield-1-frac", "sm-subfield-2", "sm-subfield-2-frac", "sm-field", "sm-field-frac", "rank sm-subfield-1", "rank sm-subfield-1 (ns)", "sm-subfield-1 count"],
    "BASIS": ["", "", "", "", "", "", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "self-citations excluded", "", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "", "", "", "", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "all citations", "self-citations excluded", ""],
    "DESCRIPTION": ["author name", "institution name (large institutions only)", "country associated with most recent institution", "# papers 1960-2023", "year of first publication", "year of most recent publication", "rank based on composite score c", "total cites 1996-2023", "h-index as of end-2023", "hm-index as of end-2023", "number of single authored papers", "total cites to single authored papers", "number of single+first authored papers", "total cites to single+first authored papers", "number of single+first+last authored papers", "total cites to single+first+last authored papers", "composite score", "number of distinct citing papers", "ratio of total citations to distinct citing papers", "number of papers 1960-2023 that have been cited at least once", "self-citation percentage", "rank based on composite score c", "total cites 1996-2023", "h-index as of end-2023", "hm-index as of end-2023", "number of single authored papers", "total cites to single authored papers", "number of single+first authored papers", "total cites to single+first authored papers", "number of single+first+last authored papers", "total cites to single+first+last authored papers", "composite score", "number of distinct citing papers", "ratio of total citations to distinct citing papers", "number of papers 1960-2023 that have been cited at least once", "# papers 1960-2023 marked as Retraction in RWDB", "total cites 1996-2023 to papers (by this author) marked as Retraction in RWDB", "total cites 1996-2023 from papers (by any author) marked as Retraction in RWDB", "top ranked Science-Metrix category (subfield) for author", "associated category fraction", "second ranked Science-Metrix category (subfield) for author", "associated category fraction", "top ranked higher-level Science-Metrix category (field) for author", "associated category fraction", "rank of c within category sm-subfield-1", "rank of c (ns) within category sm-subfield-1", "total number of authors within category sm-subfield-1"]
}

# Print lengths of each list to identify the issue
st.write(f"Length of FIELD: {len(table_data['FIELD'])}")
st.write(f"Length of BASIS: {len(table_data['BASIS'])}")
st.write(f"Length of DESCRIPTION: {len(table_data['DESCRIPTION'])}")

# Ensure all lists in table_data have the same length
assert len(table_data["FIELD"]) == len(table_data["BASIS"]) == len(table_data["DESCRIPTION"]), "All lists in table_data must have the same length"

# Create an expander to show the table information
with st.expander("Show Table Information"):
    st.write("### Table Information")
    st.dataframe(pd.DataFrame(table_data))




# Step 1: Filter countries and institutions dynamically based on selection
all_institutions = sorted(data['inst_name'].unique())
all_countries = sorted([f"{country_mapping.get(code.lower(), code)} ({code})" for code in data['cntry'].unique()])

# Country selection filter
selected_country_display = st.selectbox("Select Country", options=['All'] + all_countries)
selected_country = None
if selected_country_display != 'All':
    selected_country = selected_country_display.split('(')[-1].rstrip(')')

# Filter based on country selection
if selected_country and selected_country != 'All':
    filtered_data_by_country = data[data['cntry'].str.lower() == selected_country.lower()]
    institutions = sorted(filtered_data_by_country['inst_name'].unique())
else:
    institutions = all_institutions

# Institution selection filter
selected_institution = st.selectbox("Select Institution", options=['All'] + list(institutions))

# Filter data based on institution and country selection
filtered_data = data.copy()
if selected_institution != 'All':
    filtered_data = filtered_data[filtered_data['inst_name'] == selected_institution]
if selected_country and selected_country != 'All':
    filtered_data = filtered_data[filtered_data['cntry'].str.lower() == selected_country.lower()]

# Author name search filter
author_name = st.text_input("Search by Author Name (Partial or Full)")
if author_name:
    filtered_data = filtered_data[filtered_data['authfull'].str.contains(author_name, case=False, na=False)]

# Author Distribution by Country
st.subheader("Author Distribution by Country")
if not filtered_data.empty:
    country_counts = filtered_data['cntry'].value_counts().reset_index()
    country_counts.columns = ['cntry', 'count']
    country_counts['cntry'] = country_counts['cntry'].str.upper()
    
    valid_iso3_codes = set([country.alpha_3 for country in pycountry.countries])
    country_counts = country_counts[country_counts['cntry'].isin(valid_iso3_codes)]
    
    if not country_counts.empty:
        country_counts['country_name'] = country_counts['cntry'].apply(lambda x: country_mapping.get(x.lower(), x))
        
        fig_map = px.choropleth(country_counts,
                                locations="cntry",
                                color="count",
                                hover_name="country_name",
                                locationmode="ISO-3",
                                color_continuous_scale="Viridis",
                                labels={"count": "Number of Authors"})
        st.plotly_chart(fig_map)
    else:
        st.write("No valid country data to display on the map.")
else:
    st.write("No data to display.")

# Show some basic statistics about the filtered data
st.subheader("Statistics")
num_authors = len(filtered_data['authfull'].unique())
num_institutions = len(filtered_data['inst_name'].unique())
num_countries = len(filtered_data['cntry'].unique())

st.write(f"**Number of Authors:** {num_authors}")
st.write(f"**Number of Institutions:** {num_institutions}")
st.write(f"**Number of Countries:** {num_countries}")

# Display the filtered results
st.write(f"Showing {len(filtered_data)} results")
st.write(filtered_data)

# Top 5 Countries by Author Count
top_countries = filtered_data['cntry'].value_counts().head(5)
st.write("**Top 5 Countries by Author Count:**")
for i, (country_code, count) in enumerate(top_countries.items(), 1):
    country_name = country_mapping.get(country_code.lower(), country_code)
    st.write(f"{i}. {country_name} ({count} authors)")

# Top 5 Institutions by Author Count
top_institutions = filtered_data['inst_name'].value_counts().head(5)
st.write("**Top 5 Institutions by Author Count:**")
for i, (inst_name, count) in enumerate(top_institutions.items(), 1):
    st.write(f"{i}. {inst_name} ({count} authors)")

# Visualization 1: Field Distribution
if 'sm-field' in filtered_data.columns:
    st.subheader("Field Distribution")
    field_counts = filtered_data['sm-field'].value_counts().reset_index()
    field_counts.columns = ['Field', 'Count']
    
    fig_field = px.bar(field_counts, x='Field', y='Count', 
                       title='Field Distribution',
                       labels={'Field': 'Field', 'Count': 'Number of Authors'})
    st.plotly_chart(fig_field)

# Visualization 2: Subfield Distribution
if 'sm-subfield-1' in filtered_data.columns:
    st.subheader("Subfield Distribution")
    subfield_counts = filtered_data['sm-subfield-1'].value_counts().reset_index()
    subfield_counts.columns = ['Subfield', 'Count']
    
    fig_subfield = px.bar(subfield_counts, x='Subfield', y='Count',
                          title='Subfield Distribution',
                          labels={'Subfield': 'Subfield', 'Count': 'Number of Authors'})
    st.plotly_chart(fig_subfield)

# Visualization 4: Rank Distribution by Subfield
if 'rank sm-subfield-1' in filtered_data.columns:
    # Ensure 'rank sm-subfield-1' is numeric
    filtered_data['rank sm-subfield-1'] = pd.to_numeric(filtered_data['rank sm-subfield-1'], errors='coerce')
    
    st.subheader("Rank Distribution by Subfield")
    rank_by_subfield = filtered_data.groupby('sm-subfield-1')['rank sm-subfield-1'].mean().reset_index()
    rank_by_subfield.columns = ['Subfield', 'Average Rank']

    fig_rank_subfield = px.bar(rank_by_subfield, x='Subfield', y='Average Rank',
                               title='Average Rank by Subfield',
                               labels={'Subfield': 'Subfield', 'Average Rank': 'Average Rank'})
    
    st.plotly_chart(fig_rank_subfield)

# Visualization: Rank Distribution Histogram by Field
if 'rank (ns)' in filtered_data.columns and 'sm-field' in filtered_data.columns:
    # Ensure 'rank (ns)' is numeric
    filtered_data['rank (ns)'] = pd.to_numeric(filtered_data['rank (ns)'], errors='coerce')
    
    st.subheader("Rank Distribution Histogram by Field")
    
    fig_rank_hist = px.histogram(filtered_data, x='rank (ns)', color='sm-field',
                                 title='Rank Distribution by Field',
                                 labels={'rank (ns)': 'Rank', 'sm-field': 'Field'},
                                 nbins=20)
    st.plotly_chart(fig_rank_hist)

# Visualization: Rank Distribution by Field (Average)
if 'rank (ns)' in filtered_data.columns and 'sm-field' in filtered_data.columns:
    st.subheader("Rank Distribution by Field (Average Rank)")
    
    rank_by_field = filtered_data.groupby('sm-field')['rank (ns)'].mean().reset_index()
    rank_by_field.columns = ['Field', 'Average Rank']
    
    fig_rank_field = px.bar(rank_by_field, x='Field', y='Average Rank',
                            title='Average Rank by Field',
                            labels={'Field': 'Field', 'Average Rank': 'Average Rank'})
    
    st.plotly_chart(fig_rank_field)

# Contact information
st.write("---")
st.write("Contact Information")
st.write("**Dr. Mehmet Kanik**")
st.write("[mmtkanik@gmail.com](mailto:mmtkanik@gmail.com)")
