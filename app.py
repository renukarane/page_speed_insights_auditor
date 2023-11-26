# Streamlit app
def main():
    st.title("Sitemap Scraper and PageSpeed Insights")
    input_url = st.text_input("Enter the URL of the sitemap (e.g., https://example.com/sitemap.xml):")

    # Retrieve the API key from Streamlit secrets
    api_key = st.secrets["pagespeed"]["api_key"]
    
    if st.button("Scrape and Analyze"):
        if input_url:
            scraped_urls = scrape_sitemap(input_url)
            results = []
            for url in scraped_urls:
                insights = get_pagespeed_insights(url, api_key)
                # Process the insights data as needed
                results.append({"URL": url, "Insights": insights})
            
            df = pd.DataFrame(results)
            st.write(df)

            # Download link for DataFrame
            st.download_button(label="Download data as CSV",
                               data=df.to_csv().encode('utf-8'),
                               file_name='pagespeed_insights.csv',
                               mime='text/csv')

if __name__ == "__main__":
    main()
