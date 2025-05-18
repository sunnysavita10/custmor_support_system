import streamlit as st
from data_scrapper.scrape_data import scrape_flipkart_products, save_to_csv
from data_ingestion.ingestion_pipeline import DataIngestion
import os

output_path = "data/product_reviews.csv"
st.title("📦 Product Review Scraper")

if "product_inputs" not in st.session_state:
    st.session_state.product_inputs = [""]

def add_product_input():
    st.session_state.product_inputs.append("")

st.subheader("📝 Optional Product Description")
product_description = st.text_area("Enter product description (used as an extra search keyword):")

st.subheader("🛒 Product Names")
updated_inputs = []
for i, val in enumerate(st.session_state.product_inputs):
    input_val = st.text_input(f"Product {i+1}", value=val, key=f"product_{i}")
    updated_inputs.append(input_val)
st.session_state.product_inputs = updated_inputs

st.button("➕ Add Another Product", on_click=add_product_input)

max_products = st.number_input("How many products per search?", min_value=1, max_value=10, value=1)
review_count = st.number_input("How many reviews per product?", min_value=1, max_value=10, value=2)

if st.button("🚀 Start Scraping"):
    product_inputs = [p.strip() for p in st.session_state.product_inputs if p.strip()]
    if product_description.strip():
        product_inputs.append(product_description.strip())

    if not product_inputs:
        st.warning("⚠️ Please enter at least one product name or a product description.")
    else:
        final_data = []
        for query in product_inputs:
            st.write(f"🔍 Searching for: {query}")
            results = scrape_flipkart_products(query, max_products=max_products, review_count=review_count)
            final_data.extend(results)

        unique_products = {}
        for row in final_data:
            if row[1] not in unique_products:
                unique_products[row[1]] = row
        # final_data = list(unique_products.values())

        # save_to_csv(final_data, output_path)
        
        final_data = list(unique_products.values())
        st.session_state["scraped_data"] = final_data  # ✅ store in session
        save_to_csv(final_data, output_path)
        st.success("✅ Data saved to `data/product_reviews.csv`")
        st.download_button("📥 Download CSV", data=open(output_path, "rb"), file_name="product_reviews.csv")

# This stays OUTSIDE "if st.button('Start Scraping')"
if "scraped_data" in st.session_state and st.button("🧠 Store in Vector DB (AstraDB)"):
    with st.spinner("📡 Initializing ingestion pipeline..."):
        try:
            ingestion = DataIngestion()
            st.info("🚀 Running ingestion pipeline...")
            ingestion.run_pipeline()
            st.success("✅ Data successfully ingested to AstraDB!")
        except Exception as e:
            st.error("❌ Ingestion failed!")
            st.exception(e)

