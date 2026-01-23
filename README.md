# 🎓 College Picker
> A data-driven GUI tool to find the best-fit colleges based on your SAT scores.

This tool helps students identify target schools by processing historical college data and ranking them based on score proximity and selectivity, all through an intuitive graphical interface.

## 🚀 Features
- **Smart Filtering:** Uses a custom SAT range buffer to find realistic targets.
- **Dynamic Sorting:** Ranks colleges by the absolute difference between your score and their average.
- **Selectivity Tiering:** Secondary sorting by acceptance rate to highlight competitive matches.
- **Top 10 Picks:** Provides a curated list of the best 10 options in a table.
- **User-Friendly GUI:** Built with PySide6 for easy input and visualization.

## 🛠️ How It Works
1. **Data Loading:** Parses `data.csv` to load institutional statistics.
2. **Initial Filter:** Applies a default score buffer to narrow down the list.
3. **Advanced Ranking:**
   - Primary Sort: `abs(College SAT - User SAT)` (closest match first).
   - Secondary Sort: Acceptance rate (selectivity preference).
4. **GUI Display:** Shows the top 10 results in a table with columns for Name, Avg SAT, and Acceptance Rate.

## 📋 Prerequisites
- Python 3.x
- PySide6 library
- A `data.csv` file in the root directory with the following headers:  
  `College Name, Acceptance Rate, Average SAT`

## ⚙️ Installation & Usage
```bash
# Install dependencies
pip install PySide6

# Run the application
python app.py
```

The GUI window will open, allowing you to enter your SAT score and view recommendations.
