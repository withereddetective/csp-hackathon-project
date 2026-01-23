import csv  # for reading the csv file
import sys  # for accessing system-specific parameters and functions
import requests  # for making http requests to fetch logos
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)  # for creating gui widgets
from PySide6.QtGui import QIcon, QPixmap, QImage  # for handling images and icons in the gui
from PySide6.QtCore import Qt, QThreadPool, QObject, Signal  # for threading and qt signals


"""
START OF COLLEGE LOGO FETCHING CODE USING CLEARBIT API
THIS IS A SIMPLER ALTERNATIVE TO WIKIPEDIA SCRAPING
IT STILL ISNT WORKING IDK WHAT IM DOING
"""
known_domains = {
    "Massachusetts Institute of Technology": "mit.edu",
    "Stanford University": "stanford.edu",
    "Harvard University": "harvard.edu",
    "California Institute of Technology": "caltech.edu",
    "University of Chicago": "uchicago.edu",
    "Princeton University": "princeton.edu",
    "Yale University": "yale.edu",
    "Columbia University": "columbia.edu",
    "University of Pennsylvania": "upenn.edu",
    "Johns Hopkins University": "jhu.edu",
    "Northwestern University": "northwestern.edu",
    "Duke University": "duke.edu"
    # add more later
}
def get_college_logo(college_name: str) -> bytes | None:
    # check known domains first for accuracy
    if college_name in known_domains:
        domain = known_domains[college_name]
    else:
        # guess the domain by extracting key word and adding .edu
        # improved domain guessing: handle commas for campus names, clean punctuation
        name_lower = college_name.lower()
        if ',' in name_lower:
            domain_base = name_lower.split(',')[-1].strip().split()[0]
        elif "university of" in name_lower:
            parts = name_lower.split()
            try:
                idx = parts.index("of")
                domain_base = ' '.join(parts[idx + 1:]).split()[-1]  # take the last word after "of"
            except ValueError:
                domain_base = parts[0]
        else:
            domain_base = name_lower.split()[0]
        # clean domain_base by removing punctuation and keeping only alphanumeric
        domain_base = ''.join(c for c in domain_base if c.isalnum())
        domain = f"{domain_base}.edu"
    
    print(f"trying domain: {domain} for {college_name}")  # added debug print to see attempted domains
    url = f"https://logo.clearbit.com/{domain}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.content
        else:
            print(f"status {r.status_code} for {domain}")  # added to see if 404 or other
            # try alternative domain if available (e.g., for state universities, try u[state].edu)
            if "university of" in college_name.lower():
                parts = college_name.lower().split()
                if len(parts) > 2:
                    state = parts[-1]
                    alt_domain = f"u{state}.edu"
                    print(f"trying alternative domain: {alt_domain} for {college_name}")
                    alt_url = f"https://logo.clearbit.com/{alt_domain}"
                    r_alt = requests.get(alt_url, timeout=5)
                    if r_alt.status_code == 200:
                        return r_alt.content
                    else:
                        print(f"status {r_alt.status_code} for {alt_domain}")
    except requests.exceptions.ConnectionError:
        # no internet or dns issue, skip printing to avoid spam
        pass
    except Exception as e:
        print(f"logo fetch error for {college_name}: {e}")
    return None
"""
END OF COLLEGE LOGO FETCHING CODE
"""

"""
START OF CODE WRITTEN DURING HACKATHON
ANY COMMENT THAT STARTS WITH 'ADDED' WAS ADDED AFTER THE HACKATHON
"""
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
    # added try-except to handle file reading errors and provide graceful exit
    try:
        with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            # skip the header row because it is labeling
            next(csv_reader)
            for row in csv_reader:
                # each 'row' is a list of column values
                # the magic numbers below are 0 = name, 1 = acceptance rate, 2 = average gpa
                # added try-except to skip bad rows in csv and continue processing
                try:
                    list_of_colleges.append(College(str(row[0]), 
                                                    int(row[1]), 
                                                    int(row[2])))
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
    b) acceptance Rate (higher acceptance rate is usually safer, so we sort in descending order for secondary sort)
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

class LogoWorker(QObject):
    finished = Signal(int, bytes)

    def __init__(self, row, college_name):
        super().__init__()
        self.row = row
        self.college_name = college_name

    def run(self):
        logo = get_college_logo(self.college_name)
        self.finished.emit(self.row, logo or b"")

class CollegeFinder(QWidget):  # this is the main window
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()  # thread pool for running logo fetching tasks in background
        self.colleges = get_data()
        self.setWindowTitle("college finder")
        font = self.font()
        font.setPointSize(14)
        self.setFont(font)
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.sat_label = QLabel("what is your sat score?: ")
        self.sat_input = QLineEdit()
        self.sat_input.returnPressed.connect(self.find_colleges)
        self.find_button = QPushButton("find colleges")
        self.find_button.clicked.connect(self.find_colleges)
        top_layout.addWidget(self.sat_label)
        top_layout.addWidget(self.sat_input)
        top_layout.addWidget(self.find_button)
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["logo", "name", "avg sat", "acceptance rate"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 400)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.resize(1000, 600)

    def find_colleges(self):
        # added input validation for sat score
        try:
            user_sat_score = int(self.sat_input.text())
            if not 400 <= user_sat_score <= 1600:
                raise ValueError("SAT score out of range")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid SAT score between 400 and 1600.")
            return
        
        recommended = get_recommended_colleges(self.colleges, user_sat_score)
        self.find_button.setEnabled(False)
        self.find_button.setText("loading...")
        self.table.setRowCount(len(recommended))

        for row, college in enumerate(recommended):
            self.table.setRowHeight(row, 85)
            self.table.setItem(row, 1, QTableWidgetItem(college.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(college.avg_sat)))
            self.table.setItem(row, 3, QTableWidgetItem(f"{college.acceptance_rate}%"))
            self.table.setItem(row, 0, QTableWidgetItem("loading…"))

            worker = LogoWorker(row, college.name)  # create a worker to fetch logo in a separate thread
            worker.finished.connect(self.set_logo)  # connect the finished signal to update the table
            self.threadpool.start(worker.run)  # start the worker in the thread pool

        self.find_button.setEnabled(True)
        self.find_button.setText("find colleges")

    def set_logo(self, row, logo_bytes):
        item = QTableWidgetItem()
        if logo_bytes:
            image = QImage.fromData(logo_bytes)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
        self.table.setItem(row, 0, item)

def main():
    app = QApplication(sys.argv)  # create the main qt application object, passing command line arguments
    window = CollegeFinder()      # create an instance of our CollegeFinder window
    window.show()                 # show the window on the screen
    sys.exit(app.exec())          # start the application's event loop and exit when the window is closed


if __name__ == "__main__":
    main()