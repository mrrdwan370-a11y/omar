import streamlit as st
from datetime import date

# ======================
# PAGE CONFIG
# ======================
st.set_page_config("Hospital System", layout="wide")

# ======================
# STYLE (مختصر)
# ======================
st.markdown("""
<style>
.stApp { background: linear-gradient(to right, #0f172a, #1e293b, #334155); font-family: 'Segoe UI', sans-serif; }
section[data-testid="stSidebar"] { background: linear-gradient(to bottom, #141e30, #243b55); color: white; }
button { background: linear-gradient(to right, #1e3c72, #2a5298) !important; color: white !important; border-radius: 8px !important; font-weight: bold !important; }
input, textarea, select { border-radius: 8px !important; border: 1px solid #1e3c72 !important; }
thead tr th { background-color: #1e3c72 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ======================
# USERS
# ======================
users = {"admin":"1234","doctor":"1111","reception":"2222"}

# ======================
# SESSION INIT
# ======================
if "login" not in st.session_state:
    st.session_state.login = False

for k in ["doctors","patients","appointments","visits","prescriptions"]:
    if k not in st.session_state:
        st.session_state[k] = []
if "payments" not in st.session_state:
    st.session_state["payments"] = []

# ======================
# CLASSES
# ======================
class Doctor:
    def __init__(self,id,name,specialty):
            self.id=id; self.name=name; self.specialty=specialty

class Patient:
    def __init__(self,id,name,age):
        self.id=id; self.name=name; self.age=age

class Appointment:
    def __init__(self,id,patient,doctor,date):
        self.id=id; self.patient=patient; self.doctor=doctor; self.date=date

class Visit:
    def __init__(self,id,patient,doctor,date,diagnosis):
        self.id=id; self.patient=patient; self.doctor=doctor; self.date=date; self.diagnosis=diagnosis

class Prescription:
    def __init__(self,id,patient,doctor,meds,notes):
        self.id=id; self.patient=patient; self.doctor=doctor; self.meds=meds; self.notes=notes

class Payment:
    def __init__(self, id, patient, visit_id, amount, date):
        self.id = id              # رقم تعريف الدفع
        self.patient = patient    # اسم المريض
        self.visit_id = visit_id  # رقم الزيارة المرتبطة بالدفع
        self.amount = amount      # قيمة الدفع
        self.date = date          # تاريخ الدفع

# ======================
# LOGIN
# ======================
if not st.session_state.login:
    st.title("🏥 Hospital System Login")
    user = st.text_input("Username", key="login_user")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("LOGIN", key="login_btn"):
        if user in users and users[user] == pwd:
            st.success("Welcome ✅")
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Wrong Login ❌")
    st.stop()

# ======================
# SIDEBAR
# ======================
st.sidebar.success("✅ Logged in")
if st.sidebar.button("LOGOUT", key="logout_btn"):
    st.session_state.login = False
    st.rerun()

menu = st.sidebar.radio("MENU", ["Doctors","Patients","Appointments","Visits","Prescriptions","Payments"], key="main_menu")

# ======================
# HELPERS
# ======================
def safe_next(lst, attr, value):
    return next((x for x in lst if getattr(x, attr) == value), None)

def delete_item(lst, attr, value):
    obj = safe_next(lst, attr, value)
    if obj:
        lst.remove(obj)
        st.success("Deleted ✅")
        st.rerun()
    else:
        st.error("Item not found")

# ======================
# DOCTORS
# ======================
if menu == "Doctors":
    st.header("👨‍⚕️ Doctors")
    t = st.tabs(["View","Add","Edit","Delete"])

    # VIEW
    with t[0]:
        q = st.text_input("Search by name or specialty", key="doc_view_search")
        data = st.session_state.doctors
        if q:
            data = [d for d in data if q.lower() in d.name.lower() or q.lower() in d.specialty.lower()]
        st.table([vars(x) for x in data]) if data else st.info("No doctors")

    # ADD
    with t[1]:
        id_in = st.text_input("ID", key="doc_add_id")
        name_in = st.text_input("Name", key="doc_add_name")
        sp_in = st.text_input("Specialty", key="doc_add_sp")
        if st.button("ADD Doctor", key="doc_add_btn"):
            st.session_state.doctors.append(Doctor(id_in.strip(), name_in.strip(), sp_in.strip()))
            st.success("Doctor added ✅")
            st.rerun()

    # EDIT
    with t[2]:
        if not st.session_state.doctors:
            st.info("No doctors to edit")
        else:
            options = [f"{d.name} ({d.id})" for d in st.session_state.doctors]
            sel = st.selectbox("Select doctor to edit", options, key="doc_edit_select")
            # parse selection to find by id
            sel_id = sel.split("(")[-1].rstrip(")") if "(" in sel else None
            d = safe_next(st.session_state.doctors, "id", sel_id)
            if d:
                new_id = st.text_input("ID", value=d.id, key="doc_edit_id")
                new_name = st.text_input("Name", value=d.name, key="doc_edit_name")
                new_sp = st.text_input("Specialty", value=d.specialty, key="doc_edit_sp")
                if st.button("SAVE Doctor", key="doc_save_btn"):
                    d.id = new_id.strip(); d.name = new_name.strip(); d.specialty = new_sp.strip()
                    st.success("Doctor updated ✅")
                    st.rerun()
            else:
                st.error("Selected doctor not found")

    # DELETE
    with t[3]:
        if not st.session_state.doctors:
            st.info("No doctors to delete")
        else:
            options = [f"{d.name} ({d.id})" for d in st.session_state.doctors]
            sel = st.selectbox("Select doctor to delete", options, key="doc_del_select")
            sel_id = sel.split("(")[-1].rstrip(")") if "(" in sel else None
            if st.button("DELETE Doctor", key="doc_del_btn"):
                delete_item(st.session_state.doctors, "id", sel_id)

# ======================
# PATIENTS
# ======================
if menu == "Patients":
    st.header("🧑 Patients")
    t = st.tabs(["View","Add","Edit","Delete"])

    with t[0]:
        q = st.text_input("Search by name", key="pat_view_search")
        data = st.session_state.patients
        if q:
            data = [p for p in data if q.lower() in p.name.lower()]
        st.table([vars(x) for x in data]) if data else st.info("No patients")

    with t[1]:
        id_in = st.text_input("ID", key="pat_add_id")
        name_in = st.text_input("Name", key="pat_add_name")
        age_in = st.number_input("Age", 1, 120, key="pat_add_age")
        if st.button("ADD Patient", key="pat_add_btn"):
            st.session_state.patients.append(Patient(id_in.strip(), name_in.strip(), int(age_in)))
            st.success("Patient added ✅")
            st.rerun()

    with t[2]:
        if not st.session_state.patients:
            st.info("No patients to edit")
        else:
            options = [f"{p.name} ({p.id})" for p in st.session_state.patients]
            sel = st.selectbox("Select patient to edit", options, key="pat_edit_select")
            sel_id = sel.split("(")[-1].rstrip(")")
            p = safe_next(st.session_state.patients, "id", sel_id)
            if p:
                new_id = st.text_input("ID", value=p.id, key="pat_edit_id")
                new_name = st.text_input("Name", value=p.name, key="pat_edit_name")
                new_age = st.number_input("Age", 1, 120, value=p.age, key="pat_edit_age")
                if st.button("SAVE Patient", key="pat_save_btn"):
                    p.id = new_id.strip(); p.name = new_name.strip(); p.age = int(new_age)
                    st.success("Patient updated ✅")
                    st.rerun()
            else:
                st.error("Selected patient not found")

    with t[3]:
        if not st.session_state.patients:
            st.info("No patients to delete")
        else:
            options = [f"{p.name} ({p.id})" for p in st.session_state.patients]
            sel = st.selectbox("Select patient to delete", options, key="pat_del_select")
            sel_id = sel.split("(")[-1].rstrip(")")
            if st.button("DELETE Patient", key="pat_del_btn"):
                delete_item(st.session_state.patients, "id", sel_id)

# ======================
# APPOINTMENTS
# ======================
if menu == "Appointments":
    st.header("📅 Appointments")
    t = st.tabs(["View","Add","Edit","Delete"])

    with t[0]:
        st.table([vars(x) for x in st.session_state.appointments]) if st.session_state.appointments else st.info("No appointments")

    with t[1]:
        id_in = st.text_input("ID", key="app_add_id")
        pat_opt = [f"{p.name} ({p.id})" for p in st.session_state.patients] if st.session_state.patients else []
        doc_opt = [f"{d.name} ({d.id})" for d in st.session_state.doctors] if st.session_state.doctors else []
        pat_sel = st.selectbox("Patient", pat_opt, key="app_add_pat") if pat_opt else st.text_input("Patient ID/Name", key="app_add_pat_text")
        doc_sel = st.selectbox("Doctor", doc_opt, key="app_add_doc") if doc_opt else st.text_input("Doctor ID/Name", key="app_add_doc_text")
        date_in = st.date_input("Date", date.today(), key="app_add_date")
        if st.button("ADD Appointment", key="app_add_btn"):
            pat_val = pat_sel.split("(")[0].strip() if isinstance(pat_sel, str) and "(" in pat_sel else pat_sel
            doc_val = doc_sel.split("(")[0].strip() if isinstance(doc_sel, str) and "(" in doc_sel else doc_sel
            st.session_state.appointments.append(Appointment(id_in.strip(), pat_val, doc_val, str(date_in)))
            st.success("Appointment added ✅")
            st.rerun()

    with t[2]:
        if not st.session_state.appointments:
            st.info("No appointments to edit")
        else:
            options = [a.id for a in st.session_state.appointments]
            sel = st.selectbox("Select appointment (ID)", options, key="app_edit_select")
            a = safe_next(st.session_state.appointments, "id", sel)
            if a:
                new_date = st.text_input("Date", value=a.date, key="app_edit_date")
                new_pat = st.text_input("Patient", value=a.patient, key="app_edit_pat")
                new_doc = st.text_input("Doctor", value=a.doctor, key="app_edit_doc")
                if st.button("SAVE Appointment", key="app_save_btn"):
                    a.date = new_date.strip(); a.patient = new_pat.strip(); a.doctor = new_doc.strip()
                    st.success("Appointment updated ✅")
                    st.rerun()
            else:
                st.error("Appointment not found")

    with t[3]:
        if not st.session_state.appointments:
            st.info("No appointments to delete")
        else:
            options = [a.id for a in st.session_state.appointments]
            sel = st.selectbox("Select appointment to delete", options, key="app_del_select")
            if st.button("DELETE Appointment", key="app_del_btn"):
                delete_item(st.session_state.appointments, "id", sel)

# ======================
# VISITS
# ======================
if menu == "Visits":
    st.header("📋 Visits")
    t = st.tabs(["View","Add","Edit","Delete"])

    with t[0]:
        st.table([vars(x) for x in st.session_state.visits]) if st.session_state.visits else st.info("No visits")

    with t[1]:
        id_in = st.text_input("ID", key="visit_add_id")
        pat_opt = [f"{p.name} ({p.id})" for p in st.session_state.patients] if st.session_state.patients else []
        doc_opt = [f"{d.name} ({d.id})" for d in st.session_state.doctors] if st.session_state.doctors else []
        pat_sel = st.selectbox("Patient", pat_opt, key="visit_add_pat") if pat_opt else st.text_input("Patient", key="visit_add_pat_text")
        doc_sel = st.selectbox("Doctor", doc_opt, key="visit_add_doc") if doc_opt else st.text_input("Doctor", key="visit_add_doc_text")
        date_in = st.date_input("Date", date.today(), key="visit_add_date")
        diag_in = st.text_area("Diagnosis", key="visit_add_diag")
        if st.button("ADD Visit", key="visit_add_btn"):
            pat_val = pat_sel.split("(")[0].strip() if isinstance(pat_sel, str) and "(" in pat_sel else pat_sel
            doc_val = doc_sel.split("(")[0].strip() if isinstance(doc_sel, str) and "(" in doc_sel else doc_sel
            st.session_state.visits.append(Visit(id_in.strip(), pat_val, doc_val, str(date_in), diag_in.strip()))
            st.success("Visit added ✅")
            st.rerun()

    with t[2]:
        if not st.session_state.visits:
            st.info("No visits to edit")
        else:
            options = [v.id for v in st.session_state.visits]
            sel = st.selectbox("Select visit (ID)", options, key="visit_edit_select")
            v = safe_next(st.session_state.visits, "id", sel)
            if v:
                new_diag = st.text_area("Diagnosis", value=v.diagnosis, key="visit_edit_diag")
                if st.button("SAVE Visit", key="visit_save_btn"):
                    v.diagnosis = new_diag.strip()
                    st.success("Visit updated ✅")
                    st.rerun()
            else:
                st.error("Visit not found")

    with t[3]:
        if not st.session_state.visits:
            st.info("No visits to delete")
        else:
            options = [v.id for v in st.session_state.visits]
            sel = st.selectbox("Select visit to delete", options, key="visit_del_select")
            if st.button("DELETE Visit", key="visit_del_btn"):
                delete_item(st.session_state.visits, "id", sel)

# ======================
# PRESCRIPTIONS
# ======================
if menu == "Prescriptions":
    st.header("💊 Prescriptions")
    t = st.tabs(["View","Add","Edit","Delete"])

    with t[0]:
        st.table([vars(x) for x in st.session_state.prescriptions]) if st.session_state.prescriptions else st.info("No prescriptions")

    with t[1]:
        id_in = st.text_input("ID", key="pres_add_id")
        pat_opt = [f"{p.name} ({p.id})" for p in st.session_state.patients] if st.session_state.patients else []
        doc_opt = [f"{d.name} ({d.id})" for d in st.session_state.doctors] if st.session_state.doctors else []
        pat_sel = st.selectbox("Patient", pat_opt, key="pres_add_pat") if pat_opt else st.text_input("Patient", key="pres_add_pat_text")
        doc_sel = st.selectbox("Doctor", doc_opt, key="pres_add_doc") if doc_opt else st.text_input("Doctor", key="pres_add_doc_text")
        meds_in = st.text_area("Medicines", key="pres_add_meds")
        notes_in = st.text_area("Notes", key="pres_add_notes")
        if st.button("ADD Prescription", key="pres_add_btn"):
            pat_val = pat_sel.split("(")[0].strip() if isinstance(pat_sel, str) and "(" in pat_sel else pat_sel
            doc_val = doc_sel.split("(")[0].strip() if isinstance(doc_sel, str) and "(" in doc_sel else doc_sel
            st.session_state.prescriptions.append(Prescription(id_in.strip(), pat_val, doc_val, meds_in.strip(), notes_in.strip()))
            st.success("Prescription added ✅")
            st.rerun()

    with t[2]:
        if not st.session_state.prescriptions:
            st.info("No prescriptions to edit")
        else:
            options = [r.id for r in st.session_state.prescriptions]
            sel = st.selectbox("Select prescription (ID)", options, key="pres_edit_select")
            r = safe_next(st.session_state.prescriptions, "id", sel)
            if r:
                new_meds = st.text_area("Medicines", value=r.meds, key="pres_edit_meds")
                new_notes = st.text_area("Notes", value=r.notes, key="pres_edit_notes")
                if st.button("SAVE Prescription", key="pres_save_btn"):
                    r.meds = new_meds.strip(); r.notes = new_notes.strip()
                    st.success("Prescription updated ✅")
                    st.rerun()
            else:
                st.error("Prescription not found")

    with t[3]:
        if not st.session_state.prescriptions:
            st.info("No prescriptions to delete")
        else:
            options = [r.id for r in st.session_state.prescriptions]
            sel = st.selectbox("Select prescription to delete", options, key="pres_del_select")
            if st.button("DELETE Prescription", key="pres_del_btn"):
                delete_item(st.session_state.prescriptions, "id", sel)


if menu == "Payments":
    st.header("💰 Payments")
    t = st.tabs(["View","Add","Edit","Delete"])
    
    # View
    with t[0]:
        st.table([vars(x) for x in st.session_state.payments]) if st.session_state.payments else st.info("No payments")
    
    # Add
    with t[1]:
        id_in = st.text_input("ID", key="pay_add_id")
        pat_opt = [f"{p.name} ({p.id})" for p in st.session_state.patients] if st.session_state.patients else []
        pat_sel = st.selectbox("Patient", pat_opt, key="pay_add_pat") if pat_opt else st.text_input("Patient", key="pay_add_pat_text")
        visit_opt = [f"{v.id}" for v in st.session_state.visits] if st.session_state.visits else []
        visit_sel = st.selectbox("Visit ID", visit_opt, key="pay_add_visit") if visit_opt else st.text_input("Visit ID", key="pay_add_visit_text")
        amount_in = st.number_input("Amount", 0, 100000, 0, key="pay_add_amount")
        date_in = st.date_input("Date", date.today(), key="pay_add_date")
        
        if st.button("ADD Payment", key="pay_add_btn"):
            pat_val = pat_sel.split("(")[0].strip() if "(" in pat_sel else pat_sel
            st.session_state.payments.append(Payment(id_in.strip(), pat_val, visit_sel, float(amount_in), str(date_in)))
            st.success("Payment added ✅")
            st.rerun()
    
    # Edit
    with t[2]:
        if not st.session_state.payments:
            st.info("No payments to edit")
        else:
            options = [p.id for p in st.session_state.payments]
            sel = st.selectbox("Select Payment (ID)", options, key="pay_edit_select")
            p = safe_next(st.session_state.payments, "id", sel)
            if p:
                new_amount = st.number_input("Amount", value=p.amount, key="pay_edit_amount")
                new_date = st.date_input("Date", value=p.date, key="pay_edit_date")
                if st.button("SAVE Payment", key="pay_save_btn"):
                    p.amount = float(new_amount)
                    p.date = str(new_date)
                    st.success("Payment updated ✅")
                    st.rerun()
            else:
                st.error("Payment not found")
    
    # Delete
    with t[3]:
        if not st.session_state.payments:
            st.info("No payments to delete")
        else:
            options = [p.id for p in st.session_state.payments]
            sel = st.selectbox("Select Payment to delete", options, key="pay_del_select")
            if st.button("DELETE Payment", key="pay_del_btn"):
                delete_item(st.session_state.payments, "id", sel)