import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="Spy & Verify",
    page_icon="🕵️‍♂️",
    layout="centered"
)

# --- Hide Streamlit Branding ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    # Display Logo
    try:
        st.image("logo.jpg.png", use_container_width=True)
    except:
        st.warning("Logo not found. Please rename your image to 'logo.jpg.png'")
    
    st.markdown("---")
    
    # API Key Input
    st.header("🔑 Configuration")
    api_key = st.text_input("Enter SerpApi Key", type="password", help="Get your key from serpapi.com")
    
    st.sidebar.markdown("---")
st.sidebar.markdown("### 👑 Upgrade to PRO")
st.sidebar.markdown(
    """
    Unlock competitor links, prices, and CSV Export!
    The Monthly Subscription is only $19.
    """
)

# الرابط الفعلي لزر PayPal الذي أنشأته
paypal_link = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XH3ZKY7F6RSJJ" 

# عرض الزر الذي يفتح صفحة PayPal في متصفح جديد:
st.sidebar.markdown(f"[💳 Subscribe for $19/mo]({paypal_link})") 

# --- قسم معلومات التواصل ---

st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Contact Us")
st.sidebar.markdown("📧 Email: **luxurylifeinusa@gmail.com** (Working Email)")
st.sidebar.markdown("📱 WhatsApp/Call: **+213779921126**")
st.sidebar.markdown("---")

# نظام التحقق من الاشتراك عبر الكود السري
# الكود السري الرسمي للتطبيق هو Mishka@*2026
secret_premium_code = "Mishka@*2026"
secret_code_input = st.sidebar.text_input("Enter Access Code (For Premium Users)", type="password")

is_premium = (secret_code_input == secret_premium_code)

if is_premium:
    st.sidebar.success("User is: PREMIUM (Access Granted)")
elif secret_code_input != "":
    st.sidebar.error("Invalid Code. Please check or subscribe.")
else:
    st.sidebar.error("User is: FREE TIER")

# -----------------------------------------------------------------------

# --- Main Interface ---
st.title("Spy & Verify 🕵️‍♂️")
st.subheader("Uncover Your Dropshipping Competition")

product_name = st.text_input("Enter product name (e.g., Galaxy Projector)", placeholder="Type product name here...")
search_btn = st.button("🚀 Spy Now", use_container_width=True)

# --- Logic ---
if search_btn:
    if not api_key:
        st.error("⚠️ Please enter your SerpApi Key in the sidebar to start spying.")
    elif not product_name:
        st.warning("⚠️ Please enter a product name.")
    else:
        try:
            with st.spinner(f"Scanning the market for '{product_name}'..."):
                # Construct Query for Shopify Stores
                query = f"site:myshopify.com {product_name}"
                
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": api_key,
                    "num": 20  # Fetch top 20 results
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                # Process Results
                organic_results = results.get("organic_results", [])
                total_results_approx = results.get("search_information", {}).get("total_results", 0)
                
                # --- 1. The Saturation Gauge ---
                st.markdown("### 📊 Market Saturation Level")
                
                # Determine Competition Level
                count = len(organic_results) # Using fetched count for accuracy in this demo
                
                if count == 0:
                     st.error("No results found. Try a different keyword.")
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    if count < 5:
                        st.success(f"🟢 LOW COMPETITION\n\nFound: {count} Stores")
                    elif count < 15:
                        st.warning(f"🟡 MEDIUM COMPETITION\n\nFound: {count} Stores")
                    else:
                        st.error(f"🔴 SATURATED / HIGH RISK\n\nFound: {count}+ Stores")
                    
                    st.markdown("---")
                    
                    # --- 2. The Reveal (Freemium Logic) ---
                    st.markdown("### 🕵️‍♂️ Competitor List")
                    
                    if is_pro:
                        # Prepare Data for Table
                        data = []
                        for result in organic_results:
                            data.append({
                                "Store Title": result.get("title"),
                                "Link": result.get("link"),
                                "Snippet": result.get("snippet")
                            })
                        
                        df = pd.DataFrame(data)
                        
                        # Show Dataframe
                        st.dataframe(
                            df, 
                            column_config={
                                "Link": st.column_config.LinkColumn("Direct Link")
                            },
                            hide_index=True
                        )
                        
                        st.success(f"🔓 **PRO ACCESS UNLOCKED:** Revealed {len(data)} competitor links.")
                        
                        # Export Button (CSV)
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download Results (CSV)",
                            csv,
                            "competitors.csv",
                            "text/csv",
                            key='download-csv'
                        )
                        
                    else:
                        # Free User View - HIDDEN
                        st.warning(f"🔒 **HIDDEN CONTENT**")
                        st.info(f"We found **{len(organic_results)}** active competitors selling this item.")
                        
                        # Blur effect simulation with text
                        st.markdown("""
                        <div style="filter: blur(4px); opacity: 0.6; user-select: none;">
                        Store 1: Super Cool Gadgets - www.example.com<br>
                        Store 2: Best Home Decor - www.mystore.com<br>
                        Store 3: Galaxy Lights - www.lights.com<br>
                        ... and 15 more.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.error("🚀 **UPGRADE TO PRO** to see exact store links, prices, and ads.")

        except Exception as e:
            st.error(f"An error occurred: {e}")


