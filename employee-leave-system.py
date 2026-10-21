import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64
import json
import os

# ضبط إعدادات الصفحة وتفعيل الواجهة الواسعة
st.set_page_config(
    page_title="النظام المتكامل لإدارة الإجازات",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔑 ملف الترخيص الخاص بهذه النسخة المباعة للعميل (يتم وضعه مسبقاً مع النسخة الخاصة بالشركة)
LICENSE_FILE = "client_license.json"

def get_client_license():
    """قراءة بيانات الترخيص والشركة الخاصة بهذه النسخة فقط"""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # بيانات افتراضية في حال لم يتم ايجاد ملف الترخيص
    return {
        "id": "company_default",
        "license": "LIC-1001",
        "name": "الشركة الموحدة للبرمجيات"
    }

# جلب بيانات الشركة والترخيص المخصص لهذه النسخة فقط (بدون إظهار بوابة الشركات)
client_data = get_client_license()
company_id = client_data["id"]
company_license = client_data["license"]
company_display_name = client_data["name"]

# مجلد تخزين بيانات الشركة الحالية المعزولة
COMPANIES_DIR = "client_companies_data"
if not os.path.exists(COMPANIES_DIR):
    os.makedirs(COMPANIES_DIR)

COMPANY_FILE = os.path.join(COMPANIES_DIR, f"{company_id}_data.json")

# ---------------------------------------------------------
# 💾 دوال الحفظ والاستعادة التلقائية المعزولة للشركة
# ---------------------------------------------------------
def load_company_data():
    """تحميل بيانات الشركة الحالية المعزولة تماماً مع ضمان وجود كافة الأعمدة"""
    if os.path.exists(COMPANY_FILE):
        try:
            with open(COMPANY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if "employees" in data and len(data["employees"]) > 0:
                    st.session_state.employees = pd.DataFrame(data["employees"])
                else:
                    st.session_state.employees = pd.DataFrame(columns=[
                        "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                        "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي",
                        "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي",
                        "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي"
                    ])

                if "requests" in data and len(data["requests"]) > 0:
                    st.session_state.requests = pd.DataFrame(data["requests"])
                else:
                    st.session_state.requests = pd.DataFrame(columns=[
                        "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الحالة"
                    ])

                if "users" in data and len(data["users"]) > 0:
                    st.session_state.users = pd.DataFrame(data["users"])
                else:
                    st.session_state.users = pd.DataFrame([
                        {"اسم المستخدم": "admin", "الاسم الكامل": "المدير العام", "الفرع التابع": "المركز الرئيسي", "القسم التابع": "الإدارة العليا", "الصلاحية": "مشرف عام (Admin)", "البريد الإلكتروني": "admin@company.com", "الحالة": "نشط", "الرسم السري": "1-2-3"}
                    ])

                if "company_info" in data:
                    st.session_state.company_info = data["company_info"]
        except Exception as e:
            st.error(f"خطأ في تحميل ملف الشركة: {e}")
    else:
        st.session_state.employees = pd.DataFrame([
            {
                "كود الموظف": "EMP001", "اسم الموظف": "أحمد محمود", "الوظيفة": "محاسب أول", "القسم": "الإدارة المالية", "الفرع": "المركز الرئيسي",
                "صلاحية الموظف": "اعتماد الطلبات",
                "رصيد سنوي (إجمالي)": 21, "سنوي مستهلك": 3, "سنوي متبقي": 18,
                "رصيد أسبوعي (إجمالي)": 4, "أسبوعي مستهلك": 1, "أسبوعي متبقي": 3,
                "رصيد رسمي (إجمالي)": 10, "رسمي مستهلك": 2, "رسمي متبقي": 8
            }
        ])
        st.session_state.requests = pd.DataFrame(columns=[
            "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الحالة"
        ])
        st.session_state.users = pd.DataFrame([
            {"اسم المستخدم": "admin", "الاسم الكامل": "المدير العام", "الفرع التابع": "المركز الرئيسي", "القسم التابع": "الإدارة العليا", "الصلاحية": "مشرف عام (Admin)", "البريد الإلكتروني": "admin@company.com", "الحالة": "نشط", "الرسم السري": "1-2-3"}
        ])
        st.session_state.company_info = {
            "name": company_display_name,
            "address": "القاهرة، جمهورية مصر العربية",
            "cr": "123456",
            "tax": "987-654-321",
            "contact": "هاتف: 01000000000 | بريد: info@company.com",
            "license": company_license,
            "logo": None
        }

def auto_save_data():
    """حفظ التغييرات في ملف هذه الشركة فقط"""
    try:
        data_to_save = {
            "employees": st.session_state.employees.to_dict(orient='records'),
            "requests": st.session_state.requests.to_dict(orient='records'),
            "users": st.session_state.users.to_dict(orient='records'),
            "company_info": st.session_state.company_info
        }
        with open(COMPANY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في الحفظ التلقائي: {e}")

load_company_data()
st.session_state.company_info["name"] = company_display_name
st.session_state.company_info["license"] = company_license

# 🎨 تصميم CSS مخصص لإخفاء الأشرطة الجانبية والتحكم بالمظهر
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    html, body, [class*="css"] {
        font-family: 'Tahoma', 'Segoe UI', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }
    .company-header-container {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 6px !important;
        width: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.15);
        box-sizing: border-box;
    }
    .header-top-system {
        text-align: center;
        width: 100%;
        margin-bottom: 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 3px;
    }
    .header-top-system h2 {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .header-bottom-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    .header-right-info { text-align: right; flex: 3; }
    .header-left-logo {
        flex: 1;
        text-align: left;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-left: 5px;
    }
    .comp-name-txt {
        font-size: 13px !important;
        font-weight: bold !important;
        margin-bottom: 1px !important;
        color: #ffffff !important;
    }
    .comp-info-txt {
        font-size: 10px !important;
        margin: 1px 0 !important;
        color: #e0e0e0 !important;
        line-height: 1.2;
    }
    .dashboard-card {
        background: #ffffff;
        border-right: 4px solid #1f4068;
        padding: 8px 10px;
        border-radius: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        text-align: right;
        margin-bottom: 6px;
    }
    .dashboard-card-title {
        font-size: 11px;
        color: #555555;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .dashboard-card-value {
        font-size: 20px;
        color: #1f4068;
        font-weight: bold;
    }
    .section-header {
        font-size: 13px !important;
        font-weight: bold !important;
        color: #1f4068 !important;
        border-bottom: 2px solid #1f4068;
        padding-bottom: 2px;
        margin-top: 6px !important;
        margin-bottom: 4px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    table.custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 2px !important;
        margin-bottom: 6px !important;
        background-color: #ffffff;
        color: #000000;
        direction: rtl;
        text-align: right;
    }
    table.custom-table th, table.custom-table td {
        border: 1px solid #333333;
        padding: 4px 8px;
        text-align: right;
        font-size: 11px;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    table.custom-table th {
        background-color: #f0f2f6 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# حالة المصادقة
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'current_logged_user' not in st.session_state:
    st.session_state.current_logged_user = ""
if 'current_user_dept' not in st.session_state:
    st.session_state.current_user_dept = ""
if 'current_user_branch' not in st.session_state:
    st.session_state.current_user_branch = ""
if 'current_user_role' not in st.session_state:
    st.session_state.current_user_role = ""

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "لوحة التحكم الرئيسية"

def render_printable_table(df):
    if df.empty:
        st.info("لا توجد بيانات متاحة للعرض.")
        return
    html = df.to_html(classes="custom-table", index=False, escape=False)
    st.markdown(html, unsafe_allow_html=True)

def render_company_header():
    info = st.session_state.company_info
    logo_html = '<div style="padding: 2px 4px; border: 1px dashed white; border-radius: 3px; font-size: 8px; color: white;">🏢 الشعار</div>'
    if info.get("logo") is not None:
        try:
            logo_html = f'<img src="data:image/png;base64,{info.get("logo")}" alt="Logo" style="max-height: 38px; max-width: 75px; object-fit: contain; background: white; border-radius: 3px; padding: 1px;" />'
        except Exception:
            pass
            
    st.markdown(f"""
        <div class="company-header-container">
            <div class="header-top-system">
                <h2>🏢 النظام المتكامل لإدارة الإجازات - شركة: {info.get("name", "")} (ترخيص: {info.get("license", "")})</h2>
            </div>
            <div class="header-bottom-content">
                <div class="header-right-info">
                    <div class="comp-name-txt">{info.get("name", "")}</div>
                    <div class="comp-info-txt">📍 {info.get("address", "")} &nbsp;|&nbsp; 📋 سجل: {info.get("cr", "")} &nbsp;|&nbsp; 🧾 ضريبي: {info.get("tax", "")} &nbsp;|&nbsp; 🔑 ترخيص: {info.get("license", "")}</div>
                    <div class="comp-info-txt">📞 {info.get("contact", "")}</div>
                </div>
                <div class="header-left-logo">
                    {logo_html}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 🔐 شاشة تسجيل الدخول المخصصة للشركة
if not st.session_state.is_authenticated:
    st.markdown(f"""
        <div style="max-width: 450px; margin: 40px auto; background: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; direction: rtl;">
            <h2 style="color: #1f4068; margin-bottom: 10px;">🔐 تسجيل الدخول - {company_display_name}</h2>
            <p style="color: #666; font-size: 13px;">رخصة النظام النشطة: {company_license}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("login_pattern_form"):
            usernames = st.session_state.users["اسم المستخدم"].tolist()
            selected_user_login = st.selectbox("اختر المستخدم", usernames)
            pattern_input = st.text_input("أدخل تسلسل الرسم السري", type="password", placeholder="مثل: 1-2-3")
            login_btn = st.form_submit_button("🔓 فتح قفل الدخول للنظام", use_container_width=True)
            
            if login_btn:
                user_record = st.session_state.users[st.session_state.users["اسم المستخدم"] == selected_user_login].iloc[0]
                stored_pattern = str(user_record["الرسم السري"])
                
                if pattern_input.strip() == stored_pattern.strip():
                    st.session_state.is_authenticated = True
                    st.session_state.current_logged_user = selected_user_login
                    st.session_state.current_user_dept = user_record["القسم التابع"]
                    st.session_state.current_user_branch = user_record["الفرع التابع"]
                    st.session_state.current_user_role = user_record["الصلاحية"]
                    st.session_state.active_tab = "لوحة التحكم الرئيسية"
                    st.success(f"مرحباً بك يا {user_record['الاسم الكامل']}! تم تسجيل الدخول بنجاح.")
                    st.rerun()
                else:
                    st.error("❌ الرسم السري غير صحيح!")
    st.stop()

# بعد نجاح المصادقة
render_company_header()

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6 = st.columns(6)
with col_nav1:
    if st.button("📈 لوحة التحكم", use_container_width=True): st.session_state.active_tab = "لوحة التحكم الرئيسية"
with col_nav2:
    if st.button("📝 طلب إجازة", use_container_width=True): st.session_state.active_tab = "تسجيل طلب إجازة"
with col_nav3:
    if st.button("👥 الموظفين", use_container_width=True): st.session_state.active_tab = "إدارة وفهرس الموظفين"
with col_nav4:
    if st.button("🔍 بحث متقدم", use_container_width=True): st.session_state.active_tab = "🔍 بحث متقدم"
with col_nav5:
    if st.button("🔒 المستخدمين", use_container_width=True): st.session_state.active_tab = "إدارة المستخدمين والصلاحيات"
with col_nav6:
    if st.button("🖨️ التقارير", use_container_width=True): st.session_state.active_tab = "🖨️ طباعة البيانات والتقارير"

col_sub1, col_sub2, col_sub3, col_sub4 = st.columns(4)
with col_sub1:
    if st.button("⚙️ إعدادات الشركة", use_container_width=True): st.session_state.active_tab = "⚙️ إعدادات وبيانات الشركة"
with col_sub2:
    if st.button("📥 تحميل Excel", use_container_width=True): st.session_state.active_tab = "📥 تحميل البيانات (Excel)"
with col_sub3:
    if st.button("💾 نسخة احتياطية", use_container_width=True): st.session_state.active_tab = "💾 النسخة الاحتياطية"
with col_sub4:
    if st.button("🗑️ مسح البيانات", use_container_width=True): st.session_state.active_tab = "🗑️ مسح وحذف البيانات"

col_info_bar, col_logout_bar = st.columns([5, 1])
with col_info_bar:
    st.markdown(f"""
        <div style="background: #eef2f7; padding: 6px 12px; border-radius: 4px; font-size: 11px; margin-bottom: 8px; color: #1f4068; font-weight: bold; display: flex; gap: 15px; direction: rtl;">
            <div>🏢 الشركة: {company_display_name}</div>