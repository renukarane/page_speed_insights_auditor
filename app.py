import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse

# ✅ Function to scrape sitemap with custom headers and XML parser
def scrape_sitemap(url):
    try:
        if not urlparse(url).scheme:
            url = 'https://' + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/xml,text/xml"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'xml')  # use XML parser
        urls = [element.text for element in soup.find_all('loc')]

        if not urls:
            st.warning("No URLs found in sitemap.")
        return urls

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sitemap: {e}")
        return []

# ✅ Function to get PageSpeed Insights using Google API
def get_pagespeed_insights(url, api_key):
    try:
        response = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={"url": url, "key": api_key}
        )
        response.raise_for_status()
        data = response.json()

        audits = data.get('lighthouseResult', {}).get('audits', {})
        return {
            'URL': url,
            'Score': data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score'),
            'First Contentful Paint': audits.get('first-contentful-paint', {}).get('displayValue'),
            'Speed Index': audits.get('speed-index', {}).get('displayValue'),
            'Largest Contentful Paint': audits.get('largest-contentful-paint', {}).get('displayValue'),
            'Time to Interactive': audits.get('interactive', {}).get('displayValue'),
            'Total Blocking Time': audits.get('total-blocking-time', {}).get('displayValue'),
            'Cumulative Layout Shift': audits.get('cumulative-layout-shift', {}).get('displayValue'),
        }

    except Exception as e:
        st.warning(f"Error processing {url}: {e}")
        return {
            'URL': url,
            'Score': None,
            'First Contentful Paint': None,
            'Speed Index': None,
            'Largest Contentful Paint': None,
            'Time to Interactive': None,
            'Total Blocking Time': None,
            'Cumulative Layout Shift': None,
        }

# ✅ Main Streamlit App
def main():
    st.title("🕸️ Sitemap Auditor + PageSpeed Insights")

    input_url = st.text_input("Enter sitemap URL (e.g., https://example.com/sitemap.xml)")
    api_key = st.secrets.get("pagespeed_api_key")

    if not api_key:
        st.error("⚠️ API key missing. Please add 'pagespeed_api_key' to your Streamlit secrets.")
        return

    if st.button("Scrape & Audit"):
        if not input_url:
            st.warning("Please enter a sitemap URL.")
            return

        urls = scrape_sitemap(input_url)
        total = len(urls)

        if total == 0:
            return

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        table_placeholder = st.empty()

        for i, url in enumerate(urls, start=1):
            insights = get_pagespeed_insights(url, api_key)
            results.append(insights)

            df = pd.DataFrame(results)
            table_placeholder.dataframe(df)

            progress_bar.progress(i / total)
            status_text.text(f"Processing {i}/{total}: {url}")

        progress_bar.empty()
        status_text.empty()

        if df is not None and not df.empty:
            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='pagespeed_insights.csv',
                mime='text/csv'
            )
        else:
            st.info("No results to download.")

if __name__ == "__main__":
    main()
