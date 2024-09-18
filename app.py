import streamlit as st
import pandas as pd
import pycountry
import plotly.express as px

# Generate a mapping of short codes to full country names using pycountry
country_mapping = {country.alpha_3.lower(): country.name for country in pycountry.countries}

# Function to load data from Google Drive using the direct download link
@st.cache_data
def load_data_from_drive():
    # Use the correct Google Drive direct download link for the CSV file
    google_drive_csv_url = 'https://drive.google.com/uc?id=1Eyaz5WozXoqHu-6X82Dc5GlwHbI99-7g'

    # Read the CSV data with UTF-8 encoding
    data = pd.read_csv(google_drive_csv_url, encoding='utf-8')  # Assuming the file is properly UTF-8 encoded
    
    # Handle NaN values by replacing them with 'Unknown' for the relevant columns
    data['inst_name'] = data['inst_name'].fillna('Unknown')
    data['cntry'] = data['cntry'].fillna('Unknown')
    data['authfull'] = data['authfull'].fillna('Unknown')
    
    return data

# Load the data
data = load_data_from_drive()

# Set the title of the app
st.title("Author Career and Publications Search App")

# Step 1: Filter countries and institutions dynamically based on selection
# Get the list of countries and institutions in the filtered data
all_institutions = sorted(data['inst_name'].unique())
all_countries = sorted([f"{country_mapping.get(code.lower(), code)} ({code})" for code in data['cntry'].unique()])

# Filter based on country selection
selected_country_display = st.selectbox("Select Country", options=['All'] + all_countries)
selected_country = None
if selected_country_display != 'All':
    selected_country = selected_country_display.split('(')[-1].rstrip(')')

# Filter the institutions based on the selected country
if selected_country and selected_country != 'All':
    filtered_data_by_country = data[data['cntry'].str.lower() == selected_country.lower()]
    institutions = sorted(filtered_data_by_country['inst_name'].unique())
else:
    institutions = all_institutions

# Step 2: Filter institutions dynamically based on country or institution selection
selected_institution = st.selectbox("Select Institution", options=['All'] + list(institutions))

# Filter based on institution selection
if selected_institution != 'All':
    filtered_data_by_institution = data[data['inst_name'] == selected_institution]
    countries = sorted([f"{country_mapping.get(code.lower(), code)} ({code})" for code in filtered_data_by_institution['cntry'].unique()])
else:
    countries = all_countries

# Now we dynamically update the countries list if an institution is selected
if selected_institution != 'All':
    selected_country_display = st.selectbox("Select Country (Filtered)", options=countries, index=0)

# Step 3: Handle Author Name Search
author_name = st.text_input("Search by Author Name (Partial or Full)")

# Apply filters to the data
filtered_data = data.copy()

# Apply Institution filter if selected
if selected_institution != 'All':
    filtered_data = filtered_data[filtered_data['inst_name'] == selected_institution]

# Apply Country filter if selected
if selected_country and selected_country != 'All':
    filtered_data = filtered_data[filtered_data['cntry'].str.lower() == selected_country.lower()]

# Apply Author Name filter if input is provided
if author_name:
    filtered_data = filtered_data[filtered_data['authfull'].str.contains(author_name, case=False, na=False)]

# Show some basic statistics about the filtered data
st.subheader("Statistics")
num_authors = len(filtered_data['authfull'].unique())
num_institutions = len(filtered_data['inst_name'].unique())
num_countries = len(filtered_data['cntry'].unique())

st.write(f"**Number of Authors:** {num_authors}")
st.write(f"**Number of Institutions:** {num_institutions}")
st.write(f"**Number of Countries:** {num_countries}")

# Select only necessary columns to show
columns_to_show = ['authfull', 'inst_name', 'rank (ns)', 'cntry']
filtered_data = filtered_data[columns_to_show]

# Display the filtered results
st.write(f"Showing {len(filtered_data)} results")
st.dataframe(filtered_data)

# Create a choropleth map for country distribution
st.subheader("Author Distribution by Country")

if not filtered_data.empty:
    # Use the short country code and count authors per country
    country_counts = filtered_data['cntry'].value_counts().reset_index()
    country_counts.columns = ['cntry', 'count']

    # Ensure all country codes are uppercase for the ISO-3 format required by Plotly
    country_counts['cntry'] = country_counts['cntry'].str.upper()

    # Filter out any country codes that are not valid ISO-3 codes
    valid_iso3_codes = set([country.alpha_3 for country in pycountry.countries])
    country_counts = country_counts[country_counts['cntry'].isin(valid_iso3_codes)]

    # Check if there is any valid data to display
    if not country_counts.empty:
        # Add full country names
        country_counts['country_name'] = country_counts['cntry'].apply(lambda x: country_mapping.get(x.lower(), x))

        # Plot the map
        fig = px.choropleth(country_counts,
                            locations="cntry",
                            color="count",
                            hover_name="country_name",
                            locationmode="ISO-3",
                            color_continuous_scale="Viridis",
                            labels={"count": "Number of Authors"})

        st.plotly_chart(fig)
    else:
        st.write("No valid country data to display on the map.")
else:
    st.write("No data to display.")

# Additional visualization: Bar Chart of Top Institutions by Author Count
st.subheader("Top Institutions by Author Count")

# Count authors per institution
institution_counts = filtered_data['inst_name'].value_counts().reset_index()
institution_counts.columns = ['inst_name', 'count']

# Plot a bar chart
fig_inst = px.bar(institution_counts.head(10), x='inst_name', y='count',
                  labels={'inst_name': 'Institution', 'count': 'Number of Authors'},
                  title='Top 10 Institutions by Author Count')
st.plotly_chart(fig_inst)

# Add contact information at the bottom
st.write("---")
st.write("Contact Information")
st.write("**Dr. Mehmet Kanik**")
st.write("[mmtkanik@gmail.com](mailto:mmtkanik@gmail.com)")
