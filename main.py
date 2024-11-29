import backend.Functions_.commands as cmd
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def initial():
    return "Hello world:)"


@app.post("/doctor/create_doctor")
def create_new_doctor(doctor: cmd.DoctorBase):
    try:
        new_doctor = cmd.create_doctor(doctor)
        if not new_doctor:
            raise HTTPException(status_code=400, detail="Doctor could not be created")
        return new_doctor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating doctor: {str(e)}")


@app.get("/doctor")
def get_doctor_info(email: str):
    try:
        doctor_info = cmd.get_doctor_full_info_by_email(email)
        if not doctor_info:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving doctor: {str(e)}")

@app.post("/report/create_report")
def create_new_report(report: cmd.ReportBase):
    try:
        new_report = cmd.create_report(report)
        if not new_report:
            raise HTTPException(status_code=400, detail="Report could not be created")
        return new_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating report: {str(e)}")


@app.put("/doctor/update_abonnement")
def update_abonnement(data: cmd.UpdateDoctorAbonnement):
    try:
        updated_doctor = cmd.update_doctor_abonnement(data.doctor_id, data.abonnement)
        if not updated_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return updated_doctor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating abonnement: {str(e)}")
    
