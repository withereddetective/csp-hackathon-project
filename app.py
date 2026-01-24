import csv  # for reading the csv file
import sys  # for accessing system specific parameters and functions
import requests  # for making http requests to fetch logos
import time  # for adding delays to avoid api rate limits
import random  # for randomizing delays
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)  # for creating gui widgets
from PySide6.QtGui import QIcon, QPixmap, QImage  # for handling images and icons in the gui
from PySide6.QtCore import Qt, QThreadPool, QObject, Signal  # for threading and qt signals


"""
START OF COLLEGE LOGO FETCHING CODE USING BRAND FETCH API
THIS IS THE WORKING VERSION THAT FETCHES COLLEGE LOGOS
THIS TOOK ME WAY TOO LONG TO FIGURE OUT BUT IT IS FINALLY WORKING
"""
known_domains = {}
def get_college_logo(college_name: str, domain: str = "") -> bytes | None:
    # determine the domain for the college
    # first, use provided domain if available
    if domain:
        pass
    # then, check if it's a known college with a predefined domain for accuracy
    elif college_name in known_domains:
        domain = known_domains[college_name]
    else:
        # if not known, guess the domain based on the college name
        # convert to lowercase for processing
        name_lower = college_name.lower()
        if ',' in name_lower:
            # handle names like "University of California, Berkeley" -> take "Berkeley"
            domain_base = name_lower.split(',')[-1].strip().split()[0]
        elif "university of" in name_lower:
            # for "University of X", take the last word after "of"
            parts = name_lower.split()
            try:
                idx = parts.index("of")
                domain_base = ' '.join(parts[idx + 1:]).split()[-1]
            except ValueError:
                domain_base = parts[0]
        else:
            # default: take the first word
            domain_base = name_lower.split()[0]
        # remove non alphanumeric characters to clean the domain base
        domain_base = ''.join(c for c in domain_base if c.isalnum())
        domain = f"{domain_base}.edu"
    
    # now use the brand fetch api to retrieve the logo
    # brand fetch provides brand assets including logos for domains
    api_key = "pX6Fb8fPSmowsrnaYqS7wTSPQZPY3Jrkc__eFi9BSZwhxzD2ew-uJ7DrlfZtPG1dEQzdTA5M49Yy1Uy_2X4oMA"  # replace with your actual api key, this is a demo key
    # construct the api url for the brand data
    url = f"https://api.brandfetch.io/v2/brands/{domain}"
    # set authorization header with bearer token
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        # make get request to brand fetch api with timeout
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # parse the json response
            data = r.json()
            # extract the logos array from the response
            logos = data.get('logos', [])
            if logos:
                # prefer png or svg formats for better quality
                for logo in logos:
                    formats = logo.get('formats', [])
                    for fmt in formats:
                        if fmt.get('format') in ['png', 'svg']:
                            logo_url = fmt.get('src')
                            if logo_url:
                                # download the logo image
                                r_logo = requests.get(logo_url, timeout=10)
                                if r_logo.status_code == 200:
                                    return r_logo.content
                # fallback: use the first available format
                logo_url = logos[0].get('formats', [{}])[0].get('src')
                if logo_url:
                    r_logo = requests.get(logo_url, timeout=10)
                    if r_logo.status_code == 200:
                        return r_logo.content
            # if no logos in response
            print(f"no logos found for {domain}")
        else:
            # api returned an error status
            print(f"brand fetch api status {r.status_code} for {domain}")
    except requests.exceptions.ConnectionError:
        # network issue, likely no internet
        print(f"connection error for brand fetch on {domain}")
        return b"no_internet"  # special return to indicate no internet
    except Exception as e:
        # other errors
        print(f"brand fetch error for {college_name}: {e}")
    return None
"""
END OF COLLEGE LOGO FETCHING CODE
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

class LogoWorker(QObject):  # worker class for fetching logos in background thread to avoid blocking ui
    finished = Signal(int, bytes)  # signal emitted when logo fetch is complete, passes row index and logo bytes

    def __init__(self, row, college_name, domain):
        super().__init__()
        self.row = row  # row index in the table
        self.college_name = college_name  # name of the college to fetch logo for
        self.domain = domain  # domain for logo fetching

    def run(self):
        # add random delay to stagger api requests and avoid rate limiting
        time.sleep(random.uniform(0.5, 2.0))
        # execute the logo fetching in the background thread
        logo = get_college_logo(self.college_name, self.domain)
        # emit signal with row and logo data (or empty bytes if failed)
        self.finished.emit(self.row, logo or b"")

class CollegeFinder(QWidget):  # main application window inheriting from QWidget
    def __init__(self):
        super().__init__()  # call parent constructor
        self.threadpool = QThreadPool()  # QThreadPool manages background threads for logo fetching
        self.colleges = get_data()  # load college data from csv
        self.setWindowTitle("college finder")  # set window title
        font = self.font()  # get default font
        font.setPointSize(14)  # increase font size for better readability
        self.setFont(font)  # apply font to the widget
        layout = QVBoxLayout()  # main vertical layout to arrange widgets top to bottom

        top_layout = QHBoxLayout()  # horizontal layout for input and button
        self.sat_label = QLabel("what is your sat score?: ")  # label for sat input
        self.sat_input = QLineEdit()  # text input for sat score
        self.sat_input.returnPressed.connect(self.find_colleges)  # connect enter key to search
        self.find_button = QPushButton("find colleges")  # button to trigger search
        self.find_button.clicked.connect(self.find_colleges)  # connect button click to search
        top_layout.addWidget(self.sat_label)
        top_layout.addWidget(self.sat_input)
        top_layout.addWidget(self.find_button)
        layout.addLayout(top_layout)

        self.table = QTableWidget()  # table to display results
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["logo", "name", "avg sat", "acceptance rate"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 160)  # increased for bigger logos
        self.table.setColumnWidth(1, 400)  # name column wider for long names
        layout.addWidget(self.table)

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
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid sat score between 400 and 1600.")
            return  # exit function without proceeding
        
        # get recommended colleges based on sat score
        recommended = get_recommended_colleges(self.colleges, user_sat_score)
        self.find_button.setEnabled(False)  # disable button to prevent multiple clicks
        self.find_button.setText("loading...")  # update button text to indicate loading
        self.table.setRowCount(len(recommended))  # set number of rows in table

        # populate table with college data and start logo fetching
        for row, college in enumerate(recommended):
            self.table.setRowHeight(row, 160)  # set row height for logo display
            self.table.setItem(row, 1, QTableWidgetItem(college.name))  # college name
            self.table.setItem(row, 2, QTableWidgetItem(str(college.avg_sat)))  # average sat
            self.table.setItem(row, 3, QTableWidgetItem(f"{college.acceptance_rate}%"))  # acceptance rate
            self.table.setItem(row, 0, QTableWidgetItem("loading…"))  # placeholder for logo

            # create worker for background logo fetching
            worker = LogoWorker(row, college.name, college.domain)
            worker.finished.connect(self.set_logo)  # connect worker's finished signal to set_logo slot
            self.threadpool.start(worker.run)  # start worker in thread pool

        # re-enable button and reset text after processing
        self.find_button.setEnabled(True)
        self.find_button.setText("find colleges")

    def set_logo(self, row, logo_bytes):
        item = QTableWidgetItem()
        if logo_bytes == b"no_internet":
            # special case: no internet connection
            item.setText("no internet")
        elif logo_bytes:
            # load the image from bytes data
            image = QImage.fromData(logo_bytes)
            if not image.isNull():
                # calculate scale factor to fit within 160x160 while maximizing size
                scale_factor = min(160 / image.width(), 160 / image.height())
                # scale the image
                pixmap = QPixmap.fromImage(image).scaled(
                    int(image.width() * scale_factor), 
                    int(image.height() * scale_factor), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                # set the pixmap as an icon in the table item
                item.setIcon(QIcon(pixmap))
            else:
                # image data is invalid
                item.setText("logo not found")
        else:
            # no logo data received
            item.setText("logo not found")
        # update the table cell with the item
        self.table.setItem(row, 0, item)

def main():
    app = QApplication(sys.argv)  # create the main qt application object, passing command line arguments
    window = CollegeFinder()      # create an instance of our CollegeFinder window
    window.show()                 # show the window on the screen
    sys.exit(app.exec())          # start the application's event loop and exit when the window is closed


if __name__ == "__main__":
    main()