import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape the sitemap
def scrape_sitemap(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    urls = [element.text for element in soup.find_all('loc')]
    return urls

# Function to get PageSpeed Insights
def get_pagespeed_insights(url, api_key):
    response = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                            params={"url": url, "key": api_key})
    data = response.json()

    # Initialize a dictionary to store the extracted data
    insights = {}

    # Basic info
    insights['URL'] = url
    insights['Overall Score'] = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score')

    # Audits data
    audits = data.get('lighthouseResult', {}).get('audits')

    # Extracting specific metrics
    insights['First Contentful Paint'] = audits.get('first-contentful-paint', {}).get('displayValue')
    insights['Speed Index'] = audits.get('speed-index', {}).get('displayValue')
    insights['Largest Contentful Paint'] = audits.get('largest-contentful-paint', {}).get('displayValue')
    insights['Time to Interactive'] = audits.get('interactive', {}).get('displayValue')
    insights['Total Blocking Time'] = audits.get('total-blocking-time', {}).get('displayValue')
    insights['Cumulative Layout Shift'] = audits.get('cumulative-layout-shift', {}).get('displayValue')

    # You can add more fields as needed

    return insights

# Streamlit app
def main():
    st.title("Sitemap Scraper and PageSpeed Insights")
    input_url = st.text_input("Enter the URL of the sitemap (e.g., https://example.com/sitemap.xml):")

    # Retrieve the API key from Streamlit secrets
    api_key = st.secrets["pagespeed_api_key"]
    
    if st.button("Scrape and Analyze"):
        if input_url:
            scraped_urls = scrape_sitemap(input_url)
            results = []
            for url in scraped_urls:
                insights = get_pagespeed_insights(url, api_key)
                results.append(insights)
            
            df = pd.DataFrame(results)
            st.write(df)

            # Download link for DataFrame
            st.download_button(label="Download data as CSV",
                               data=df.to_csv().encode('utf-8'),
                               file_name='pagespeed_insights.csv',
                               mime='text/csv')

if __name__ == "__main__":
    main()
