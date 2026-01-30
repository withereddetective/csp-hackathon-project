# college picker
> a data-driven gui tool to find the best-fit colleges based on your sat scores.

this tool helps students identify target schools by processing historical college data and ranking them based on score proximity and selectivity, all through an intuitive graphical interface.

## features
- **smart filtering:** uses a custom sat range buffer to find realistic targets.
- **dynamic sorting:** ranks colleges by the absolute difference between your score and their average.
- **selectivity tiering:** secondary sorting by acceptance rate to highlight competitive matches.
- **top 10 picks:** provides a curated list of the best 10 options in a table.
- **user-friendly gui:** built with pyside6 for easy input and visualization.

## how it works
1. **data loading:** parses `data.csv` to load institutional statistics.
2. **initial filter:** applies a default score buffer to narrow down the list.
3. **advanced ranking:**
   - primary sort: `abs(college sat - user sat)` (closest match first).
   - secondary sort: acceptance rate (selectivity preference).
4. **gui display:** shows the top 10 results in a table with names, avg sat, and acceptance rates.

## prerequisites
- python 3.x
- pyside6 library
- a `data.csv` file in the root directory with the following headers:  
  `university name, acceptance rate, average sat, domain`

## installation & usage
```bash
# install dependencies
pip install pyside6

# run the application
python app.py
```

the gui window will open, allowing you to enter your sat score and view recommendations.

## known issues
none at this time.