from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time

from schema.predictionSchema import PredictionResponse
from schema.userInput import UserInputData

from model.predict import model, MODEL_VERSION, predictOutput

from database import engine, get_db
from db_models.base import Base
from db_models.predictionLogs import PredictionLog  # Orm model for logging


app = FastAPI()

# Create tables at startup
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return JSONResponse(
        status_code=200,
        content={"message": "Welcome to Insurance Premium Prediction API"}
    )


@app.get("/health")
def healthCheck():
    return {
        "status": "OK",
        "model_loaded": model is not None,
        "version": MODEL_VERSION
    }


@app.post("/predict", response_model=PredictionResponse)
def predictPremium(
    data: UserInputData,
    db: Session = Depends(get_db)
):
    userInput = {
        'bmi': data.bmi,
        'age_group': data.ageGrp,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }

    start_time = time.perf_counter()

    try:
        prediction = predictOutput(userInput)
        status = "success"
    except Exception:
        prediction = None
        status = "error"

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    # Log to PostgreSQL
    try:
        log = PredictionLog(
            latency_ms=latency_ms,
            prediction=prediction["predicted_category"],
            model_version=MODEL_VERSION,
            status=status
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()

    if status == "error":
        return JSONResponse(
            status_code=500,
            content={"error": "Prediction failed"}
        )

    return JSONResponse(
        status_code=200,
        content={"Precicted Category": prediction}
    )
