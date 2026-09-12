import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="مساهمات الجمعية", page_icon="💰", layout="centered")

st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    .stTextInput > label, .stNumberInput > label {
        text-align: right;
        width: 100%;
    }
    .stButton > button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "contributions.csv"
COLUMNS = ["التاريخ والوقت", "الاسم الكامل", "رقم الهاتف", "المبلغ"]

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=COLUMNS)

def save_contribution(name, phone, amount):
    df = load_data()
    new_row = {
        "التاريخ والوقت": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "الاسم الكامل": name,
        "رقم الهاتف": phone,
        "المبلغ": amount
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ---------- partie publique : tout le monde peut soumettre ----------
st.title("💰 منصة مساهمات الجمعية")
st.subheader("📝 تسجيل مساهمة جديدة")

with st.form("contribution_form", clear_on_submit=True):
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الهاتف")
    amount = st.number_input("المبلغ المتبرع به (درهم)", min_value=0.0, step=10.0)
    submitted = st.form_submit_button("✅ تأكيد المساهمة")

    if submitted:
        if name.strip() == "" or phone.strip() == "" or amount <= 0:
            st.error("يرجى تعبئة جميع الحقول بشكل صحيح.")
        else:
            save_contribution(name, phone, amount)
            st.success(f"تم تسجيل مساهمة {name} بمبلغ {amount:,.2f} درهم بنجاح! 🎉")
            st.rerun()

st.markdown("---")

# ---------- partie privée : réservée à l'admin, protégée par mot de passe ----------
with st.expander("🔒 لوحة التحكم (للمشرف فقط)"):
    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if pwd == st.secrets["general"]["admin_password"]:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
    else:
        df = load_data()
        total = df["المبلغ"].sum() if not df.empty else 0
        st.metric("إجمالي المساهمات المحصلة", f"{total:,.2f} درهم")

        if df.empty:
            st.info("لا توجد مساهمات مسجلة حتى الآن.")
        else:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ تنزيل نسخة احتياطية (CSV)", data=csv,
                                file_name="contributions_backup.csv", mime="text/csv")

        if st.button("🚪 تسجيل الخروج"):
            st.session_state.admin_ok = False
            st.rerun()

