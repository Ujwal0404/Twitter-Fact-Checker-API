# app/frontend/app.py

import streamlit as st
import requests
import time
from datetime import datetime

def main():
    # Page config
    st.set_page_config(
        page_title="TruthTracker - AI Fact Checking",
        page_icon="🔍",
        layout="centered"
    )

    # Title and Description
    st.title("🔍 TruthTracker")
    st.markdown("### AI-Powered Fact-Checking System")
    
    st.write("Verify tweets and text claims using AI and multi-source verification.")

    # Input Selection
    check_type = st.radio("What would you like to fact-check?", ["Tweet", "Text"])

    if check_type == "Tweet":
        tweet_input = st.text_input(
            "Enter Tweet URL or ID:",
            placeholder="Enter tweet ID or full URL"
        )
        
        if st.button("Check Tweet", key="tweet_button"):
            if tweet_input:
                with st.spinner('Analyzing tweet...'):
                    try:
                        # API call
                        response = requests.post(
                            "http://localhost:8000/api/v1/check/tweet",
                            json={"tweet_id": tweet_input.strip()}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Display Results
                            st.success("Analysis Complete!")
                            
                            if data.get("results"):
                                results = data["results"]
                                
                                # Display each response section
                                for response in results.get("responses", []):
                                    st.markdown(f"---\n{response}")
                                
                                # Display analysis details
                                if "analysis" in results:
                                    analysis = results["analysis"]
                                    st.markdown("### Detailed Analysis")
                                    st.markdown(f"**Verdict:** {analysis.get('verdict', 'N/A')}")
                                    st.markdown(f"**Confidence:** {analysis.get('confidence', 'N/A')}")
                                    st.markdown(f"**Explanation:** {analysis.get('explanation', 'N/A')}")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
            else:
                st.warning("Please enter a tweet URL or ID")

    else:  # Text input
        text_input = st.text_area(
            "Enter text to fact-check:",
            placeholder="Type or paste the text you want to verify..."
        )
        
        if st.button("Check Text", key="text_button"):
            if text_input:
                with st.spinner('Analyzing text...'):
                    try:
                        # API call
                        response = requests.post(
                            "http://localhost:8000/api/v1/check/text",
                            json={"text": text_input}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Display Results
                            st.success("Analysis Complete!")
                            
                            if data.get("results"):
                                results = data["results"]
                                
                                # Display each response section
                                for response in results.get("responses", []):
                                    st.markdown(f"---\n{response}")
                                
                                # Display analysis details
                                if "analysis" in results:
                                    analysis = results["analysis"]
                                    st.markdown("### Detailed Analysis")
                                    st.markdown(f"**Verdict:** {analysis.get('verdict', 'N/A')}")
                                    st.markdown(f"**Confidence:** {analysis.get('confidence', 'N/A')}")
                                    st.markdown(f"**Explanation:** {analysis.get('explanation', 'N/A')}")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
            else:
                st.warning("Please enter some text to analyze")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p>Made with ❤️ by Your Name | 
            <a href="https://github.com/Ujwal0404/Twitter-Fact-Checker-Agent">GitHub</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
