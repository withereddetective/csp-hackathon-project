# 🎓 College Picker
> A data-driven tool to find the best-fit colleges based on your SAT scores.

This tool helps students identify target schools by processing historical college data and ranking them based on score proximity and selectivity.

## 🚀 Features
- **Smart Filtering:** Uses a custom SAT range buffer to find realistic targets.
- **Dynamic Sorting:** Ranks colleges by the absolute difference between your score and their average.
- **Selectivity Tiering:** Secondary sorting by acceptance rate to highlight competitive matches.
- **Top 10 Picks:** Provides a curated list of the best 10 options.

## 🛠️ How It Works
1. **Data Loading:** Parses `data.csv` to load institutional statistics.
2. **Initial Filter:** Applies a user-defined score buffer to narrow down the list.
3. **Advanced Ranking:**
   - Primary Sort: `abs(College SAT - User SAT)` (closest match first).
   - Secondary Sort: Acceptance rate (selectivity preference).
4. **Output:** Prints the top 10 results to the console.

## 📋 Prerequisites
Ensure you have a `data.csv` file in the root directory with the following headers:
`College Name, Average SAT, Acceptance Rate`

## ⚙️ Installation & Usage
```bash
# Clone the repository
git clone https://github.com

# Run the application
python main.py
