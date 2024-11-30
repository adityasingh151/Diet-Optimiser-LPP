from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://diet-frontend.onrender.com"],  # Corrected the origin URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and clean data
try:
    merged_data = pd.read_csv("https://github.com/adityasingh151/Diet-Optimiser-LPP/raw/refs/heads/main/backend/data/merged_menu_data.csv", on_bad_lines="skip")

    # Clean column names
    merged_data.columns = merged_data.columns.str.strip()

    # Define numeric columns for validation
    numeric_columns = ["Price", "Calories", "Fat (g)", "Carbohydrates (g)", "Protein (g)", "Calcium (mg)"]
    
    # Ensure all numeric columns are converted to numeric types and handle errors gracefully
    merged_data[numeric_columns] = merged_data[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # Drop rows with any NaN values in numeric columns
    merged_data = merged_data.dropna(subset=numeric_columns)

    # Convert to dictionary (Indexed by Item)
    food_data = merged_data.set_index("Item").T.to_dict()

    print("Data loaded and cleaned successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    food_data = {}

class FoodSelection(BaseModel):
    selected_items: list

@app.get("/")
def read_root():
    return {"message": "Welcome to the Diet Optimization API!"}

@app.get("/menu")
def get_menu():
    if merged_data.empty:
        raise HTTPException(status_code=500, detail="Menu data is not available.")
    return merged_data.to_dict(orient="records")

@app.post("/optimize")
def optimize_diet(selection: FoodSelection):
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

        # Create optimization problem
        problem = LpProblem("DietOptimization", LpMinimize)

        # Decision variables (Integer values)
        food_vars = {item: LpVariable(item, lowBound=0, cat="Integer") for item in selection.selected_items}
        print(f"Decision variables: {food_vars}")  # Debugging

        # Objective function: Minimize the cost
        problem += lpSum([food_data[item]["Price"] * food_vars[item] for item in selection.selected_items])
        print("Objective function added.")  # Debugging

        # Nutritional constraints (Minimum requirements)
        problem += lpSum([food_data[item]["Protein (g)"] * food_vars[item] for item in selection.selected_items]) >= 55
        problem += lpSum([food_data[item]["Fat (g)"] * food_vars[item] for item in selection.selected_items]) >= 46
        problem += lpSum([food_data[item]["Carbohydrates (g)"] * food_vars[item] for item in selection.selected_items]) >= 180
        problem += lpSum([food_data[item]["Calcium (mg)"] * food_vars[item] for item in selection.selected_items]) >= 800
        print("Constraints added.")  # Debugging

        # Add variety constraint (maximum 3 of each item)
        for item in selection.selected_items:
            problem += food_vars[item] <= 3  # Maximum of 3 units per item
        print("Variety constraint added.")  # Debugging

        # Solve the problem
        problem.solve()
        print(f"Solver status: {LpStatus[problem.status]}")  # Debugging

        if LpStatus[problem.status] != "Optimal":
            # Handle optimization failure (provide more specific error)
            raise HTTPException(
                status_code=400,
                detail="The optimization could not find a feasible solution. This could be due to the variety constraint. Try selecting fewer items or adjust your selection."
            )

        # Return the optimal selection and total cost
        optimal_selection = {item: food_vars[item].varValue for item in selection.selected_items}
        total_cost = sum(food_data[item]["Price"] * optimal_selection[item] for item in selection.selected_items)

        return {"optimal_selection": optimal_selection, "total_cost": total_cost}

    except Exception as e:
        print(f"Error during optimization: {e}")  # Debugging
        raise HTTPException(status_code=500, detail="The optimization could not find a feasible solution. This could be due to the variety constraint. Try selecting more items or adjust your selection.")
