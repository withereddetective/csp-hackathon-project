import csv  # for reading the csv file
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox  # for creating GUI widgets like windows, buttons, and tables
import sys  # for accessing system-specific parameters and functions


class College:  # just has 3 values
    def __init__(self, name: str, acceptance_rate: int, avg_sat: int):
        self.name = name
        self.acceptance_rate = acceptance_rate
        self.avg_sat = avg_sat

def get_data() -> list:
    """
    data set from http://github.com/frishberg/US-College-Ranking-Data
    the data has 3 items per college
    1. name
    2. acceptance rate
    3. average sat
    """
    list_of_colleges = []  # need this to contain and sort lists
    with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=',')
        # skip the header row because it is labeling
        next(csv_reader)
        for row in csv_reader:
            # each 'row' is a list of column values
            # the magic numbers below are 0 = name, 1 = acceptance rate, 2 = average gpa
            list_of_colleges.append(College(str(row[0]), 
                                            int(row[1]), 
                                            int(row[2])))
    # then sort and return by average sat and then by acceptance rate if i have to
    return sorted(list_of_colleges, key=lambda student: (student.avg_sat, -student.acceptance_rate))

def filter_colleges(list_of_colleges: list, user_sat_score: int) -> list:  # originally in get_reccommended_colleges() but this makes it easier to read
    # filtering colleges by the range the user provides
    SAT_RANGE_BUFFER = 100
    min_sat = user_sat_score - SAT_RANGE_BUFFER
    max_sat = user_sat_score + SAT_RANGE_BUFFER
    filtered_colleges = [
        college for college in list_of_colleges 
        if min_sat <= college.avg_sat <= max_sat
    ]

    # if no colleges are found in that range, expand the search slightly
    while not filtered_colleges:
        SAT_RANGE_BUFFER += 100
        min_sat -= 100
        max_sat += 100
        filtered_colleges = [
            college for college in list_of_colleges 
            if min_sat <= college.avg_sat <= max_sat
        ]
    
    # ensure at least 10 colleges are found
    while len(filtered_colleges) < 10:
        SAT_RANGE_BUFFER += 100
        min_sat -= 100
        max_sat += 100
        filtered_colleges = [
            college for college in list_of_colleges 
            if min_sat <= college.avg_sat <= max_sat
        ]
    return filtered_colleges

def get_reccommended_colleges(list_of_colleges: list, user_sat_score: int) -> list:
    list_of_colleges = filter_colleges(list_of_colleges, user_sat_score)

    # sort the filtered list using a custom key function
    # the key prioritizes:
    # a) proximity to the users sat score (closer is better, abs(diff) is smaller)
    # b) acceptance Rate (higher acceptance rate is usually safer, so we sort in descending order for secondary sort)
    def sorting_key(college):
        sat_difference = abs(college.avg_sat - user_sat_score)
        # using a tuple for sorting: (primary_key, secondary_key)
        # python sorts tuples element by element.
        # need to negate acceptance_rate to sort it in descending order (higher rate first).
        return (sat_difference, -college.acceptance_rate)
    
    # sort the list using the custom key
    list_of_colleges.sort(key=sorting_key)

    # return the top 10 results
    return list_of_colleges[:10]

class CollegeFinder(QWidget):
    def __init__(self):
        super().__init__()                     # call the parent QWidget constructor to initialize the window
        self.colleges = get_data()             # load data once
        self.setWindowTitle("college finder")  # set the title of the window that appears at the top
                                               # everything was too small so increasing font size
        font = self.font()                     # get the current font of the widget
        font.setPointSize(14)                  # set the font size to 14 points to make text bigger
        self.setFont(font)                     # apply the font to this widget and its children
        layout = QVBoxLayout()                 # create a vertical layout to arrange widgets from top to bottom
        
        # top layout
        top_layout = QHBoxLayout()                            # create a horizontal layout for the top row (label, input, button)
        self.sat_label = QLabel("what is your sat score?: ")  # create a label widget to display text next to the input
        self.sat_input = QLineEdit()                          # create a line edit widget for user to type their SAT score
        self.sat_input.returnPressed.connect(self.find_colleges)  # connect the return pressed signal to the find_colleges method
        self.find_button = QPushButton("find colleges")       # create a button widget that the user clicks to find colleges
        self.find_button.clicked.connect(self.find_colleges)  # connect the button's clicked signal to the find_colleges method
        top_layout.addWidget(self.sat_label)                  # add the label to the horizontal layout
        top_layout.addWidget(self.sat_input)                  # add the input field to the horizontal layout
        top_layout.addWidget(self.find_button)                # add the button to the horizontal layout
        layout.addLayout(top_layout)                          # add the horizontal layout to the main vertical layout
        
        # table
        self.table = QTableWidget()                                                   # create a table widget to display the college recommendations in rows and columns
        self.table.setColumnCount(3)                                                  # set the number of columns in the table to 3
        self.table.setHorizontalHeaderLabels(["name", "avg sat", "acceptance rate"])  # set the labels for the table headers
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)       # make columns stretch to fill the available width
        self.table.setColumnWidth(0, 400)                                             # set the width of the first column (Name) to 400 pixels to give it more space
        layout.addWidget(self.table)                                                  # add the table to the main vertical layout
        
        self.setLayout(layout)  # set the main layout for this widget
        self.resize(800, 500)   # resize the window to 800 pixels wide and 500 pixels tall, making it longer and giving space to columns
    
    def find_colleges(self):
        try:
            user_sat_score = int(self.sat_input.text())                                  # try to convert the text from the input field to an integer
        except ValueError:
            QMessageBox.warning(self, "invalid input", "give an integer ONLY")           # display a warning dialog box with title and message if conversion fails
            return                                                                       # exit the method early if input is invalid
        if not (400 <= user_sat_score <= 1600):
            QMessageBox.warning(self, "invalid score", "input a valid score within the range of 400-1600")  # display warning if score is out of range
            return                                                                       # exit the method early if score is invalid
        recommended = get_reccommended_colleges(self.colleges, user_sat_score)           # get the list of recommended colleges based on the user's score
        self.table.setRowCount(0)                                                        # clear all rows from the table by setting row count to 0
        for i, college in enumerate(recommended, 1):                                     # loop through each recommended college, starting index from 1
            self.table.insertRow(i-1)                                                    # insert a new row at the end of the table (i-1 because rows are 0-indexed)
            self.table.setItem(i-1, 0, QTableWidgetItem(college.name))                   # create and set a table item for the college name in column 0
            self.table.setItem(i-1, 1, QTableWidgetItem(str(college.avg_sat)))           # create and set a table item for the average SAT in column 1
            self.table.setItem(i-1, 2, QTableWidgetItem(f"{college.acceptance_rate}%"))  # create and set a table item for the acceptance rate as percentage in column 2

def main():
    app = QApplication(sys.argv)  # create the main Qt application object, passing command line arguments
    window = CollegeFinder()      # create an instance of our CollegeFinder window
    window.show()                 # show the window on the screen
    sys.exit(app.exec())          # start the application's event loop and exit when the window is closed


if __name__ == "__main__":
    main()