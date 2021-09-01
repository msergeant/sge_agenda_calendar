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


def render_week(data, monday):
    quote = data['quotes'].get(monday)
    idea = data['ideas'].get(monday)
    concept = concept_of_quarter(monday, data)

    if concept:
        print(f"Concept of the quarter: {concept}")

    if quote:
        print(f'Quote of the week: "{quote.get("quote")}" '
              f'-- {quote.get("author")}')
    if idea:
        print(f'Idea of the week: {idea}')

    for i in range(5):
        date = (monday + datetime.timedelta(days=i))
        days = data['days'].get(date)

        if days:
            text = [i for i in days if i]
            print(f"{date.day} {'|'.join(text)}")
        else:
            print(f"{date.day}")


def generate_calendar():
    parser = argparse.ArgumentParser(
        description='Generate a pdf of agenda calendar days')
    parser.add_argument('--csv', dest='csv',
                        help='The source CSV file for generating the calendar')
    parser.add_argument('--first', dest='first', required=True,
                        help='The first day of the calendar (mm/dd/yyyy)')
    parser.add_argument('--last', dest='last', required=True,
                        help='The last day of the calendar (mm/dd/yyyy)')

    args = parser.parse_args()

    if args.csv:
        data = parse_csv_file(args.csv)
    else:
        print("You must include either a --csv or --xlsx argument")

    first_date = datetime.datetime.strptime(args.first, '%m/%d/%Y').date()
    last_date = datetime.datetime.strptime(args.last, '%m/%d/%Y').date()

    if last_date <= first_date:
        print("First date must be before last date")

    current_date = monday_of_week(first_date)
    while current_date <= last_date:
        render_week(data, current_date)
        current_date = (current_date + datetime.timedelta(days=7))


if __name__ == "__main__":
    generate_calendar()

