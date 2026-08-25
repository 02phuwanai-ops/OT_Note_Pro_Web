from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_file,
    send_from_directory,
    redirect,
    session,
)

import os
import bcrypt

from parser import parse_sms

from database import (
    init_db,
    save_ot,
    get_recent,
    delete_ot,
    update_ot,
    register_user,
    login_user,
    get_users,
    delete_user,
    reset_password,
    get_all_records,
    get_recent,
    get_total_hours

)


# ถ้ายังไม่มีไฟล์ excel.py ให้คอมเมนต์บรรทัดนี้ไว้ก่อน
# from excel import export_excel


app = Flask(__name__)

app.secret_key = "falcon_ot_note_2026"

from datetime import timedelta


app.permanent_session_lifetime = timedelta(days=30)
# =====================================
# Home
# =====================================

@app.route("/")
def home():

    if "employee_id" in session:

        return redirect("/dashboard")


    return render_template("login.html")
    


# =====================================
# Parse SMS
# =====================================
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    data = request.json

    result = register_user(

        data["employee_id"],

        data["password"]

    )

    if result:

        return jsonify({

            "success": True

        })

    return jsonify({

        "success": False,

        "message": "Employee ID นี้มีอยู่แล้ว"

    })


@app.route("/parse", methods=["POST"])
def parse():

    sms = request.form.get(
        "sms",
        ""
    )

    data = parse_sms(sms)

    return jsonify(data)


@app.route("/login", methods=["POST"])
def login():

    data = request.json

    user = login_user(

        data["employee_id"],
        data["password"]

    )

    if user:

        session["employee_id"] = data["employee_id"]
        session["role"] = user[0]
        session.permanent = True

        return jsonify({

            "success": True

        })

    return jsonify({

        "success": False

    })

@app.route("/dashboard")
def dashboard():

    if "employee_id" not in session:
        return redirect("/")

    return render_template(

        "index.html",

        role=session.get("role"),

        employee_id=session.get("employee_id")

    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =====================================
# Save OT
# =====================================

@app.route("/save", methods=["POST"])
def save():
    
    if "employee_id" not in session:

        return jsonify({

        "success": False,
        "message": "Please login"

    })


    try:

        data = request.json

        ticket = (data.get("ticket") or "").strip()

        if ticket == "":

            ticket = None

        print("DATA FROM WEB:")
        print(data)

        result = save_ot(

            ticket,
            data["circuit"],
            data["fault_date"],
            data["start_time"],
            data["finish_time"],
            float(data["hours"] or 0),
            data["description"],
            session["employee_id"]

        )

        print("SAVE RESULT:")
        print(result)

        return jsonify({

            "success": result

        })

    except Exception as e:

        print("ERROR:")
        print(e)

        return jsonify({

            "success": False,
            "error": str(e)

        })


# =====================================
# Recent Records
# =====================================

@app.route("/records")
def records():

    if "employee_id" not in session:

        return jsonify([])

    data = get_recent(

        session["employee_id"]

    )

    return jsonify(data)

# =====================================
# Summary
# =====================================

@app.route("/summary")
def summary():

    if "employee_id" not in session:

        return jsonify({

            "hours":0

        })

    total = get_total_hours(

        session["employee_id"]

    )

    return jsonify({

        "hours":round(total,2)

    })

# ==========================================
# Export TXT
# ==========================================

from datetime import datetime


@app.route("/export")
def export_txt():

    if "employee_id" not in session:

        return redirect("/")


    records = get_recent(

        session["employee_id"],

        99999

    )


    # ชื่อไฟล์ตามวันที่ปัจจุบัน
    export_name = datetime.now().strftime("OT_%d-%m-%Y.txt")

    # ไฟล์ชั่วคราวใน Server
    temp_filename = "OT_Report.txt"


    with open(
        temp_filename,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            f'{"Ticket":<18}'
            f'{"Circuit":<12}'
            f'{"Fault Date":<14}'
            f'{"Start":<8}'
            f'{"Finish":<8}'
            f'{"Hour":<8}'
            f'{"Detail"}\n'
        )


        f.write("-" * 95 + "\n")


        for row in records:

            f.write(

                f'{str(row[0]):<18}'
                f'{str(row[1]):<12}'
                f'{str(row[2]):<14}'
                f'{str(row[3]):<8}'
                f'{str(row[4]):<8}'
                f'{str(row[5]):<8}'
                f'{str(row[6])}\n'

            )


    return send_file(

        temp_filename,

        as_attachment=True,

        download_name=export_name

    )

# =====================================
# Delete OT
# =====================================

@app.route("/delete", methods=["POST"])
def delete():

    if "employee_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login"
        })

    data = request.json

    delete_ot(data["id"])

    return jsonify({
        "success": True
    })

# =====================================
# update OT
# =====================================

@app.route("/update", methods=["POST"])
def update():

    data = request.json

    result = update_ot(

    data["ticket"],
    data["start_time"],
    data["finish_time"],
    data["hours"],
    data["description"],
    session["employee_id"]

)

    return jsonify({

        "success": result

    })

@app.route("/users")
def users():

    if "employee_id" not in session:

        return redirect("/")

    if session.get("role") != "admin":

        return redirect("/dashboard")

    return render_template("users.html")

@app.route("/user_list")
def user_list():

    if "employee_id" not in session:

        return jsonify([])

    if session.get("role") != "admin":

        return jsonify([])

    return jsonify(

        get_users()

    )

@app.route("/delete_user/<employee_id>", methods=["POST"])
def delete_user_route(employee_id):

    if "employee_id" not in session:

        return jsonify({
            "success": False
        })


    if session.get("role") != "admin":

        return jsonify({
            "success": False
        })


    # กัน Admin ลบตัวเอง

    if employee_id == session["employee_id"]:

        return jsonify({

            "success": False,

            "message": "ไม่สามารถลบบัญชีตัวเองได้"

        })


    result = delete_user(employee_id)


    return jsonify({

        "success": result

    })

@app.route("/reset_password", methods=["POST"])
def reset_password_route():

    if "employee_id" not in session:

        return jsonify({"success": False})

    if session.get("role") != "admin":

        return jsonify({"success": False})

    data = request.json

    result = reset_password(

        data["employee_id"],
        data["password"]

    )

    return jsonify({

        "success": result

    })

# =====================================
# Export Excel
# =====================================

"""
ยกเลิกเครื่องหมายคอมเมนต์เมื่อมี excel.py

@app.route("/export")
def export():

    file = export_txt()

    return send_file(
        file,
        as_attachment=True
    )
"""
# =====================================
# PWA Manifest
# =====================================

@app.route("/manifest.json")
def manifest():

    return send_from_directory(".", "manifest.json")

# =====================================
# Main
# =====================================

from waitress import serve
if __name__ == "__main__":

    init_db()

    print("=" * 50)
    print(" OT Note Pro Web v1.0 FINAL")
    print(" Production Server Started")
    print(" http://0.0.0.0:5000")
    print("=" * 50)

    serve(

        app,

        host="0.0.0.0",

        port=5000,

        threads=8

    )

