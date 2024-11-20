import React, { useState } from "react";
import axios from "axios";

const FoodItemSelector = () => {
  const [selectedItems, setSelectedItems] = useState([]);
  const [result, setResult] = useState(null);

  const foodItems = ["Paneer Toast", "Grilled Sandwich", "Aloo Samosa"];

  const handleCheckboxChange = (item) => {
    setSelectedItems((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post("https://diet-backend-d1gj.onrender.com/optimize", {
        selected_items: selectedItems,
      });
      
      setResult(response.data);
    } catch (error) {
      console.error("Error fetching optimization results:", error);
    }
  };

  return (
    <div>
      <h2>Select Food Items</h2>
      {foodItems.map((item) => (
        <div key={item}>
          <input
            type="checkbox"
            value={item}
            onChange={() => handleCheckboxChange(item)}
          />
          {item}
        </div>
      ))}
      <button onClick={handleSubmit}>Optimize</button>
      {result && (
        <div>
          <h3>Result</h3>
          <p>Optimal Selection: {JSON.stringify(result.optimal_selection)}</p>
          <p>Total Cost: {result.total_cost}</p>
        </div>
      )}
    </div>
  );
};

export default FoodItemSelector;
