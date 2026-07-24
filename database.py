"""
=========================================
OT Note Pro v1.0 - Falcon
Database (SQLite)
=========================================
"""
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

DB_NAME = "ot_note.db"


# ==========================================
# Connect
# ==========================================

def connect():

    print(
        "DB:",
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_NAME")
    )

    return mysql.connector.connect(

        host=os.getenv("DB_HOST"),

        port=int(os.getenv("DB_PORT")),

        user=os.getenv("DB_USER"),

        password=os.getenv("DB_PASSWORD"),

        database=os.getenv("DB_NAME")

    )

# ==========================================
# Initialize Database
# ==========================================

def init_db():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    
    CREATE TABLE IF NOT EXISTS ot_records(

    id INT AUTO_INCREMENT PRIMARY KEY,

    ticket VARCHAR(50) UNIQUE,

    circuit VARCHAR(100),

    fault_date VARCHAR(50),

    start_time VARCHAR(10),

    finish_time VARCHAR(10),

    hours DECIMAL(5,2),

    description TEXT,

    owner VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
    """)

    conn.commit()

    # ตรวจสอบว่ามีคอลัมน์ description หรือยัง
     
# ==========================================
# Users
# ==========================================

def create_user_table():

    conn = connect()

    cur = conn.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users(

        id INT AUTO_INCREMENT PRIMARY KEY,

        employee_id VARCHAR(50) UNIQUE,

        password VARCHAR(255),

        role VARCHAR(50) DEFAULT 'technician'

    )

    """)

    conn.commit()

    conn.close()


def register_user(employee_id, password):

    import bcrypt

    conn = connect()

    cur = conn.cursor()


    hashed_password = bcrypt.hashpw(

        password.encode("utf-8"),

        bcrypt.gensalt()

    ).decode("utf-8")


    try:

        cur.execute("""

        INSERT INTO users(

            employee_id,
            password,
            role

        )

        VALUES(%s,%s,%s)

        """,

        (

            employee_id,

            hashed_password,

            "technician"

        ))


        conn.commit()

        return True


    except Exception as e:

        print(e)

        return False


    finally:

        conn.close()


def login_user(employee_id, password):

    import bcrypt

    conn = connect()

    cur = conn.cursor()


    cur.execute("""

    SELECT password, role

    FROM users

    WHERE employee_id=%s

    """,

    (employee_id,))


    user = cur.fetchone()


    conn.close()


    if not user:

        return None


    stored_password = user[0]


    # =========================
    # bcrypt user
    # =========================

    if stored_password.startswith("$2"):

        try:

            if bcrypt.checkpw(

                password.encode("utf-8"),

                stored_password.encode("utf-8")

            ):

                return (user[1],)

        except:

            return None


    # =========================
    # old password
    # =========================

    else:

        if password == stored_password:

            return (user[1],)


    return None


    # =========================
    # bcrypt password
    # =========================

    if stored_password.startswith("$2"):

        try:

            if bcrypt.checkpw(

                password.encode("utf-8"),

                stored_password.encode("utf-8")

            ):

                return (user[1],)

            else:

                return None


        except ValueError:

            return None


    # =========================
    # password เก่า (plain text)
    # =========================

    else:

        if password == stored_password:

            return (user[1],)


    return None

# ==========================================
# Save OT
# ==========================================

def save_ot(
    ticket,
    circuit,
    fault_date,
    start_time,
    finish_time,
    hours,
    description,
    owner
):

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute("""

        INSERT INTO ot_records(

            ticket,
            circuit,
            fault_date,
            start_time,
            finish_time,
            hours,
            description,
            owner

        )

        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                

        """,(

            ticket,
            circuit,
            fault_date,
            start_time,
            finish_time,
            hours,
            description,
            owner

        ))

        conn.commit()

        return True

    except mysql.connector.Error as e:

    print("MYSQL ERROR:", e)

    return False

    finally:

        conn.close()


# ==========================================
# Update OT
# ==========================================

def update_ot(
    ticket,
    start_time,
    finish_time,
    hours,
    description,
    owner
):

    conn = connect()

    cur = conn.cursor()

    cur.execute("""

    UPDATE ot_records

    SET

        start_time=%s,
        finish_time=%s,
        hours=%s,
        description=%s

    WHERE ticket=%s
    AND owner=%s

    """,(

        start_time,
        finish_time,
        hours,
        description,
        ticket,
        owner

    ))


    conn.commit()


    updated = cur.rowcount


    conn.close()


    return updated > 0


# ==========================================
# Delete OT
# ==========================================

def delete_ot(ticket, owner):

    conn = connect()

    cur = conn.cursor()

    cur.execute(

        """
        DELETE FROM ot_records
        WHERE ticket = %s
        AND owner = %s
        """,

        (ticket, owner)

    )

    conn.commit()

    conn.close()


# ==========================================
# Recent Records
# ==========================================

def get_recent(owner, limit=20):

    conn = connect()

    cur = conn.cursor()

    cur.execute("""

    SELECT

        ticket,
        circuit,
        fault_date,
        start_time,
        finish_time,
        hours,
        description

    FROM ot_records

    WHERE owner=%s

    ORDER BY id DESC

    LIMIT %s

    """,(

        owner,
        limit

    ))

    rows = cur.fetchall()

    conn.close()

    return rows


# ==========================================
# All Records
# ==========================================

def get_all_records():

    conn = connect()

    cur = conn.cursor()

    cur.execute("""

    SELECT

        ticket,
        circuit,
        fault_date,
        start_time,
        finish_time,
        hours,
        description

    FROM ot_records

    ORDER BY id DESC

    """)

    rows = cur.fetchall()

    conn.close()

    return rows


# ==========================================
# Search Ticket
# ==========================================

def search_ticket(keyword):

    conn = connect()

    cur = conn.cursor()

    cur.execute("""

    SELECT

        ticket,
        circuit,
        fault_date,
        start_time,
        finish_time,
        hours,
        description

    FROM ot_records

    WHERE ticket LIKE %s

    ORDER BY id DESC

    """,(f"%{keyword}%",))

    rows = cur.fetchall()

    conn.close()

    return rows


# ==========================================
# Clear Database
# ==========================================

def clear_database():

    conn = connect()

    cur = conn.cursor()

    cur.execute("DELETE FROM ot_records")

    conn.commit()

    conn.close()


    # ==========================================
# Add owner column
# ==========================================

    cur.execute(
        "PRAGMA table_info(ot_records)"
    )

    columns = [

        row[1]

        for row in cur.fetchall()

    ]

    if "owner" not in columns:

        cur.execute("""

        ALTER TABLE ot_records

        ADD COLUMN owner TEXT

        """)


# ==========================================
# Get Users
# ==========================================

def get_users():

    conn = connect()

    cur = conn.cursor()

    cur.execute("""

        SELECT

            employee_id,
            role

        FROM users

        ORDER BY employee_id

    """)

    rows = cur.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({

            "employee_id": row[0],
            "role": row[1]

        })

    return result

# ==========================================
# Delete User
# ==========================================

def delete_user(employee_id):

    conn = connect()

    cur = conn.cursor()

    cur.execute(

        """
        DELETE FROM users
        WHERE employee_id=%s
        """,

        (employee_id,)

    )

    conn.commit()

    deleted = cur.rowcount

    conn.close()

    return deleted > 0

# ==========================================
# Reset Password
# ==========================================

def reset_password(employee_id, new_password):

    conn = connect()

    cur = conn.cursor()

    cur.execute(

        """
        UPDATE users
        SET password = %s
        WHERE employee_id = %s
        """,

        (new_password, employee_id)

    )

    conn.commit()

    updated = cur.rowcount

    conn.close()

    return updated > 0
