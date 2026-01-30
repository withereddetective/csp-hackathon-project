import csv  # for reading the csv file
import sys  # for accessing system-specific parameters and functions
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)  # for creating gui widgets
from PySide6.QtCore import Qt, QUrl  # for qt core functionality
from PySide6.QtGui import QDesktopServices  # for opening urls in browser


"""
THE ORIGINAL PURPOSE FOR THE DOMAINS WAS TO FETCH LOGOS FOR EACH COLLEGE,
BUT DUE TO TIME CONSTRAINTS THIS FEATURE WAS NOT IMPLEMENTED.
ALSO, BRANDFETCH API IS GOING TO SEND A MISSILE TO MY HOUSE.    
"""


"""
START OF CODE WRITTEN DURING HACKATHON
ANY COMMENT THAT STARTS WITH 'ADDED' WAS ADDED AFTER THE HACKATHON
"""
class College:  # just has 4 values
    def __init__(self, name: str, acceptance_rate: int, avg_sat: int, domain: str = ""):  # domain added after hackathon
        self.name = name
        self.acceptance_rate = acceptance_rate
        self.avg_sat = avg_sat
        self.domain = domain  # domain for logo fetching

def get_data() -> list:
    """
    data set from http://github.com/frishberg/US-College-Ranking-Data
    the data has 4 items per college
    1. name
    2. acceptance rate
    3. average sat
    4. domain
    """
    list_of_colleges = []  # need this to contain and sort lists
    # added try-except to handle file reading errors and provide graceful exit
    try:
        with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            # skip the header row because it is labeling
            next(csv_reader)
            for row in csv_reader:
                # each 'row' is a list of column values
                # the magic numbers below are 0 = name, 1 = acceptance rate, 2 = average sat, 3 = domain
                try:  # added try-except to skip bad rows in csv and continue processing
                    list_of_colleges.append(College(str(row[0]), 
                                                    int(row[1]), 
                                                    int(row[2]),
                                                    str(row[3]) if len(row) > 3 else ""))  # domain added after hackathon
                except (ValueError, IndexError) as e:
                    print(f"skipping bad row in csv: {row} - {e}")
                    continue
    except FileNotFoundError:
        print("error: data.csv file not found. please ensure it is in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"error reading data.csv: {e}")
        sys.exit(1)
    # added check for empty data after processing to ensure valid data exists
    if not list_of_colleges:
        print("error: no valid data found in data.csv.")
        sys.exit(1)
    # then sort and return by average sat and then by acceptance rate if i have to
    return sorted(list_of_colleges, key=lambda student: (student.avg_sat, -student.acceptance_rate))

def filter_colleges(list_of_colleges: list, user_sat_score: int) -> list:  # originally in get_recommended_colleges() but this makes it easier to read
    # filtering colleges by the range the user provides
    SAT_RANGE_BUFFER = 100
    min_sat = user_sat_score - SAT_RANGE_BUFFER
    max_sat = user_sat_score + SAT_RANGE_BUFFER
    filtered_colleges = [
        college for college in list_of_colleges 
        if min_sat <= college.avg_sat <= max_sat
    ]

    # if at least 10 colleges are not found in that range, expand the search slightly
    while len(filtered_colleges) < 10:
        SAT_RANGE_BUFFER += 100
        min_sat -= 100
        max_sat += 100
        filtered_colleges = [
            college for college in list_of_colleges 
            if min_sat <= college.avg_sat <= max_sat
        ]
    return filtered_colleges

def get_recommended_colleges(list_of_colleges: list, user_sat_score: int) -> list:
    list_of_colleges = filter_colleges(list_of_colleges, user_sat_score)

    """
    sort the filtered list using a custom key function
    the key prioritizes:
    a) proximity to the users sat score (closer is better, abs(diff) is smaller)
    b) acceptance rate (higher acceptance rate is usually safer, so we sort in descending order for secondary sort)
    """
    def sorting_key(college):
        sat_difference = abs(college.avg_sat - user_sat_score)
        """
        using a tuple for sorting: (primary_key, secondary_key)
        python sorts tuples element by element.
        need to negate acceptance_rate to sort it in descending order (higher rate first).
        """
        return (sat_difference, -college.acceptance_rate)
    
    # sort the list using the custom key
    list_of_colleges.sort(key=sorting_key)

    # return the top 10 results
    return list_of_colleges[:10]
"""
END OF CODE WRITTEN DURING HACKATHON
"""

class CollegeFinder(QWidget):  # this be the main window
    def __init__(self):
        super().__init__()                     # call parent constructor
        self.colleges = get_data()             # load college data from csv
        self.setWindowTitle("college finder")  # set the window title
        font = self.font()                     # get default font
        font.setPointSize(14)                  # increase font size for better readability because the default is tiny
        self.setFont(font)                     # apply font to the widget
        layout = QVBoxLayout()                 # main vertical layout to arrange widgets top to bottom

        top_layout = QHBoxLayout()                                # horizontal layout for input and button
        self.sat_label = QLabel("what is your sat score?: ")      # label for sat input
        self.sat_input = QLineEdit()                              # text input for sat score
        self.sat_input.returnPressed.connect(self.find_colleges)  # connect enter key to search
        self.find_button = QPushButton("find colleges")           # button to trigger search
        self.find_button.clicked.connect(self.find_colleges)      # connect button click to search
        top_layout.addWidget(self.sat_label)                      # add label to horizontal layout
        top_layout.addWidget(self.sat_input)                      # add input to horizontal layout
        top_layout.addWidget(self.find_button)                    # add button to horizontal layout
        layout.addLayout(top_layout)                              # add horizontal layout to main vertical layout

        self.table = QTableWidget()                                                   # table to display results
        self.table.setColumnCount(3)                                                  # 3 columns: name, avg sat, acceptance rate
        self.table.setHorizontalHeaderLabels(["name", "avg sat", "acceptance rate"])  # label the columns
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)       # stretch columns to fit the table width
        layout.addWidget(self.table)                                                  # add table to main vertical layout

        self.setLayout(layout)
        self.resize(1000, 600)

    def find_colleges(self):
        # validate user input for sat score
        try:
            user_sat_score = int(self.sat_input.text())  # convert input to integer
            if not 400 <= user_sat_score <= 1600:  # check if within valid sat range
                raise ValueError("sat score out of range")
        except ValueError:
            # show warning dialog if input is invalid
            QMessageBox.warning(self, "invalid input", "please enter a valid sat score between 400 and 1600.")
            return  # exit function without proceeding
        
        # get recommended colleges based on sat score
        recommended = get_recommended_colleges(self.colleges, user_sat_score)
        self.table.setRowCount(len(recommended))  # set number of rows in table

        # populate table with college data
        for row, college in enumerate(recommended):
            # create a button for the college name that links to their website
            name_button = QPushButton(college.name)  # create button with college name
            name_button.setCursor(Qt.PointingHandCursor)  # change cursor to pointer
            name_button.setStyleSheet("color: #6699FF; text-decoration: underline; border: none; background: none; padding-left: 5px; text-align: left; font-size: 14pt;")  # style as hyperlink with left alignment and matching font size because the stupid hyperlink style messes up the alignment and size and the color is ugly
            # create lambda to capture domain in closure
            url = f"https://{college.domain}" if college.domain else ""
            name_button.clicked.connect(lambda checked, u=url: QDesktopServices.openUrl(QUrl(u)) if u else None)
            self.table.setCellWidget(row, 0, name_button)  # add button to table
            
            self.table.setItem(row, 1, QTableWidgetItem(str(college.avg_sat)))  # average sat
            self.table.setItem(row, 2, QTableWidgetItem(f"{college.acceptance_rate}%"))  # acceptance rate

def main():
    app = QApplication(sys.argv)  # create the main qt application object, passing command line arguments
    window = CollegeFinder()      # create an instance of our collegefinder window
    window.show()                 # show the window on the screen
    sys.exit(app.exec())          # start the application's event loop and exit when the window is closed


if __name__ == "__main__":
    main()