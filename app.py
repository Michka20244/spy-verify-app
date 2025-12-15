import streamlit as st
import pandas as pd
from serpapi import GoogleSearch
import time 

# ====================================================================
# 1. إعدادات الواجهة (Configuration - لتحسين الأداء والجمالية)
# ====================================================================

st.set_page_config(
    page_title="Spy & Verify: PRO Analyst", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)
st.sidebar.image("https://i.imgur.com/Qj0YfK7.png", use_column_width=True) 

# تهيئة حالة الجلسة لتتبع الاستخدام المجاني والمفتاح
if 'trial_used' not in st.session_state:
    st.session_state['trial_used'] = False
if 'is_premium' not in st.session_state:
    st.session_state['is_premium'] = False
if 'serpapi_key' not in st.session_state: # تخزين مفتاح SerpApi
    st.session_state['serpapi_key'] = ''


# ====================================================================
# 2. نظام الدفع والوصول (Sidebar - الشريط الجانبي الثابت)
# ====================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='text-align: center; color: #F4D03F;'>👑 Access & Payments </h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

paypal_link = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XH3ZKY7F6RSJJ" 
st.sidebar.markdown(f"**💰 Monthly Subscription: $19**")
st.sidebar.markdown(f"[💳 Click Here to Subscribe via PayPal]({paypal_link})") 

# نظام التحقق من الاشتراك عبر الكود السري أو التجربة المجانية
secret_premium_code = "Mishka@*2026"
trial_code = "FREEFIRSTSPY"

# 1. إدخال الكود
st.sidebar.markdown("---")
access_code_input = st.sidebar.text_input("🔑 Enter Access Code (Premium/Trial)", type="password")

# 2. تحديد حالة العضوية
if access_code_input == secret_premium_code:
    st.session_state['is_premium'] = True
    st.session_state['trial_used'] = True 
elif access_code_input == trial_code and not st.session_state['trial_used']:
    st.session_state['is_premium'] = True
    st.sidebar.warning("This is your FREE TRIAL. Results will be locked after next use!")
else:
    # لا نغير حالة is_premium إذا لم يكن هناك كود صحيح
    if access_code_input and access_code_input != secret_premium_code:
        st.sidebar.error("Invalid Code or Trial already used.")

# 3. عرض الحالة
if st.session_state['is_premium']:
    st.sidebar.success("User Status: PREMIUM (Access Granted)")
else:
    st.sidebar.error("User Status: FREE TIER (Access Denied)")

# --- معلومات التواصل ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Contact Support")
st.sidebar.markdown("📧 Email: **luxurylifeinusa@gmail.com**")
st.sidebar.markdown("📱 WhatsApp/Call: **+213779921126**")
st.sidebar.markdown("---")

# ====================================================================
# 3. المنطقة الرئيسية للتطبيق (Main App Area)
# ====================================================================

st.title("🕵️‍♂️ Spy & Verify: Dropshipping Market Analyst")
st.markdown("### Uncover Hidden Competitors & Validate Product Potential in Real-Time.")

# 1. إدخال اسم المنتج
product_name = st.text_input("Enter product name (e.g., Galaxy Projector, Mini drone)", placeholder="Type product name here...", help="Enter the exact product name you wish to analyze.")

# 2. اختيار المنصة (Dropdown for Multi-Platform Search)
platform = st.selectbox(
    "🔬 Select Target Platform for Analysis:",
    ["Shopify Stores (Competitor Count)", "Amazon Review Spy (Product Weakness)", "Facebook/Instagram Ads (Active Campaigns)", "TikTok/YouTube Virality (Trend Check)"],
    index=0,
    help="Choose the platform to check for saturation, reviews, or advertising activity."
)

# 3. تحديد المناطق الجغرافية
REGION_MAP = {
    "United States (US)": {"location": "United States", "gl": "us"},
    "Europe (UK Hub)": {"location": "United Kingdom", "gl": "uk"},
    "Canada (CA)": {"location": "Canada", "gl": "ca"},
    "Australia (AU)": {"location": "Australia", "gl": "au"},
    "China (CN)": {"location": "China", "gl": "cn"},
}
selected_regions = st.multiselect(
    "🌍 Select Target Markets (Regions):",
    list(REGION_MAP.keys()),
    default=["United States (US)", "Europe (UK Hub)", "Canada (CA)"],
    help="Select regions for deep, localized competitor analysis. Each region provides 20 top results."
)

# 4. زر البدء
search_button = st.button('🚀 Spy Now')

# 5. منطقة إدخال مفتاح SerpApi (لضمان وجوده في كل عملية)
# تخزين المفتاح في حالة الجلسة
serpapi_key_input = st.text_input(
    "Enter SerpApi Key", 
    value=st.session_state['serpapi_key'], 
    type="password", 
    help="We store this key only for the current session. Get yours from SerpApi."
)
# تحديث حالة الجلسة
if serpapi_key_input:
    st.session_state['serpapi_key'] = serpapi_key_input


# 6. دالة البحث (Search Function - تدعم البحث المتعدد)
def run_search(product, platform_choice, api_key, regions_list):
    if not api_key:
        return None, "SerpApi Key Missing. Please enter your key in the sidebar."
    if not regions_list:
        return None, "Please select at least one region to search."

    # تحديد معامل البحث بناءً على اختيار المنصة (تحسين بحث TikTok)
    search_query = product
    if platform_choice == "Shopify Stores (Competitor Count)":
        search_query = f"site:myshopify.com {product}"
    elif platform_choice == "Amazon Review Spy (Product Weakness)":
        search_query = f"site:amazon.com reviews {product}"
    elif platform_choice == "Facebook/Instagram Ads (Active Campaigns)":
        search_query = f"facebook.com/ads/library OR instagram {product}"
    elif platform_choice == "TikTok/YouTube Virality (Trend Check)":
        # بحث أوسع وأكثر فاعلية 
        search_query = f"{product} viral review (site:tiktok.com OR site:youtube.com)" 

    all_results = []
    
    for region_name in regions_list:
        region_params = REGION_MAP.get(region_name)
        st.info(f"Sub-Search: Fetching 20 results for {region_name}...")
        
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": api_key,
            "location": region_params["location"], 
            "gl": region_params["gl"],           
            "hl": "en",
            "num": 20 # جلب 20 نتيجة من كل منطقة
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            if 'organic_results' in results:
                for res in results['organic_results']:
                    res['region'] = region_name
                all_results.extend(results['organic_results'])
            else:
                st.warning(f"No organic results found for {region_name}.")

        except Exception as e:
            st.error(f"API Error for {region_name}: {e}")
            
    if all_results:
        df_all = pd.DataFrame(all_results)
        df_unique = df_all.drop_duplicates(subset=['link'], keep='first')
        return df_unique.to_dict('records'), None
    else:
        return None, "No unique results found across the selected regions."


# 7. معالجة النتائج
if search_button and product_name and selected_regions:
    # 7.1. معالجة الاستخدام التجريبي لمرة واحدة
    if access_code_input == trial_code and not st.session_state['trial_used']:
        st.session_state['trial_used'] = True 
        st.experimental_rerun() 

    # 7.2. جلب النتائج
    st.info(f"🔎 Starting Deep Analysis for: {product_name}...")
    results, error = run_search(product_name, platform, st.session_state['serpapi_key'], selected_regions)

    if error:
        st.error(error)
    elif results:
        df = pd.DataFrame(results)

        # 7.3. تحليل التشبع بالألوان (Shopify)
        competitor_count = len(df[df['link'].astype(str).str.contains('myshopify.com')]) if platform == "Shopify Stores (Competitor Count)" else len(df)
        
        st.markdown("---")
        st.subheader("📊 Market Analysis:")

        if platform == "Shopify Stores (Competitor Count)":
            # تطبيق الألوان الثلاثة المتفق عليها
            if competitor_count <= 10:
                saturation = "🟢 LOW COMPETITION (High Potential)"
                st.success(f"Saturation Level: **{saturation}**")
            elif competitor_count <= 30:
                saturation = "🟡 MEDIUM COMPETITION (Moderate Risk)"
                st.warning(f"Saturation Level: **{saturation}**")
            else:
                saturation = "🔴 HIGH COMPETITION (High Risk - Avoid)"
                st.error(f"Saturation Level: **{saturation}**")
            st.markdown(f"**Found:** {competitor_count} unique active competitors across selected regions.")

        else:
             st.info(f"Found {competitor_count} relevant unique links across selected regions.")
        
        st.markdown("---")
        st.subheader("🔗 Deep Competitor List (Clickable Links):")
        
        # 7.4. حاجز الاشتراك (Paywall Logic)
        if st.session_state['is_premium']:
            # إنشاء عمود جديد للروابط القابلة للنقر (الحل لمشكلة الروابط)
            df['Action Link'] = df['link'].apply(lambda x: f'<a href="{x}" target="_blank">Click to Visit</a>')
            
            # عرض النتائج الكاملة للمشتركين (باستخدام st.markdown و unsafe_allow_html)
            st.markdown(df[['title', 'Action Link', 'region', 'snippet']].to_html(escape=False), unsafe_allow_html=True)

            # زر التحميل
            csv = df[['title', 'link', 'region', 'snippet']].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv,
                file_name=f'{product_name}_global_spy.csv',
                mime='text/csv',
            )
        else:
            # حجب النتائج للمستخدمين المجانيين
            st.error("🔒 HIDDEN CONTENT: Upgrade to PRO to unlock all results, full links, and multi-region data.")
            # عرض أول 5 نتائج مع إخفاء الروابط
            df_masked = df[['title', 'link', 'region', 'snippet']].head(5).copy()
            df_masked['link'] = df_masked['link'].astype(str).str.replace('https://', 'h**s://').str.replace('.com', '.***').str[:30] + '...'
            st.code(df_masked.to_markdown(index=False), language='markdown')
            
# 8. إظهار رسالة البداية إذا لم يتم إدخال شيء (الحل لمشكلة التجربة المجانية)
else:
    if not product_name and not st.session_state['is_premium']:
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #007bff;'>🎁 إبهار البداية: جرب تحليل PRO مجاناً لمرة واحدة!</h2>", unsafe_allow_html=True)
        st.warning(f"💡 Tip: Enter the Access Code **{trial_code}** in the sidebar to unlock a one-time full analysis!")
        st.markdown("---")
