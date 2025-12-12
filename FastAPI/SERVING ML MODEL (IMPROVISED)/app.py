from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schema.predictionSchema import PredictionResponse
from schema.userInput  import UserInputData

from model.predict import model, MODEL_VERSION, predictOutput


app = FastAPI()


@app.get("/")
def home():
    return JSONResponse(status_code=200, content={"message": "Welcome to Insurance Premium Prediction API"})     

@app.get("/health")
def healthCheck():
    return {
        "status": "OK",
        "model_loaded" : model is not None,
        "version": MODEL_VERSION
    }
@app.post("/predict", response_model=PredictionResponse)
def predictPremium(data : UserInputData):
    userInput = {
        'bmi': data.bmi,
        'age_group': data.ageGrp,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }

    try:
        prediction = predictOutput(userInput)
        return JSONResponse(status_code=200, content={'Precicted Category': prediction})
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})