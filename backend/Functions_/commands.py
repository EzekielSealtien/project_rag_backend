from pydantic import BaseModel, EmailStr
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from typing import Optional

from dotenv import load_dotenv
import os

load_dotenv()

# Récupérer les variables d'environnement
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


def create_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        con = psycopg2.connect(
            
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            keepalives=1,                
            keepalives_idle=300,         
            keepalives_interval=10,      
            keepalives_count=5 
            
        )
        print("Database connection established.")
        return con
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

# Create the connection
conn = create_connection()



class DoctorBase(BaseModel):
    name: str
    email: str
    password: str
    specialization: Optional[str] = None
    abonnement:str
class DoctorResponse(DoctorBase):
    doctor_id: int

        
class ReportBase(BaseModel):
    doctor_id: int
    title: str
    content: str


class ReportResponse(ReportBase):
    report_id: int


class ResponseChatbot(BaseModel):
    context:str
    question:str

class UpdateDoctorAbonnement(BaseModel):
    doctor_id: int
    abonnement: str
        

def create_doctor(doctor: DoctorBase):
    if not conn:
        raise Exception("No database connection available.")
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO doctor (name, email, password, specialization,abonnement)
            VALUES (%s, %s, %s, %s,%s)
            RETURNING doctor_id, name, email, password, specialization,abonnement
            """,
            (doctor.name, doctor.email, doctor.password, doctor.specialization,doctor.abonnement)
        )
        new_doctor = cursor.fetchone()
        conn.commit()
        return new_doctor
    except Exception as e:
        conn.rollback()
        print(f"Error creating doctor: {e}")
        raise
    finally:
        cursor.close()


def create_report(report: ReportBase):
    if not conn:
        raise Exception("No database connection available.")
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO report (doctor_id, title, content)
            VALUES (%s, %s, %s)
            RETURNING report_id, doctor_id, title, content
            """,
            (report.doctor_id, report.title, report.content)
        )
        new_report = cursor.fetchone()
        conn.commit()
        return new_report
    except Exception as e:
        conn.rollback()
        print(f"Error creating report: {e}")
        raise
    finally:
        cursor.close()

def update_doctor_abonnement(doctor_id: int, abonnement: str):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE doctor
                SET abonnement = %s
                WHERE doctor_id = %s
                RETURNING doctor_id, abonnement
                """,
                (abonnement, doctor_id)
            )
            updated_doctor = cursor.fetchone()
            conn.commit()
            return updated_doctor
    except Exception as e:
        conn.rollback()
        print(f"Error updating doctor's abonnement: {e}")
        return None



def get_doctor_by_id(doctor_id: int):
    if not conn:
        raise Exception("No database connection available.")
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM doctor WHERE doctor_id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        if doctor:
            return doctor
        else:
            return f"No doctor found with doctor_id = {doctor_id}"
    except Exception as e:
        print(f"Error fetching doctor: {e}")
        raise
    finally:
        cursor.close()

def get_all_reports():
    if not conn:
        raise Exception("No database connection available.")
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM report")
        reports = cursor.fetchall()
        return reports
    except Exception as e:
        print(f"Error fetching reports: {e}")
        raise
    finally:
        cursor.close()

def get_all_reports_for_doctor(doctor_id):
    if not conn:
        raise Exception("No database connection available.")
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Adjust the query to filter by doctor ID
        cursor.execute("SELECT * FROM report WHERE doctor_id = %s", (doctor_id,))
        reports = cursor.fetchall()
        return reports
    except Exception as e:
        print(f"Error fetching reports for doctor {doctor_id}: {e}")
        raise
    finally:
        cursor.close()



def get_doctor_full_info_by_email(email: str):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT 
                    d.doctor_id, d.name AS doctor_name, d.email AS doctor_email, d.password, d.specialization, d.abonnement,
                    r.report_id, r.title AS report_title, r.content AS report_content
                FROM doctor d
                LEFT JOIN report r ON d.doctor_id = r.doctor_id
                WHERE d.email = %s
                """,
                (email,)
            )
            rows = cursor.fetchall()

            if not rows:
                return None

            # Group the doctor's information
            doctor_info = {
                "doctor_id": rows[0]["doctor_id"],
                "name": rows[0]["doctor_name"],
                "email": rows[0]["doctor_email"],
                "password": rows[0]["password"],
                "specialization": rows[0]["specialization"],
                "abonnement": rows[0]["abonnement"],
                "reports": []
            }

            # Track existing report IDs to avoid duplicates
            existing_report_ids = {report["report_id"] for report in doctor_info["reports"]}

            # Group reports
            for row in rows:
                if row["report_id"] and row["report_id"] not in existing_report_ids:
                    doctor_info["reports"].append({
                        "report_id": row["report_id"],
                        "title": row["report_title"],
                        "content": row["report_content"]
                    })
                    existing_report_ids.add(row["report_id"])

            return doctor_info

    except Exception as e:
        print(f"Error retrieving full doctor information by email: {e}")
        return None
