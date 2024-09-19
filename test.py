from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
import uvicorn

app = FastAPI()


class CarInfo(BaseModel):
    cars_type: str
    category: str
    make: str
    model: str
    year: str
    type: str
    status: str
    vin: str
    fuel_type: str
    transmission: str
    engine: str
    cylinders: str
    drive: str
    kilometer: str
    mileage_type: str
    condition: str
    keys: str
    engine_runs :str
    drivable : str
    stock_number: str
    interior_colour: str
    exterior_colour: str
    accessories: str
    currency: str
    price: str
    country: str
    state: str
    city: str
    auction_date: str
    purchase_option: str
    hid_main_images: str
    hid_addedtype: str
    hid_addedby: str
    h_inventory: str
    hid_allimages: list[str]
    auction_name: str
    title_status: str
    run_no: str
    pmr: str


@app.post("/add_car_info")
async def add_car_info(car_info: CarInfo):
    file_name = f"{car_info.stock_number}.json"
    file_path = os.path.join("data", file_name)
    
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with open(file_path, 'w') as json_file:
        json.dump(car_info.dict(), json_file, indent=4)
    
    return {"message": "Car information saved successfully", "file_path": file_path}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8080)


