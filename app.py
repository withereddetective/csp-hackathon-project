import csv  # for reading the csv file
import sys  # for accessing system-specific parameters and functions
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)  # for creating gui widgets
from PySide6.QtCore import Qt, QUrl  # for qt core functionality
from PySide6.QtGui import QDesktopServices  # for opening urls in browser
from puter import PuterAI  # for puter ai api calls


"""
THE ORIGINAL PURPOSE FOR THE DOMAINS WAS TO FETCH LOGOS FOR EACH COLLEGE,
BUT DUE TO TIME CONSTRAINTS THIS FEATURE WAS NOT IMPLEMENTED.
ALSO, BRANDFETCH API IS GOING TO SEND A MISSILE TO MY HOUSE.    
"""

"""
START OF PUTER AI API CODE
THIS CODE FETCHES COLLEGE DESCRIPTIONS FROM PUTER AI API
"""
# cache to store college descriptions to avoid duplicate api calls
college_descriptions_cache = {}

# global puter ai client (initialized on first use)
puter_client = None

def initialize_puter_client():
    """
    initialize the puter ai client using environment variables.
    returns the client if successful, none otherwise.
    """
    global puter_client
    
    if puter_client is not None:
        return puter_client
    
    try:
        puter_client = PuterAI(username="hackathon_test", password="seguinhs2026")
        if puter_client.login():
            return puter_client
        return None
    except Exception:
        return None

def get_college_description(college_name: str) -> str:
    """
    fetches a college description from puter ai api.
    uses caching to avoid duplicate api calls.
    """
    # check if description is already cached
    if college_name in college_descriptions_cache:
        return college_descriptions_cache[college_name]
    
    # initialize puter client
    client = initialize_puter_client()
    if client is None:
        return "error: puter.js credentials not set. set PUTER_USERNAME and PUTER_PASSWORD environment variables."
    
    try:
        # call puter ai to generate college description
        prompt = f"provide a brief 2-3 sentence description of {college_name} as a college. be concise and informative."
        description = client.chat(prompt)
        
        # cache the description
        college_descriptions_cache[college_name] = description
        
        return description
    except Exception as e:
        # return error message if api call fails
        return f"error fetching description: {str(e)}"

"""
END OF PUTER AI API CODE
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
        self.setWindowTitle("college finder")  # set the window title to be shown in the window header
        font = self.font()                     # get default font from the widget
        font.setPointSize(14)                  # increase font size to 14pt for better readability because the default is tiny
        self.setFont(font)                     # apply the larger font to the entire widget and all children
        
        # store the main layout for switching between views
        self.main_layout = QVBoxLayout()       # create a vertical layout that will hold either the table view or description view
        self.current_view = "table"            # track which view is currently displayed (table or description)
        self.current_college = None            # store current college name for description view
        
        # create the table view
        self.create_table_view()               # build the initial table view with input and results
        
        self.setLayout(self.main_layout)       # set the main layout for the window
        self.resize(1000, 600)                 # set initial window size to 1000x600 pixels

    def clear_layout(self, layout):
        """recursively clear a layout's children (widgets and sub-layouts)."""
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)

    def create_table_view(self):
        """create the main table view for college recommendations"""
        self.clear_layout(self.main_layout)  # clear main layout
        
        layout = QVBoxLayout()  # create main vertical layout to arrange widgets top to bottom

        top_layout = QHBoxLayout()                                # create horizontal layout for input controls
        self.sat_label = QLabel("what is your sat score?: ")      # create label text for sat input
        self.sat_input = QLineEdit()                              # create text input field for user to enter sat score
        self.sat_input.returnPressed.connect(self.find_colleges)  # trigger search when user presses enter
        self.find_button = QPushButton("find colleges")           # create button widget with text
        self.find_button.clicked.connect(self.find_colleges)      # connect button click signal to search function
        top_layout.addWidget(self.sat_label)                      # add label to horizontal layout
        top_layout.addWidget(self.sat_input)                      # add input field to horizontal layout
        top_layout.addWidget(self.find_button)                    # add button to horizontal layout
        layout.addLayout(top_layout)                              # add the horizontal layout to the main vertical layout

        self.table = QTableWidget()                                                                     # create table widget to display results
        self.table.setColumnCount(4)                                                                    # set table to have 4 columns
        self.table.setHorizontalHeaderLabels(["name", "avg sat", "acceptance rate", "ai description"])  # label each column
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)                         # stretch columns to fit available width
        layout.addWidget(self.table)                                                                    # add table to main vertical layout

        self.main_layout.addLayout(layout)
        self.current_view = "table"

    def create_description_view(self, college_name: str):
        """create a view displaying the college description"""
        # clear main layout
        self.clear_layout(self.main_layout)
        
        layout = QVBoxLayout()  # create vertical layout for description view
        
        # back button at top
        back_button = QPushButton("back")                  # create button to return to table view
        back_button.clicked.connect(self.show_table_view)  # connect button to function that shows table
        layout.addWidget(back_button)                      # add back button to the layout
        
        # title
        title_prefix = "the " if college_name.lower().startswith("university") else ""  # add 'the' if college name starts with 'university'
        title = QLabel(f"description of {title_prefix}{college_name} using puter ai")   # create title label showing college name
        title_font = title.font()                                                       # get the default font from the label
        title_font.setPointSize(16)                                                     # set font size to 16pt for prominent title
        title_font.setBold(True)                                                        # make the title bold for emphasis
        title.setFont(title_font)                                                       # apply the styled font to the title label
        layout.addWidget(title)                                                         # add title label to the layout
        
        # description
        description = get_college_description(college_name)  # fetch description from puter ai
        description_label = QLabel(description)              # create label to display the ai-generated description
        description_label.setWordWrap(True)                  # enable word wrapping so text flows to multiple lines
        description_label.setStyleSheet("padding: 10px;")    # add padding for readability
        # increase font size for better readability of ai-generated content
        desc_font = description_label.font()                 # get the default font from the label
        desc_font.setPointSize(12)                           # set font size to 12pt for easy reading
        description_label.setFont(desc_font)                 # apply the larger font to the description
        layout.addWidget(description_label)                  # add description label to the layout
        
        # add stretch to push content to top
        layout.addStretch()  # add empty space at bottom to keep content aligned to top
        
        self.main_layout.addLayout(layout)   # add the description layout to the main window layout
        self.current_view = "description"    # update current view tracker
        self.current_college = college_name  # store the college name for reference

    def show_table_view(self):
        """switch back to the table view"""
        self.create_table_view()
        # repopulate the table with the previous search results if available
        if hasattr(self, 'last_recommended'):
            self.populate_table(self.last_recommended)

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
        self.last_recommended = recommended  # store for potential return from description view
        self.populate_table(recommended)

    def populate_table(self, recommended):
        """populate the table with college data"""
        self.table.setRowCount(len(recommended))  # set number of rows in table based on recommendation count

        # populate table with college data
        for row, college in enumerate(recommended):  # loop through each recommended college
            # create a button for the college name that links to their website
            name_button = QPushButton(college.name)  # create clickable button with college name
            name_button.setCursor(Qt.PointingHandCursor)  # change cursor to pointer to indicate clickability
            # style the button to look like a hyperlink (blue text, underline, no visible button border)
            name_button.setStyleSheet("color: #6699FF; text-decoration: underline; border: none; background: none; padding-left: 5px; text-align: left; font-size: 14pt;")
            # create lambda to capture domain in closure so each button has the correct url
            url = f"https://{college.domain}" if college.domain else ""
            # connect button click to open the url in default browser
            name_button.clicked.connect(lambda checked, u=url: QDesktopServices.openUrl(QUrl(u)) if u else None)
            self.table.setCellWidget(row, 0, name_button)  # add name button to first column
            
            self.table.setItem(row, 1, QTableWidgetItem(str(college.avg_sat)))  # add average sat score to second column
            self.table.setItem(row, 2, QTableWidgetItem(f"{college.acceptance_rate}%"))  # add acceptance rate to third column
            
            # create learn more button to view ai description
            learn_more_button = QPushButton("learn more")  # create button with text
            # connect button click to show description view for this college
            learn_more_button.clicked.connect(lambda checked, name=college.name: self.create_description_view(name))
            self.table.setCellWidget(row, 3, learn_more_button)  # add learn more button to fourth column

def main():
    app = QApplication(sys.argv)  # create the main qt application object, passing command line arguments
    window = CollegeFinder()      # create an instance of our collegefinder window
    window.show()                 # show the window on the screen
    sys.exit(app.exec())          # start the application's event loop and exit when the window is closed


if __name__ == "__main__":
    main()