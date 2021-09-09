import argparse
import csv
import datetime
from io import BytesIO

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import inch, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

FRAME_WIDTH = 570.
TOP_MARGIN = 0.35 * inch

HeaderStyle = ParagraphStyle(
    name="header",
    font="Calibri-Bold",
    fontSize=22,
)

DayHeaderStyle = ParagraphStyle(
    name="dayHeader",
    font="Calibri-Bold",
    fontSize=16,
)

EventStyle = ParagraphStyle(
    name="dayHeader",
    font="Calibri",
    fontSize=12,
)


def monday_of_week(date):
    weekday = date.weekday()
    if weekday == 6:
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
                    'quote': row.get('Event1'),
                    'author': row.get('Event2')}
            elif row.get('Type') == 'idea':
                ideas[monday_of_week(date).date()] = row.get('Event1')
            elif row.get('Type') == 'concept':
                concepts[date.date()] = row.get('Event1')
            elif row.get('Type') == 'day':
                days[date.date()] = [row.get(f"Event{x}") for x in range(1, 6)]

    return {'quotes': quotes,
            'concepts': concepts,
            'ideas': ideas,
            'days': days}


def _single_day(data, date):
    table_data = [[Paragraph(date.strftime('%A, %B %d, %Y'),
                             DayHeaderStyle)]]
    events = data['days'].get(date, [])

    for event in events:
        if event:
            table_data.append([Paragraph(event, EventStyle)])

    return Table(table_data,
                 rowHeights=([0.4*inch] +
                             [0.3 * inch for x in range(len(table_data) - 1)]),
                 style=[('VALIGN', (0, 0), (0, 0), "TOP")])


def _merge_elements(elements, existing_page):
    buff = BytesIO()
    side_margin = (letter[0] - FRAME_WIDTH) / 2.
    doc = SimpleDocTemplate(buff, pagesize=letter)
    doc.leftMargin = side_margin + 0.23 * inch
    doc.rightMargin = side_margin
    doc.bottomMargin = 0.
    doc.topMargin = TOP_MARGIN

    doc.build(elements)
    new_pages = PdfFileReader(buff).pages
    for new_page in new_pages:
        new_page.mergePage(existing_page)
    return new_pages


def render_left_page(data, monday, left_page):
    tuesday = monday + datetime.timedelta(days=1)
    wednesday = monday + datetime.timedelta(days=2)
    friday = monday + datetime.timedelta(days=4)

    elements = [Paragraph(f"{monday.strftime('%B %d').upper()} - "
                          f"{friday.strftime('%B %d').upper()}", HeaderStyle),
                Spacer(width=60, height=0.4*inch),
                Table([[_single_day(data, monday)],
                       [_single_day(data, tuesday)],
                       [_single_day(data, wednesday)]],
                      rowHeights=3.18*inch,
                      style=[
                          ("VALIGN", (0, 0), (-1, -1), "TOP")])]

    return _merge_elements(elements, left_page)


def render_right_page(data, monday, right_page):
    thursday = monday + datetime.timedelta(days=3)
    friday = monday + datetime.timedelta(days=4)

    elements = [Spacer(width=60, height=0.6*inch),
                Table([[_single_day(data, thursday)],
                       [_single_day(data, friday)]],
                      rowHeights=3.18*inch,
                      style=[
                          ("VALIGN", (0, 0), (-1, -1), "TOP")])]

    return _merge_elements(elements, right_page)


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
    pages = []
    left_page = PdfFileReader("left_page.pdf").pages[0]
    right_page = PdfFileReader("right_page.pdf").pages[0]
    while current_date <= last_date:
        pages.extend(render_left_page(data, current_date, left_page))
        pages.extend(render_right_page(data, current_date, right_page))
        current_date = (current_date + datetime.timedelta(days=7))

    buff = BytesIO()
    output = PdfFileWriter()
    for page in pages:
        page.compressContentStreams()
        output.addPage(page)

    output.write(buff)

    filename = "agenda_out.pdf"
    print(f"Completed: {filename}")
    with open(filename, "wb") as f:
        f.write(buff.getbuffer())


if __name__ == "__main__":
    generate_calendar()
