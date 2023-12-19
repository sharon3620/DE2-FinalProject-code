import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from google.cloud import bigquery
import seaborn as sns
import numpy as np

# project details
project_id = "de2-finalproject"
client = bigquery.Client(project=project_id)
os.environ["GOOGLE_CLOUD_PROJECT"] = "C:/Users/Sharon Mathew/Downloads/de2-finalproject-28f624697f1b.json"

# Streamlit page heading
st.title("NYPD Incident Analysis Dashboard")

# Visualization 1 of business question 1 
Query1_Visual1 = """
SELECT 
    EXTRACT(DAYOFWEEK FROM OCCUR_DATE) AS DayOfWeek, 
    EXTRACT(YEAR FROM OCCUR_DATE) AS Year,
    BORO, 
    COUNT(*) AS IncidentCount
FROM 
    `de2-finalproject.nypd_data.nypd_table` 
WHERE 
    EXTRACT(YEAR FROM OCCUR_DATE) = @selected_year
GROUP BY 
    DayOfWeek, Year, BORO
ORDER BY 
    DayOfWeek, Year, IncidentCount DESC
"""

# Fetch unique years in the dataset
unique_years = client.query("SELECT DISTINCT EXTRACT(YEAR FROM OCCUR_DATE) AS Year FROM `de2-finalproject.nypd_data.nypd_table`").to_dataframe()["Year"].tolist()

# Streamlit widget for interaction 
selected_year = st.selectbox("Select Year", unique_years)

# Set parameters for the query
query_params = [
    bigquery.ScalarQueryParameter("selected_year", "INT64", selected_year)
]

# Configure the job with the parameterized query
job_config = bigquery.QueryJobConfig(
    query_parameters=query_params
)

# Fetch the data for the selected year
df1 = client.query(Query1_Visual1, job_config=job_config).to_dataframe()

st.header(f"Incident Count by Day of Week and Borough for {selected_year}")
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x='DayOfWeek', y='IncidentCount', hue='BORO', data=df1, ax=ax)
plt.xlabel('Day of Week')
plt.ylabel('Incident Count')
st.pyplot(fig)




# Visualization 2 of business question 1 
Query1_Visual2 = """
SELECT 
    BORO, 
    EXTRACT(MONTH FROM OCCUR_DATE) AS Month,
    EXTRACT(YEAR FROM OCCUR_DATE) AS Year,
    COUNT(*) AS IncidentCount 
FROM 
    `de2-finalproject.nypd_data.nypd_table` 
GROUP BY 
    BORO, Month, Year 
ORDER BY 
    BORO, Year, Month
"""

df2 = client.query(Query1_Visual2).to_dataframe()

# Plotting the results of the query
st.header("Visualization 2: Incident Count Over Time by Borough")
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize = (12, 8))
sns.lineplot(x = 'Month', y = 'IncidentCount', hue = 'BORO', data = df2, ax = ax)
#plt.title('Incident Count Over Time by Borough')
plt.xlabel('Month')
plt.ylabel('Incident Count')
st.pyplot(fig)


# Visualization 1 of business question 2 
Query2_Visual1 = """
SELECT 
    PERP_AGE_GROUP, PERP_SEX, PERP_RACE, BORO, LOC_OF_OCCUR_DESC, 
    COUNT(*) AS IncidentCount 
FROM 
    `de2-finalproject.nypd_data.nypd_table` 
WHERE 
    PERP_RACE NOT IN ("UNKNOWN","(null)") 
GROUP BY 
    PERP_AGE_GROUP, PERP_SEX, PERP_RACE, BORO, LOC_OF_OCCUR_DESC 
ORDER BY 
    IncidentCount DESC
"""

df3 = client.query(Query2_Visual1).to_dataframe()

# Plotting the results of the query
st.header("Visualization 3: Incident Counts by Race")
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize = (12, 8))
sns.barplot(x = 'IncidentCount', y = 'PERP_RACE', data = df3, ci = None, palette = 'viridis')
#plt.title('Incident Counts by Race')
plt.xlabel('Incident Count')
plt.ylabel('Race')
st.pyplot(fig)


# Visualization 2 of business question 2 
Query2_Visual2 = """
SELECT 
    VIC_AGE_GROUP, VIC_RACE, VIC_SEX, BORO,
    COUNT(*) as Incident_Count
FROM 
    `de2-finalproject.nypd_data.nypd_table`
WHERE 
    VIC_AGE_GROUP NOT IN ("UNKNOWN")
     AND VIC_RACE NOT IN ("UNKNOWN")   
GROUP BY 
    VIC_AGE_GROUP, VIC_RACE, VIC_SEX, BORO
ORDER BY Incident_Count DESC
"""

df4 = client.query(Query2_Visual2).to_dataframe()
heatmap_data = df4.pivot_table(index='VIC_AGE_GROUP', columns='VIC_RACE', values='Incident_Count', aggfunc='sum')
heatmap_data = heatmap_data.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
heatmap_data = heatmap_data.fillna(0)

# Plotting the results of the query
st.header("Visualization 4: Heatmap of Incident Counts by Victim Age Group and Race")
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(heatmap_data, annot=True, cmap='YlGn', fmt="g", ax=ax)
#plt.title('Heatmap of Incident Counts by Victim Age Group and Race')
plt.xlabel('Victim Race')
plt.ylabel('Victim Age Group')
st.pyplot(fig)