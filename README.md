# college picker
> a data-driven gui tool to find the best-fit colleges based on your sat scores.

this tool helps students identify target schools by processing historical college data and ranking them based on score proximity and selectivity, all through an intuitive graphical interface. college descriptions are powered by puter.js ai.

## features
- **smart filtering:** uses a custom sat range buffer to find realistic targets.
- **dynamic sorting:** ranks colleges by the absolute difference between your score and their average.
- **selectivity tiering:** secondary sorting by acceptance rate to highlight competitive matches.
- **top 10 picks:** provides a curated list of the best 10 options in a table.
- **ai descriptions:** click "learn more" to view ai-generated descriptions of each college powered by puter.js.
- **description caching:** descriptions are cached during the session to minimize api calls.
- **clickable college links:** college names link directly to their official websites.
- **user-friendly gui:** built with pyside6 for easy input and visualization.

## how it works
1. **data loading:** parses `data.csv` to load institutional statistics.
2. **initial filter:** applies a default score buffer to narrow down the list.
3. **advanced ranking:**
   - primary sort: `abs(college sat - user sat)` (closest match first).
   - secondary sort: acceptance rate (selectivity preference).
4. **gui display:** shows the top 10 results in a table with names, avg sat, and acceptance rates.
5. **ai descriptions:** click "learn more" to fetch and display ai-generated college descriptions.

## prerequisites
- python 3.x
- pyside6 library
- puter-python-sdk library
- puter.js credentials (free account at https://puter.com)
- a `data.csv` file in the root directory with the following headers:  
  `university name, acceptance rate, average sat, domain`

## installation & usage
```bash
# install dependencies
pip install pyside6 puter-python-sdk

# run the application
python app.py
```

the gui window will open, allowing you to enter your sat score and view recommendations. click "learn more" to see ai-generated descriptions for each college.

## environment variables
- `PUTER_USERNAME` - your puter.js username
- `PUTER_PASSWORD` - your puter.js password

without these set, the "learn more" feature will display an error message.

## known issues
none at this time.