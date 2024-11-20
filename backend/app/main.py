from fastapi import FastAPI
from pydantic import BaseModel
from pulp import LpProblem, LpVariable, LpMinimize, lpSum
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://diet-frontend.onrender.com/"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)



class FoodSelection(BaseModel):
    selected_items: list

# Mock data for food items and their nutritional content
food_data = {
    "Paneer Toast": {"cost": 60, "protein": 8, "fat": 10, "carb": 28, "phos": 200, "vitC": 6, "calcium": 150},
    "Grilled Sandwich": {"cost": 70, "protein": 6, "fat": 8.5, "carb": 35, "phos": 120, "vitC": 7, "calcium": 50},
    "Aloo Samosa": {"cost": 10, "protein": 4, "fat": 11, "carb": 32, "phos": 100, "vitC": 10, "calcium": 30},
}

@app.post("/optimize")
def optimize_diet(selection: FoodSelection):
    problem = LpProblem("DietOptimization", LpMinimize)

    # Decision variables
    food_vars = {item: LpVariable(item, lowBound=0, cat='Continuous') for item in selection.selected_items}

    # Objective function: Minimize cost
    problem += lpSum([food_data[item]["cost"] * food_vars[item] for item in selection.selected_items])

    # Nutritional constraints
    problem += lpSum([food_data[item]["protein"] * food_vars[item] for item in selection.selected_items]) >= 55
    problem += lpSum([food_data[item]["fat"] * food_vars[item] for item in selection.selected_items]) >= 46
    problem += lpSum([food_data[item]["carb"] * food_vars[item] for item in selection.selected_items]) >= 180
    problem += lpSum([food_data[item]["phos"] * food_vars[item] for item in selection.selected_items]) >= 700
    problem += lpSum([food_data[item]["vitC"] * food_vars[item] for item in selection.selected_items]) >= 70
    problem += lpSum([food_data[item]["calcium"] * food_vars[item] for item in selection.selected_items]) >= 800

    # Solve the problem
    problem.solve()

    # Prepare the results
    result = {item: food_vars[item].varValue for item in selection.selected_items if food_vars[item].varValue > 0}
    total_cost = sum([food_data[item]["cost"] * result[item] for item in result])

    return {"optimal_selection": result, "total_cost": total_cost}
