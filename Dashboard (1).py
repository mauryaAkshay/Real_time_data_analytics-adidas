import streamlit as st
import plotly.express as px
import pandas as pd
import io

# File upload
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
if fl is not None:
    # Reset the file stream position
    fl.seek(0)
    
    # Read the file content as a string
    csv_string = io.StringIO(fl.read().decode("ISO-8859-1"))

    # Skip problematic rows using the skiprows parameter
    df = pd.read_csv(csv_string, error_bad_lines=False)
else:
    # Use a default file path if no file is uploaded
    default_file_path = r"C:\Users\Dell\Desktop\Capstone-2024\Sample - Superstore.xls"
    df = pd.read_excel(default_file_path)

# Sidebar filters
st.sidebar.header("Choose your filter: ")

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

# Convert date1 and date2 to datetime objects
date1 = pd.to_datetime(st.sidebar.date_input("Start Date", startDate))
date2 = pd.to_datetime(st.sidebar.date_input("End Date", endDate))

region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
state = st.sidebar.multiselect("Pick the State", df["State"].unique())
city = st.sidebar.multiselect("Pick the City", df["City"].unique())

# Filter data
filtered_df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)]

if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]
if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]
if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]

# EDA
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

# Charts and visualizations
st.subheader("Category wise Sales")
fig_category = px.bar(category_df, x="Category", y="Sales", text='Sales', template="seaborn")
st.plotly_chart(fig_category, use_container_width=True)

st.subheader("Region wise Sales")
fig_region = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
fig_region.update_traces(textposition="outside")
st.plotly_chart(fig_region, use_container_width=True)

# Data tables
with st.expander("Category_ViewData"):
    st.write(category_df)
    csv = category_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                       help='Click here to download the data as a CSV file')

with st.expander("Region_ViewData"):
    region_sales = filtered_df.groupby("Region", as_index=False)["Sales"].sum()
    st.write(region_sales)
    csv = region_sales.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                       help='Click here to download the data as a CSV file')

# Time series analysis
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["Order Date"].dt.to_period("M"))["Sales"].sum()).reset_index()

# Convert Period object to string representation
linechart["Order Date"] = linechart["Order Date"].astype(str)

fig_time_series = px.line(linechart, x="Order Date", y="Sales", labels={"Sales": "Amount"})
st.plotly_chart(fig_time_series, use_container_width=True)


# Hierarchical view
st.subheader("Hierarchical view of Sales using TreeMap")
fig_tree_map = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales",
                          hover_data=["Sales"], color="Sub-Category")
st.plotly_chart(fig_tree_map, use_container_width=True)

# Segment wise sales
st.subheader('Segment wise Sales')
fig_segment = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
st.plotly_chart(fig_segment, use_container_width=True)

# Category wise sales
st.subheader('Category wise Sales')
fig_category_wise = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
st.plotly_chart(fig_category_wise, use_container_width=True)

# Month wise sub-Category sales summary
st.subheader(":point_right: Month wise Sub-Category Sales Summary")

# Define df_sample by selecting a subset of columns from df
df_sample = df[['Region', 'State', 'City', 'Category', 'Sales', 'Profit', 'Quantity']].head()

with st.expander("Summary_Table"):
    st.write(df_sample)


# Scatter plot
st.subheader("Relationship between Sales and Profits using Scatter Plot")
fig_scatter = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
fig_scatter.update_layout(title="Relationship between Sales and Profits using Scatter Plot",
                          xaxis=dict(title="Sales"),
                          yaxis=dict(title="Profit"))
st.plotly_chart(fig_scatter, use_container_width=True)

# View Data
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2])

# Download original DataSet
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
