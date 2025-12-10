from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Annotated, Literal, Optional
import json

app= FastAPI()

def loadData():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def saveData(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., description="Full name of the patient")]
    city: Annotated[str, Field(..., description="City of residence")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal['Male', 'Female', 'Other'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height in meters", example=1.75)]
    weight: Annotated[float, Field(..., gt=0, description="Weight in kilograms")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight / (self.height ** 2)
        return round(bmi, 2)

    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi

        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"


@app.get("/")
def hello():
    return {'message' : 'Patient Management System API'}

@app.get("/about")
def about():
    return {'message' : 'This API is designed to manage patient records efficiently.'}

@app.get('/view')
def viewPatients():
    data = loadData()
    return data
 
@app.get('/patient/{patientId}')
def viewPatient(patientId : str = Path(..., description ="ID of the patient to retrieve", example="P001")):
    wholeData = loadData()
    if patientId in wholeData:
        return wholeData[patientId]
    # else:
    #     return {'message' : 'Patient not found'}
    raise HTTPException(status_code=404, detail="Patient not found") 

@app.get('/sort')
def sortPatients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = loadData()

    sortOrder = True if order=='desc' else False

    sortedData = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sortOrder)

    return sortedData

@app.post('/create')
def createPatient(patient: Patient):
    data = loadData()
    # Check if patient ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    # Add new patient
    data[patient.id] = patient.model_dump(exclude=['id'])
    # Save updated data back to the 
    saveData(data)
    return JSONResponse(content={"message": "Patient created successfully"}, status_code=201)

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

@app.put('/edit/{patientId}')
def updatePatient(patientId: str, patientUpdate: PatientUpdate):
    data = loadData()
    if patientId not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    existingPatientData = data[patientId] # Dictionary of existing patient data
    updatedPatientData = patientUpdate.model_dump(exclude_unset=True)  # Get only fields that were provided (Pydantic object -> dictionary)

    for key, value in updatedPatientData.items():
        if value is not None:
            existingPatientData[key] = value  # Update only the provided fields

    # Calculate BMI and verdict (existingPatientData -> Patient pydantic object -> update calculated fields -> concvert back to dictionary)

    existingPatientData['id'] = patientId  # Add id to create Patient object
    patientObject = Patient(**existingPatientData)  # Create Patient object (BMI and verdict will be calculated automatically)
    existingPatientData = patientObject.model_dump(exclude = 'id')  # Convert back to dictionary (with updated calculated fields)

    data[patientId] = existingPatientData  # Update the patient data in the main dictionary

    saveData(data)
    return JSONResponse(content={"message": "Patient updated successfully"}, status_code=200)


@app.delete('/delete/{patientId}')
def deletePatient(patientId: str):
    data = loadData()
    if patientId not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    del data[patientId]
    saveData(data)

    return JSONResponse(content={"message": "Patient deleted successfully"}, status_code=200)