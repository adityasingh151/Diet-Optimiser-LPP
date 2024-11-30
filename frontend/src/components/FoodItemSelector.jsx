import React, { useState, useEffect } from "react";
import axios from "axios";
import "./styles.css"; // Import the vanilla CSS file

const FoodItemSelector = () => {
  const [foodItems, setFoodItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch food items on component mount
  useEffect(() => {
    axios
      .get("https://diet-backend-d1gj.onrender.com/menu")
      .then((response) => setFoodItems(response.data))
      .catch((error) => {
        console.error("Error fetching food items:", error);
        setError("Failed to load food items. Please try again later.");
      });
  }, []);

  // Handle checkbox selection
  const handleCheckboxChange = (item) => {
    setSelectedItems((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

  // Handle form submission to optimize diet
  const handleSubmit = async () => {
    setError(null);
    setResult(null);
    setIsLoading(true);

    if (selectedItems.length === 0) {
      setError("Please select at least one food item.");
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:8000/optimize", {
        selected_items: selectedItems,
      });

      if (response.data && response.data.optimal_selection) {
        setResult(response.data);
      } else {
        throw new Error("Optimization failed. No feasible solution.");
      }
    } catch (error) {
      console.error("Error fetching optimization results:", error);
      setError(error.response?.data?.detail || "An error occurred during optimization. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="food-item-selector-container">
      <h2>Select Your Favorite Food Items</h2>

      {/* Error and loading message */}
      {error && <p className="error-message">{error}</p>}
      {isLoading && <p className="loading-message">Optimizing your selection...</p>}

      {/* Food item list */}
      <div className="food-item-grid">
        {foodItems.length === 0 ? (
          <p className="loading-message">Loading food items...</p>
        ) : (
          foodItems.map((item) => (
            <div key={item.Item} className="food-item-card">
              <div className="food-item-details">
                <h3 className="food-item-title">{item.Item}</h3>
                <p className="food-item-description">
                  {Object.entries(item).map(([key, value]) =>
                    key !== "Item" && key !== "image_url" ? (
                      <span key={key}>
                        {key}: {value} |{" "}
                      </span>
                    ) : null
                  )}
                </p>
              </div>
              <div className="checkbox-container">
                <input
                  type="checkbox"
                  value={item.Item}
                  onChange={() => handleCheckboxChange(item.Item)}
                  className="food-item-checkbox"
                />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Submit button */}
      <button onClick={handleSubmit} disabled={isLoading}>
        Optimize Selection
      </button>

      {/* Display optimization result */}
      {result && (
        <div className="optimization-result">
          <h3>Diet Optimizer for North Campus</h3> {/* Updated Heading */}
          <ul>
            {Object.entries(result.optimal_selection).map(([item, quantity]) => (
              <li key={item}>
                {item}: {quantity.toFixed(0)} units
              </li>
            ))}
          </ul>
          <p className="total-cost">Total Cost: ₹{result.total_cost.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
};

export default FoodItemSelector;
