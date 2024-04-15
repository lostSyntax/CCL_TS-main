
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from lifetimes.utils import summary_data_from_transaction_data
from lifetimes import BetaGeoFitter
import plotly.express as px

st.title('Retail Data Analysis and Customer Segmentation')

uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, encoding='latin-1')
    st.write("Data Overview:")
    st.dataframe(data.head())

    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
    data['CustomerID'] = data['CustomerID'].astype(str)
    data['TotalPrice'] = data['Quantity'] * data['UnitPrice']

    latest_date = data['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = summary_data_from_transaction_data(data, 'CustomerID', 'InvoiceDate', 'TotalPrice', observation_period_end=latest_date)

    bgf = BetaGeoFitter(penalizer_coef=0.0)
    bgf.fit(rfm['frequency'], rfm['recency'], rfm['T'])
    
    def rfm_segmentation(df):
        if df['recency'] <= 365 and df['frequency'] > 3 and df['monetary_value'] > 500:
            return 'Champions'
        elif df['frequency'] > 2 and df['monetary_value'] > 300:
            return 'Loyal Customers'
        elif df['recency'] <= 365 and df['frequency'] == 2:
            return 'Potential Loyalist'
        elif df['recency'] <= 365 and df['frequency'] == 1:
            return 'New Customers'
        elif df['recency'] > 365 and df['frequency'] >= 2:
            return 'At Risk'
        else:
            return 'Can’t Lose Them'

    rfm['Segment'] = rfm.apply(rfm_segmentation, axis=1)
    
    st.write("RFM Segmentation Overview:")
    st.dataframe(rfm.head())

    st.subheader("Count of Transactions by Country")
    country_counts = data['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Transactions']
    fig1 = px.bar(country_counts, x='Country', y='Transactions', title='Transactions by Country')
    st.plotly_chart(fig1)

    st.subheader("Customer Segments")
    segments_counts = rfm['Segment'].value_counts().reset_index()
    segments_counts.columns = ['Segment', 'Count']
    fig2, ax = plt.subplots()
    sns.barplot(data=segments_counts, x='Segment', y='Count', palette='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.title('Customer Segments')
    st.pyplot(fig2)

    st.subheader("Average Price by Country")
    avg_price_country = data.groupby('Country')['UnitPrice'].mean().reset_index()
    fig_avg_price = px.scatter(avg_price_country, x='Country', y='UnitPrice', color='UnitPrice',
                               title='Average Price by Country')
    st.plotly_chart(fig_avg_price)
    
    st.subheader("Price Distribution for a Selected Country")
    selected_country = st.selectbox("Select a Country", data['Country'].unique())
    filtered_data = data[data['Country'] == selected_country]
    fig3, ax = plt.subplots()
    sns.violinplot(x=filtered_data['UnitPrice'])
    plt.title(f'Price Distribution in {selected_country}')
    st.pyplot(fig3)


else:
    st.warning('Please upload a CSV file to proceed.')
