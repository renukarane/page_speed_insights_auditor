import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse

# Function to scrape the sitemap
def scrape_sitemap(url):
    try:
        if not urlparse(url).scheme:
            url = 'https://' + url

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        urls = [element.text for element in soup.find_all('loc')]
        return urls
    except Exception as e:
        st.error(f"Error fetching sitemap: {e}")
        return []

# Function to get PageSpeed Insights
def get_pagespeed_insights(url, api_key):
    try:
        response = requests.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                                params={"url": url, "key": api_key})
        data = response.json()

        insights = {
            'URL': url,
            'Overall Score': data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score'),
        }

        audits = data.get('lighthouseResult', {}).get('audits', {})

        insights.update({
            'First Contentful Paint': audits.get('first-contentful-paint', {}).get('displayValue'),
            'Speed Index': audits.get('speed-index', {}).get('displayValue'),
            'Largest Contentful Paint': audits.get('largest-contentful-paint', {}).get('displayValue'),
            'Time to Interactive': audits.get('interactive', {}).get('displayValue'),
            'Total Blocking Time': audits.get('total-blocking-time', {}).get('displayValue'),
            'Cumulative Layout Shift': audits.get('cumulative-layout-shift', {}).get('displayValue'),
        })

        return insights

    except Exception as e:
        st.warning(f"Failed to fetch PageSpeed Insights for {url}: {e}")
        return {'URL': url, 'Overall Score': None, 'First Contentful Paint': None, 'Speed Index': None,
                'Largest Contentful Paint': None, 'Time to Interactive': None, 'Total Blocking Time': None,
                'Cumulative Layout Shift': None}

# Main Streamlit app
def main():
    st.title("🕸️ Sitemap Scraper + PageSpeed Insights Auditor")

    input_url = st.text_input("Enter sitemap URL (e.g., https://example.com/sitemap.xml):")

    # API key from secrets
    api_key = st.secrets.get("pagespeed_api_key", None)

    if not api_key:
        st.error("⚠️ API key not found in Streamlit secrets. Please add 'pagespeed_api_key'.")
        return

    if st.button("Scrape and Analyze"):
        if not input_url:
            st.warning("Please enter a sitemap URL.")
            return

        scraped_urls = scrape_sitemap(input_url)
        total_urls = len(scraped_urls)

        if total_urls == 0:
            st.warning("No URLs found in sitemap.")
            return

        results = []
        progress_bar = st.progress(0)
        progress_text = st.empty()
        table_placeholder = st.empty()

        for index, url in enumerate(scraped_urls, start=1):
            insights = get_pagespeed_insights(url, api_key)
            results.append(insights)

            df = pd.DataFrame(results)
            table_placeholder.dataframe(df)

            progress_bar.progress(index / total_urls)
            progress_text.text(f"Processed {index}/{total_urls}")

        progress_bar.empty()
        progress_text.empty()

        # Final safety check
        if df is not None and not df.empty:
            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="pagespeed_insights.csv",
                mime="text/csv"
            )
        else:
            st.info("No valid data to download.")

if __name__ == "__main__":
    main()
