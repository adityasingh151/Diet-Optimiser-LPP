import React, { useState, useEffect } from "react";
import axios from "axios";

const FoodItemSelector = () => {
  const [foodItems, setFoodItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/menu")
      .then((response) => setFoodItems(response.data))
      .catch((error) => {
        console.error("Error fetching food items:", error);
        setError("Failed to load food items. Please try again later.");
      });
  }, []);

  const handleCheckboxChange = (item) => {
    setSelectedItems((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

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
      setResult(response.data);
    } catch (error) {
      console.error("Error fetching optimization results:", error);
      setError(
        error.response?.data?.detail ||
        "An error occurred while optimizing. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2>Select Food Items</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {isLoading && <p>Loading...</p>}

      <div>
        {foodItems.length === 0 ? (
          <p>Loading food items...</p>
        ) : (
          foodItems.map((item) => (
            <div key={item.Item} style={{ marginBottom: "10px" }}>
              <input
                type="checkbox"
                value={item.Item}
                onChange={() => handleCheckboxChange(item.Item)}
              />
              <label style={{ marginLeft: "10px" }}>
                <b>{item.Item}</b> - 
                {Object.entries(item).map(([key, value]) =>
                  key !== "Item" ? (
                    <span key={key}>
                      {key}: {value} |{" "}
                    </span>
                  ) : null
                )}
              </label>
            </div>
          ))
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        Optimize
      </button>

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Optimization Results</h3>
          <ul>
            {Object.entries(result.optimal_selection).map(([item, quantity]) => (
              <li key={item}>
                {item}: {quantity.toFixed(2)} units
              </li>
            ))}
          </ul>
          <p>
            <b>Total Cost:</b> ₹{result.total_cost.toFixed(2)}
          </p>
        </div>
      )}
    </div>
  );
};

export default FoodItemSelector;
