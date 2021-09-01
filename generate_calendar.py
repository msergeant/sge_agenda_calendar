import argparse
import csv
import datetime


def monday_of_week(date):
    weekday = date.weekday()
    if  weekday == 6:
        return date + datetime.timedelta(days=1)
    elif weekday % 7 != 0:
        return date - datetime.timedelta(days=weekday)

    return date


def concept_of_quarter(date, data):
    closest = datetime.date(datetime.MINYEAR, 12, 31)

    for concept_date in data['concepts']:
        if concept_date > closest and concept_date <= date:
            closest = concept_date

    return data['concepts'].get(closest)


def parse_csv_file(filename):
    quotes = {}
    concepts = {}
    ideas = {}
    days = {}

    with open(filename) as file:
        for row in csv.DictReader(file):
            date = datetime.datetime.strptime(row.get('Date'), '%m/%d/%Y')

            if row.get('Type') == 'quote':
                quotes[monday_of_week(date).date()] = {
                    'quote': row.get('Line1'),
                    'author': row.get('Line2')}
            elif row.get('Type') == 'idea':
                ideas[monday_of_week(date).date()] = row.get('Line1')
            elif row.get('Type') == 'concept':
                concepts[date.date()] = row.get('Line1')
            elif row.get('Type') == 'day':
                days[date.date()] = [row.get(f"Line{x}") for x in range(1, 9)]

    return {'quotes': quotes,
            'concepts': concepts,
            'ideas': ideas,
            'days': days}

def generate_calendar():
    parser = argparse.ArgumentParser(
        description='Generate a pdf of agenda calendar days')
    parser.add_argument('--csv', dest='csv',
                        help='The source CSV file for generating the calendar')

    args = parser.parse_args()

    data = parse_csv_file(args.csv)
    print(data)

if __name__ == "__main__":
    generate_calendar()

