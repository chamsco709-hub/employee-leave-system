import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64
import json
import os

# 🏢 مجلد مخصص لتخزين بيانات الشركات بشكل مستقل وعازل تماماً
COMPANIES_DIR = "client_companies_data"
if not os.path.exists(COMPANIES_DIR):
    os.makedirs(COMPANIES_DIR)

# ضبط إعدادات الصفحة وتفعيل الواجهة الواسعة
st.set_page_config(
    page_title="النظام المتكامل لإدارة الإجازات",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔐 شريط جانبي لإدخال كود الشركة المراد إدارتها (عزل تام للبيانات)
st.sidebar.title("🔐 بوابة ترخيص الشركات")
company_id = st.sidebar.text_input("أدخل كود الشركة (Company ID):", value="company_default")

# مسار ملف البيانات الخاص بالشركة الحالية فقط
COMPANY_FILE = os.path.join(COMPANIES_DIR, f"{company_id}_data.json")

# ---------------------------------------------------------
# 💾 دوال الحفظ والاستعادة التلقائية المعزولة لكل شركة
# ---------------------------------------------------------
def load_company_data():
    """تحميل بيانات الشركة الحالية المعزولة تماماً عن باقي الشركات"""
    if os.path.exists(COMPANY_FILE):
        try:
            with open(COMPANY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "employees" in data and len(data["employees"]) > 0:
                    st.session_state.employees = pd.DataFrame(data["employees"])
                if "requests" in data and len(data["requests"]) > 0:
                    st.session_state.requests = pd.DataFrame(data["requests"])
                if "users" in data and len(data["users"]) > 0:
                    st.session_state.users = pd.DataFrame(data["users"])
                if "company_info" in data:
                    st.session_state.company_info = data["company_info"]
        except Exception as e:
            st.error(f"خطأ في تحميل ملف الشركة: {e}")
    else:
        # تهيئة بيانات جديدة ونظيفة تماماً للشركة في حال كانت أول مرة تعمل فيها
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
            "name": f"شركة {company_id}",
            "address": "القاهرة، جمهورية مصر العربية",
            "cr": "123456",
            "tax": "987-654-321",
            "contact": "هاتف: 01000000000 | بريد: info@company.com",
            "logo": None
        }

def auto_save_data():
    """حفظ التغييرات في ملف الشركة الحالية فقط دون التأثير على أي شركة أخرى"""
    try:
        data_to_save = {
            "employees": st.session_state.employees.to_dict(orient='records'),
            "requests": st.session_state.requests.to_dict(orient='records'),
            "users": st.session_state.users.to_dict(orient='records'),
            "company_info": {
                "name": st.session_state.company_info.get("name"),
                "address": st.session_state.company_info.get("address"),
                "cr": st.session_state.company_info.get("cr"),
                "tax": st.session_state.company_info.get("tax"),
                "contact": st.session_state.company_info.get("contact")
            }
        }
        with open(COMPANY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في الحفظ التلقائي: {e}")

# استدعاء التحميل للشركة المحددة فوراً
load_company_data()

# 🎨 تصميم CSS مخصص
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
    .report-title {
        font-size: 12px !important;
        font-weight: bold !important;
        color: #1f4068 !important;
        text-align: right !important;
        direction: rtl !important;
        margin-top: 6px !important;
        margin-bottom: 4px !important;
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

# حالة المصادقة لتسجيل الدخول برسم النمط السري
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
        
    st.markdown(f"""
        <div class="company-header-container">
            <div class="header-top-system">
                <h2>🏢 النظام المتكامل لإدارة الإجازات (الشركة: {company_id})</h2>
            </div>
            <div class="header-bottom-content">
                <div class="header-right-info">
                    <div class="comp-name-txt">{info.get("name", "")}</div>
                    <div class="comp-info-txt">📍 {info.get("address", "")} &nbsp;|&nbsp; 📋 سجل: {info.get("cr", "")} &nbsp;|&nbsp; 🧾 ضريبي: {info.get("tax", "")}</div>
                    <div class="comp-info-txt">📞 {info.get("contact", "")}</div>
                </div>
                <div class="header-left-logo">
                    {logo_html}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 🔐 شاشة تسجيل الدخول برسم الأمان السري
if not st.session_state.is_authenticated:
    st.markdown(f"""
        <div style="max-width: 450px; margin: 40px auto; background: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; direction: rtl;">
            <h2 style="color: #1f4068; margin-bottom: 10px;">🔐 تسجيل الدخول ({company_id})</h2>
            <p style="color: #666; font-size: 13px;">اختر المستخدم وأدخل تسلسل النقاط للرسم السري</p>
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
            <div>🏢 الشركة: {company_id}</div>
            <div>👤 المستخدم: {st.session_state.current_logged_user}</div>
            <div>🏢 الفرع: {st.session_state.current_user_branch}</div>
            <div>🛡️ الصلاحية: {st.session_state.current_user_role}</div>
        </div>
    """, unsafe_allow_html=True)
with col_logout_bar:
    if st.button("🚪 خروج آمن", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_logged_user = ""
        st.rerun()

choice = st.session_state.active_tab

# المحتوى حسب التبويب المختار
if choice == "لوحة التحكم الرئيسية":
    st.markdown('<div class="section-header">📈 مؤشرات الأداء العامة للنظام</div>', unsafe_allow_html=True)
    
    branch_filter = st.session_state.current_user_branch
    dept_filter = st.session_state.current_user_dept
    
    if "Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter:
        view_employees = st.session_state.employees
        view_requests = st.session_state.requests
    else:
        view_employees = st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]
        view_requests = st.session_state.requests[st.session_state.requests["الفرع"] == branch_filter]
    
    total_emps = len(view_employees)
    pending_count = len(view_requests[view_requests['الحالة'] == 'قيد الانتظار']) if not view_requests.empty else 0
    accepted_count = len(view_requests[view_requests['الحالة'] == 'مقبول']) if not view_requests.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="dashboard-card"><div class="dashboard-card-title">👥 إجمالي موظفي الفرع</div><div class="dashboard-card-value">{total_emps}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="dashboard-card" style="border-right-color: #f0ad4e;"><div class="dashboard-card-title">⏳ الطلبات المعلقة</div><div class="dashboard-card-value" style="color: #f0ad4e;">{pending_count}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="dashboard-card" style="border-right-color: #5cb85c;"><div class="dashboard-card-title">✅ الطلبات المقبولة</div><div class="dashboard-card-value" style="color: #5cb85c;">{accepted_count}</div></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-header">📋 أرصدة إجازات موظفي الفرع</div>', unsafe_allow_html=True)
    render_printable_table(view_employees)
    
    st.markdown('<div class="section-header">⚡ مراجعة واعتماد طلبات الإجازات المباشرة</div>', unsafe_allow_html=True)
    if view_requests.empty:
        st.info("لا توجد طلبات إجازات مسجلة حالياً.")
    else:
        render_printable_table(view_requests)
        pending_reqs = view_requests[view_requests["الحالة"] == "قيد الانتظار"]
        if not pending_reqs.empty:
            st.markdown("#### 🔄 اتخاذ قرار بشأن الطلبات المعلقة:")
            col_id, col_action, col_btn = st.columns([2, 2, 1])
            with col_id: req_id = st.selectbox("اختر رقم الطلب", pending_reqs["رقم الطلب"].tolist(), key="quick_req_id")
            with col_action: action = st.radio("القرار", ["مقبول", "مرفوض"], horizontal=True, key="quick_action")
            with col_btn:
                st.write("")
                if st.button("تنفيذ القرار", use_container_width=True):
                    st.session_state.requests.loc[st.session_state.requests["رقم الطلب"] == req_id, "الحالة"] = action
                    if action == "مقبول":
                        row = st.session_state.requests[st.session_state.requests["رقم الطلب"] == req_id].iloc[0]
                        emp_code = row["كود الموظف"]
                        days = row["عدد الأيام"]
                        l_type = row["نوع الإجازة"]
                        if "سنوية" in l_type:
                            st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "سنوي مستهلك"] += days
                            st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "سنوي متبقي"] -= days
                        elif "أسبوعية" in l_type:
                            st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "أسبوعي مستهلك"] += days
                            st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "أسبوعي متبقي"] -= days
                        elif "رسمية" in l_type:
                            st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "رسمي مستهلك"] += days
                            st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "رسمي متبقي"] -= days
                    
                    auto_save_data()  # 💾 حفظ تلقائي معزول
                    st.success(f"تم تحديث الطلب #{req_id} وحفظ البيانات للشركة بنجاح!")
                    st.rerun()

elif choice == "تسجيل طلب إجازة":
    st.subheader("📝 تقديم طلب إجازة جديد للموظف")
    branch_filter = st.session_state.current_user_branch
    dept_filter = st.session_state.current_user_dept
    
    if "Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter:
        emp_list = st.session_state.employees["اسم الموظف"].dropna().astype(str).tolist()
    else:
        emp_list = st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]["اسم الموظف"].dropna().astype(str).tolist()
    
    if not emp_list:
        st.warning("لا توجد موظفون متاحون لتسجيل إجازة لهم.")
    else:
        with st.form("leave_form"):
            emp_name = st.selectbox("اسم الموظف", emp_list)
            leave_type = st.selectbox("نوع الإجازة", ["إجازة سنوية (Annual)", "إجازة أسبوعية / عارضة", "إجازة رسمية", "بدون أجر"])
            col_d1, col_d2 = st.columns(2)
            with col_d1: start_date = st.date_input("من تاريخ")
            with col_d2: end_date = st.date_input("إلى تاريخ")
            reason = st.text_area("سبب الإجازة / ملاحظات إضافية")
            submit = st.form_submit_button("إرسال طلب الإجازة للمراجعة")
            
            if submit:
                days = (end_date - start_date).days + 1
                if days <= 0:
                    st.error("خطأ: تاريخ النهاية يجب أن يكون بعد تاريخ البداية!")
                else:
                    emp_row = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_name].iloc[0]
                    emp_code = emp_row["كود الموظف"]
                    emp_job = emp_row["الوظيفة"]
                    emp_branch = emp_row["الفرع"]
                    
                    allowed = True
                    if "سنوية" in leave_type and days > emp_row["سنوي متبقي"]:
                        allowed = False
                        st.error(f"عفواً! رصيد الإجازات السنوية المتبقي لا يكفي.")
                    elif "أسبوعية" in leave_type and days > emp_row["أسبوعي متبقي"]:
                        allowed = False
                        st.error(f"عفواً! رصيد الإجازات الأسبوعية لا يكفي.")
                    elif "رسمية" in leave_type and days > emp_row["رسمي متبقي"]:
                        allowed = False
                        st.error(f"عفواً! رصيد الإجازات الرسمية لا يكفي.")
                        
                    if allowed:
                        new_req = {
                            "رقم الطلب": int(st.session_state.requests["رقم الطلب"].max() + 1) if not st.session_state.requests.empty else 101,
                            "كود الموظف": emp_code, "اسم الموظف": emp_name, "الوظيفة": emp_job, "الفرع": emp_branch,
                            "نوع الإجازة": leave_type, "من تاريخ": str(start_date), "إلى تاريخ": str(end_date), "عدد الأيام": days, "الحالة": "قيد الانتظار"
                        }
                        st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_req])], ignore_index=True)
                        auto_save_data()  # 💾 حفظ تلقائي معزول
                        st.success("تم تقديم طلب الإجازة وحفظه تلقائياً في ملف الشركة!")

elif choice == "إدارة وفهرس الموظفين":
    st.subheader("👥 دليل وأقسام الموظفين والفروع والوظائف والصلاحيات")
    
    with st.expander("➕ إضافة موظف جديد"):
        with st.form("add_employee_form"):
            c_code = st.text_input("كود الموظف")
            c_name = st.text_input("اسم الموظف الكامل")
            c_job = st.text_input("الوظيفة")
            c_dept = st.text_input("القسم")
            c_branch = st.text_input("الفرع")
            c_emp_permission = st.selectbox("صلاحية الموظف المخصصة", ["إدخال طلبات فقط", "اعتماد الطلبات", "مدير شؤون إدارية", "صلاحيات كاملة للقسم"])
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1: c_annual = st.number_input("الرصيد السنوي", min_value=0, value=21)
            with col_b2: c_weekly = st.number_input("الرصيد الأسبوعي", min_value=0, value=4)
            with col_b3: c_official = st.number_input("رصيد الإجازات الرسمية", min_value=0, value=10)
            
            add_emp_btn = st.form_submit_button("إضافة الموظف")
            if add_emp_btn:
                if c_code and c_name:
                    if c_code in st.session_state.employees["كود الموظف"].values:
                        st.error("كود الموظف موجود مسبقاً!")
                    else:
                        new_emp = {
                            "كود الموظف": c_code, "اسم الموظف": c_name, "الوظيفة": c_job, "القسم": c_dept, "الفرع": c_branch, "صلاحية الموظف": c_emp_permission,
                            "رصيد سنوي (إجمالي)": c_annual, "سنوي مستهلك": 0, "سنوي متبقي": c_annual,
                            "رصيد أسبوعي (إجمالي)": c_weekly, "أسبوعي مستهلك": 0, "أسبوعي متبقي": c_weekly,
                            "رصيد رسمي (إجمالي)": c_official, "رسمي مستهلك": 0, "رسمي متبقي": c_official
                        }
                        st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_emp])], ignore_index=True)
                        auto_save_data()  # 💾 حفظ تلقائي معزول
                        st.success("تم إضافة الموظف وحفظ البيانات تلقائياً!")
                        st.rerun()

    st.markdown("---")
    branch_filter = st.session_state.current_user_branch
    dept_filter = st.session_state.current_user_dept
    editable_emps = st.session_state.employees if ("Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter) else st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]
    emp_names_list = editable_emps["اسم الموظف"].dropna().astype(str).tolist()
    
    if emp_names_list:
        selected_emp_name = st.selectbox("اختر الموظف للتعديل أو الحذف", emp_names_list)
        emp_row = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp_name].iloc[0]
        
        with st.form("edit_delete_employee_form"):
            e_code = st.text_input("كود الموظف", value=str(emp_row["كود الموظف"]), disabled=True)
            e_name = st.text_input("اسم الموظف", value=str(emp_row["اسم الموظف"]))
            e_job = st.text_input("الوظيفة", value=str(emp_row.get("الوظيفة", "")))
            e_dept = st.text_input("القسم", value=str(emp_row["القسم"]))
            e_branch = st.text_input("الفرع", value=str(emp_row["الفرع"]))
            
            perms_list = ["إدخال طلبات فقط", "اعتماد الطلبات", "مدير شؤون إدارية", "صلاحيات كاملة للقسم"]
            e_emp_permission = st.selectbox("صلاحية الموظف المخصصة", perms_list, index=perms_list.index(emp_row["صلاحية الموظف"]) if emp_row["صلاحية الموظف"] in perms_list else 0)
            
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                e_annual = st.number_input("الرصيد السنوي", min_value=0, value=int(emp_row["رصيد سنوي (إجمالي)"]))
                e_annual_cons = st.number_input("سنوي مستهلك", min_value=0, value=int(emp_row["سنوي مستهلك"]))
            with col_e2:
                e_weekly = st.number_input("الرصيد الأسبوعي", min_value=0, value=int(emp_row["رصيد أسبوعي (إجمالي)"]))
                e_weekly_cons = st.number_input("أسبوعي مستهلك", min_value=0, value=int(emp_row["أسبوعي مستهلك"]))
            with col_e3:
                e_official = st.number_input("رصيد رسمي", min_value=0, value=int(emp_row["رصيد رسمي (إجمالي)"]))
                e_official_cons = st.number_input("رسمي مستهلك", min_value=0, value=int(emp_row["رسمي مستهلك"]))
                
            e_annual_rem = e_annual - e_annual_cons
            e_weekly_rem = e_weekly - e_weekly_cons
            e_official_rem = e_official - e_official_cons
            
            col_f1, col_f2 = st.columns(2)
            with col_f1: update_btn = st.form_submit_button("💾 حفظ التعديلات", use_container_width=True)
            with col_f2: delete_btn = st.form_submit_button("🗑️ حذف الموظف نهائياً", use_container_width=True)
                
            if update_btn:
                st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_row["كود الموظف"], [
                    "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                    "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي",
                    "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي",
                    "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي"
                ]] = [e_name, e_job, e_dept, e_branch, e_emp_permission, e_annual, e_annual_cons, e_annual_rem, e_weekly, e_weekly_cons, e_weekly_rem, e_official, e_official_cons, e_official_rem]
                auto_save_data()  # 💾 حفظ تلقائي معزول
                st.success("تم التحديث والحفظ التلقائي بنجاح!")
                st.rerun()
                
            if delete_btn:
                st.session_state.employees = st.session_state.employees[st.session_state.employees["كود الموظف"] != emp_row["كود الموظف"]].reset_index(drop=True)
                auto_save_data()  # 💾 حفظ تلقائي معزول
                st.warning("تم الحذف بنجاح!")
                st.rerun()

    st.markdown("---")
    render_printable_table(editable_emps)

elif choice == "🔍 بحث متقدم":
    st.subheader("🔍 شاشة البحث المتقدم بالخيارات المنسدلة")
    names_opt = ["الكل"] + sorted(st.session_state.employees["اسم الموظف"].dropna().astype(str).unique().tolist())
    branches_opt = ["الكل"] + sorted(st.session_state.employees["الفرع"].dropna().astype(str).unique().tolist())
    jobs_opt = ["الكل"] + sorted(st.session_state.employees["الوظيفة"].dropna().astype(str).unique().tolist())
    codes_opt = ["الكل"] + sorted(st.session_state.employees["كود الموظف"].dropna().astype(str).unique().tolist())
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_name = st.selectbox("اختر اسم الموظف", names_opt)
        sel_branch = st.selectbox("اختر الفرع", branches_opt)
    with col_s2:
        sel_job = st.selectbox("اختر الوظيفة", jobs_opt)
        sel_code = st.selectbox("اختر كود الموظف", codes_opt)
        
    results = st.session_state.employees.copy()
    if sel_name != "الكل": results = results[results["اسم الموظف"] == sel_name]
    if sel_branch != "الكل": results = results[results["الفرع"] == sel_branch]
    if sel_job != "الكل": results = results[results["الوظيفة"] == sel_job]
    if sel_code != "الكل": results = results[results["كود الموظف"] == sel_code]
        
    render_printable_table(results)

elif choice == "إدارة المستخدمين والصلاحيات":
    st.subheader("🔒 إدارة مستخدمي النظام وفروعهم وأقسامهم والصلاحيات والرسوم السرية")
    
    with st.expander("➕ إضافة مستخدم جديد"):
        with st.form("add_user_form"):
            u_username = st.text_input("اسم المستخدم")
            u_fullname = st.text_input("الاسم الكامل")
            u_email = st.text_input("البريد الإلكتروني")
            u_branch_target = st.text_input("الفرع التابع له")
            u_dept_target = st.text_input("القسم التابع له")
            u_role = st.selectbox("صلاحية المستخدم", ["مشرف عام (Admin)", "مفوض الموارد البشرية (HR Manager)", "مدير فرع / قسم", "مستخدم عادي (Viewer)"])
            u_status = st.selectbox("حالة الحساب", ["نشط", "موقوف"])
            u_pattern = st.text_input("الرسم السري (Pattern)", placeholder="مثل: 1-2-3")
            
            add_user_btn = st.form_submit_button("إضافة المستخدم")
            if add_user_btn:
                if u_username and u_fullname and u_pattern:
                    if u_username in st.session_state.users["اسم المستخدم"].values:
                        st.error("اسم المستخدم موجود مسبقاً!")
                    else:
                        new_user = {
                            "اسم المستخدم": u_username, "الاسم الكامل": u_fullname, "الفرع التابع": u_branch_target,
                            "القسم التابع": u_dept_target, "الصلاحية": u_role, "البريد الإلكتروني": u_email,
                            "الحالة": u_status, "الرسم السري": u_pattern
                        }
                        st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_user])], ignore_index=True)
                        auto_save_data()  # 💾 حفظ تلقائي معزول
                        st.success("تم إضافة المستخدم وحفظه تلقائياً!")
                        st.rerun()

    st.markdown("---")
    user_list = st.session_state.users["اسم المستخدم"].dropna().astype(str).tolist()
    if user_list:
        selected_username = st.selectbox("اختر اسم المستخدم للتعديل أو الحذف", user_list)
        user_row = st.session_state.users[st.session_state.users["اسم المستخدم"] == selected_username].iloc[0]
        
        with st.form("edit_delete_user_form"):
            e_uname = st.text_input("اسم المستخدم", value=str(user_row["اسم المستخدم"]), disabled=True)
            e_fullname = st.text_input("الاسم الكامل", value=str(user_row["الاسم الكامل"]))
            e_branch_target = st.text_input("الفرع التابع", value=str(user_row["الفرع التابع"]))
            e_dept_target = st.text_input("القسم التابع", value=str(user_row["القسم التابع"]))
            e_email = st.text_input("البريد الإلكتروني", value=str(user_row["البريد الإلكتروني"]))
            
            roles_list = ["مشرف عام (Admin)", "مفوض الموارد البشرية (HR Manager)", "مدير فرع / قسم", "مستخدم عادي (Viewer)"]
            e_role = st.selectbox("صلاحية المستخدم", roles_list, index=roles_list.index(user_row["الصلاحية"]) if user_row["الصلاحية"] in roles_list else 0)
            
            status_list = ["نشط", "موقوف"]
            e_status = st.selectbox("حالة الحساب", status_list, index=status_list.index(user_row["الحالة"]) if user_row["الحالة"] in status_list else 0)
            e_pattern = st.text_input("الرسم السري الجديد", value=str(user_row["الرسم السري"]))
            
            col_u1, col_u2 = st.columns(2)
            with col_u1: update_user_btn = st.form_submit_button("💾 حفظ تعديلات المستخدم", use_container_width=True)
            with col_u2: delete_user_btn = st.form_submit_button("🗑️ حذف المستخدم نهائياً", use_container_width=True)
                
            if update_user_btn:
                st.session_state.users.loc[st.session_state.users["اسم المستخدم"] == selected_username, [
                    "الاسم الكامل", "الفرع التابع", "القسم التابع", "البريد الإلكتروني", "الصلاحية", "الحالة", "الرسم السري"
                ]] = [e_fullname, e_branch_target, e_dept_target, e_email, e_role, e_status, e_pattern]
                auto_save_data()  # 💾 حفظ تلقائي معزول
                st.success("تم التحديث والحفظ التلقائي بنجاح!")
                st.rerun()
                
            if delete_user_btn:
                if len(st.session_state.users) <= 1:
                    st.error("لا يمكن حذف آخر مستخدم في النظام!")
                else:
                    st.session_state.users = st.session_state.users[st.session_state.users["اسم المستخدم"] != selected_username].reset_index(drop=True)
                    auto_save_data()  # 💾 حفظ تلقائي معزول
                    st.warning("تم الحذف بنجاح!")
                    st.rerun()

    display_users_df = st.session_state.users.drop(columns=["الرسم السري"], errors="ignore")
    render_printable_table(display_users_df)

elif choice == "🖨️ طباعة البيانات والتقارير":
    report_type = st.selectbox("اختر نوع التقرير المُراد طباعته:", [
        "تقرير شامل لجميع الموظفين",
        "تقرير مخصص حسب (اسم الموظف)",
        "تقرير مخصص حسب (الفرع)",
        "تقرير مخصص حسب (القسم)",
        "تقرير مخصص حسب (كود الموظف)"
    ])
    
    st.components.v1.html(
        '<div style="text-align: right; margin: 2px 0;">'
        '<button onclick="parent.window.print();" style="background-color: #1f4068; color: white; padding: 6px 12px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 12px; width: 100%;">'
        '🖨️ طباعة التقرير الحالي / حفظ PDF (اضغط هنا للطباعة)'
        '</button>'
        '</div>',
        height=38
    )
    
    branch_filter = st.session_state.current_user_branch
    dept_filter = st.session_state.current_user_dept
    is_admin_or_top = "Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter
    base_emps = st.session_state.employees if is_admin_or_top else st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]

    if report_type == "تقرير شامل لجميع الموظفين":
        render_printable_table(base_emps)
    elif report_type == "تقرير مخصص حسب (اسم الموظف)":
        emp_names = base_emps["اسم الموظف"].dropna().astype(str).tolist()
        if emp_names:
            chosen_name = st.selectbox("اختر اسم الموظف", emp_names)
            render_printable_table(base_emps[base_emps["اسم الموظف"] == chosen_name])
    elif report_type == "تقرير مخصص حسب (الفرع)":
        branches = base_emps["الفرع"].dropna().astype(str).unique().tolist()
        if branches:
            chosen_branch = st.selectbox("اختر الفرع", branches)
            render_printable_table(base_emps[base_emps["الفرع"].astype(str) == chosen_branch])
    elif report_type == "تقرير مخصص حسب (القسم)":
        departments = base_emps["القسم"].dropna().astype(str).unique().tolist()
        if departments:
            chosen_dept = st.selectbox("اختر القسم", departments)
            render_printable_table(base_emps[base_emps["القسم"].astype(str) == chosen_dept])
    elif report_type == "تقرير مخصص حسب (كود الموظف)":
        codes = base_emps["كود الموظف"].dropna().astype(str).unique().tolist()
        if codes:
            chosen_code = st.selectbox("اختر الكود", codes)
            render_printable_table(base_emps[base_emps["كود الموظف"].astype(str) == chosen_code])

elif choice == "⚙️ إعدادات وبيانات الشركة":
    st.subheader("⚙️ إعدادات وتعديل بيانات الشركة والشعار")
    
    with st.form("company_settings_form"):
        c_name = st.text_input("اسم الشركة / المؤسسة", value=st.session_state.company_info.get("name", ""))
        c_address = st.text_input("عنوان الشركة", value=st.session_state.company_info.get("address", ""))
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            c_cr = st.text_input("رقم السجل التجاري", value=st.session_state.company_info.get("cr", ""))
        with col_s2:
            c_tax = st.text_input("رقم البطاقة الضريبية", value=st.session_state.company_info.get("tax", ""))
            
        c_contact = st.text_area("بيانات التواصل", value=st.session_state.company_info.get("contact", ""))
        uploaded_logo = st.file_uploader("رفع أو تحديث شعار الشركة (Logo)", type=["png", "jpg", "jpeg"])
        
        save_settings = st.form_submit_button("حفظ التغييرات")
        
        if save_settings:
            st.session_state.company_info["name"] = c_name
            st.session_state.company_info["address"] = c_address
            st.session_state.company_info["cr"] = c_cr
            st.session_state.company_info["tax"] = c_tax
            st.session_state.company_info["contact"] = c_contact
            if uploaded_logo is not None:
                st.session_state.company_info["logo"] = uploaded_logo
            st.success("تم تحديث البيانات والشعار بنجاح!")
            st.rerun()

elif choice == "📥 تحميل البيانات (Excel)":
    st.subheader("📥 تصدير وتحميل بيانات النظام بصيغة Excel")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.employees.to_excel(writer, sheet_name='الموظفين', index=False)
        st.session_state.requests.to_excel(writer, sheet_name='سجل الإجازات', index=False)
        st.session_state.users.to_excel(writer, sheet_name='المستخدمين والصلاحيات', index=False)
    output.seek(0)
    st.download_button(label="تحميل ملف الإكسيل الآن", data=output, file_name=f"Leave_System_{company_id}_{datetime.now().strftime('%Y-%m-%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif choice == "💾 النسخة الاحتياطية":
    st.subheader("💾 إدارة النسخ الاحتياطية (تنزيل واستعادة)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        backup_dict = {
            "employees": st.session_state.employees.to_dict(orient='records'),
            "requests": st.session_state.requests.to_dict(orient='records'),
            "users": st.session_state.users.to_dict(orient='records')
        }
        st.download_button(
            label="💾 تحميل النسخة الاحتياطية للشركة (JSON)",
            data=json.dumps(backup_dict, ensure_ascii=False, indent=4),
            file_name=f"backup_{company_id}_{datetime.now().strftime('%Y-%m-%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_b2:
        uploaded_backup = st.file_uploader("اختر ملف النسخة الاحتياطية (.json)", type=["json"])
        if uploaded_backup is not None:
            if st.button("🔄 تأكيد واستعادة البيانات الآن", use_container_width=True):
                try:
                    data = json.load(uploaded_backup)
                    if "employees" in data and "requests" in data:
                        st.session_state.employees = pd.DataFrame(data["employees"])
                        st.session_state.requests = pd.DataFrame(data["requests"])
                        if "users" in data:
                            st.session_state.users = pd.DataFrame(data["users"])
                        auto_save_data()  # 💾 حفظ البيانات المستعادة تلقائياً
                        st.success("✅ تم استعادة النسخة الاحتياطية للشركة بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ ملف النسخة الاحتياطية غير صالح!")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

elif choice == "🗑️ مسح وحذف البيانات":
    st.subheader("🗑️ مسح كافة بيانات الشركة الحالية")
    confirm_clear = st.checkbox("تأكيد مسح كافة البيانات")
    if st.button("تفريغ البيانات", type="primary"):
        if confirm_clear:
            st.session_state.employees = pd.DataFrame(columns=[
                "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي",
                "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي",
                "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي"
            ])
            st.session_state.requests = pd.DataFrame(columns=[
                "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الحالة"
            ])
            st.session_state.users = pd.DataFrame(columns=[
                "اسم المستخدم", "الاسم الكامل", "الفرع التابع", "القسم التابع", "الصلاحية", "البريد الإلكتروني", "الحالة", "الرسم السري"
            ])
            auto_save_data()  # 💾 تحديث الملف المعزول بعد المسح
            st.success("تم مسح بيانات الشركة الحالية بنجاح!")
            st.rerun()