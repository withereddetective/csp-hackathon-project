import csv  # for reading the csv file


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

def filter_colleges(list_of_colleges: list, user_sat_score: int, SAT_RANGE_BUFFER: int) -> list:  # originally in get_reccommended_colleges() but this makes it easier to read
    # filtering colleges by the range the user provides
    min_sat = user_sat_score - SAT_RANGE_BUFFER
    max_sat = user_sat_score + SAT_RANGE_BUFFER
    filtered_colleges = [
        college for college in list_of_colleges 
        if min_sat <= college.avg_sat <= max_sat
    ]

    # if no colleges are found in that tight range, expand the search slightly
    while not filtered_colleges:
        print(f"no colleges found within {SAT_RANGE_BUFFER} points. Expanding search range...")
        SAT_RANGE_BUFFER += 100
        min_sat -= 100
        max_sat += 100
        filtered_colleges = [
            college for college in list_of_colleges 
            if min_sat <= college.avg_sat <= max_sat
        ]
    return filtered_colleges

def get_reccommended_colleges(list_of_colleges: list, user_sat_score: int, SAT_RANGE_BUFFER: int) -> list:
    list_of_colleges = filter_colleges(list_of_colleges, user_sat_score, SAT_RANGE_BUFFER)

    # sort the filtered list using a custom key function
    # the key prioritizes:
    # a) proximity to the users sat score (closer is better, abs(diff) is smaller)
    # b) acceptance Rate (higher acceptance rate is usually safer, so we sort in descending order for secondary sort)
    def sorting_key(college):
        sat_difference = abs(college.avg_sat - user_sat_score)
        # using a tuple for sorting: (primary_key, secondary_key)
        # python sorts tuples element by element.
        # we negate acceptance_rate to sort it in descending order (higher rate first).
        return (sat_difference, -college.acceptance_rate)
    
    # sort the list using the custom key
    list_of_colleges.sort(key=sorting_key)

    # return the top 10 results
    return list_of_colleges[:10]

def print_colleges(list_of_colleges: list):  # the list should only be the top 10
    for college in list_of_colleges:
        print(f"{list_of_colleges.index(college) + 1}. {college.name}, {college.avg_sat}, {college.acceptance_rate}")

def get_int_input(message: str) -> int:  # uses recursion in a try-except block to negate bad users
    try:
        return int(input(message))
    except Exception:
        print("give an integer ONLY")
        return get_int_input(message)

def main():
    print("welcome to the college finder.\ninput your sat score and i will reccomend you colleges.")
    user_sat_score = get_int_input("what is your sat score?: ")
    SAT_RANGE_BUFFER = get_int_input("what is your sat range buffer?: ")
    print_colleges(get_reccommended_colleges(get_data(), user_sat_score, SAT_RANGE_BUFFER))


if __name__ == "__main__":
    main()