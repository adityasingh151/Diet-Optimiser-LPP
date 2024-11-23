import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the CSV file and preprocess the data
try:
    # Load the dataset
    merged_data = pd.read_csv("data/merged_menu_data.csv")

    # Enforce numeric types for relevant columns
    numeric_columns = ["Price", "Calories", "Fat (g)", "Carbohydrates (g)", "Protein (g)", "Calcium (mg)"]
    merged_data[numeric_columns] = merged_data[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # Drop rows with invalid numeric data
    merged_data = merged_data.dropna(subset=numeric_columns)

    # Ensure all columns are trimmed of unnecessary spaces
    merged_data.columns = merged_data.columns.str.strip()

    # Convert to dictionary
    food_data = merged_data.set_index("Item").T.to_dict()
    print("Data loaded and cleaned successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    food_data = {}  # Fallback to empty data

class FoodSelection(BaseModel):
    selected_items: list

@app.get("/")
def read_root():
    """
    Root endpoint for API health check.
    """
    return {"message": "Welcome to the Diet Optimization API!"}

@app.get("/menu")
def get_menu():
    """
    Endpoint to fetch menu items with their nutritional details.
    """
    if merged_data.empty:
        raise HTTPException(status_code=500, detail="Menu data is not available.")
    return merged_data.to_dict(orient="records")

@app.post("/optimize")
def optimize_diet(selection: FoodSelection):
    """
    Optimize the selection of food items to minimize cost while meeting nutritional constraints.
    """
    try:
        print(f"Received selected items: {selection.selected_items}")  # Debugging

        if not selection.selected_items:
            raise HTTPException(status_code=400, detail="No food items selected.")

        # Validate selected items
        for item in selection.selected_items:
            if item not in food_data:
                print(f"Invalid item: {item}")  # Debugging
                raise HTTPException(status_code=400, detail=f"Invalid food item: {item}")

        print("All selected items are valid.")  # Debugging

        problem = LpProblem("DietOptimization", LpMinimize)

        # Decision variables
        food_vars = {item: LpVariable(item, lowBound=0, cat="Continuous") for item in selection.selected_items}
        print(f"Decision variables: {food_vars}")  # Debugging

        # Objective function: Minimize cost
        problem += lpSum([food_data[item]["Price"] * food_vars[item] for item in selection.selected_items])
        print("Objective function added.")  # Debugging

        # Nutritional constraints
        problem += lpSum([food_data[item]["Protein (g)"] * food_vars[item] for item in selection.selected_items]) >= 55
        problem += lpSum([food_data[item]["Fat (g)"] * food_vars[item] for item in selection.selected_items]) >= 46
        problem += lpSum([food_data[item]["Carbohydrates (g)"] * food_vars[item] for item in selection.selected_items]) >= 180
        problem += lpSum([food_data[item]["Calcium (mg)"] * food_vars[item] for item in selection.selected_items]) >= 800
        print("Constraints added.")  # Debugging

        # Solve the problem
        problem.solve()
        print(f"Solver status: {LpStatus[problem.status]}")  # Debugging

        if LpStatus[problem.status] != "Optimal":
            raise HTTPException(status_code=400, detail="Optimization failed. No feasible solution found.")

        # Prepare results
        result = {item: food_vars[item].varValue for item in selection.selected_items if food_vars[item].varValue > 0}
        total_cost = sum([food_data[item]["Price"] * result[item] for item in result])

        print(f"Optimization result: {result}, Total cost: {total_cost}")  # Debugging
        return {"optimal_selection": result, "total_cost": total_cost}
    except Exception as e:
        print(f"Error during optimization: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Internal Server Error")
