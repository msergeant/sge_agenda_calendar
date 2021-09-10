import argparse
import datetime
import os
import textwrap
from io import BytesIO

from openpyxl import load_workbook
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import inch, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table


def register_font(fnt):
    pdfmetrics.registerFont(TTFont(fnt, os.path.join("fonts/", fnt + '.ttf')))


FRAME_WIDTH = 570.
TOP_MARGIN = 0.35 * inch

HeaderStyle = ParagraphStyle(
    name="header",
    fontName="Carlito-Bold",
    fontSize=22,
    leftIndent=11,
)

DayHeaderStyle = ParagraphStyle(
    name="dayHeader",
    fontName="Carlito-Bold",
    fontSize=16,
)

EventStyle = ParagraphStyle(
    name="event",
    fontName="Carlito-Regular",
    fontSize=12,
)

QuoteStyle = ParagraphStyle(
    name="quote",
    fontName="Carlito-BoldItalic",
    fontSize=16,
    leading=17,
    alignment=TA_CENTER,
)

IdeaStyle = ParagraphStyle(
    name="idea",
    fontName="Carlito-Bold",
    fontSize=13,
    leading=14,
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


def parse_excel_file(filename):
    quotes = []
    ideas = []
    days = {}

    wb = load_workbook(filename=filename)
    events = wb['Events']
    for row in events.rows:
        if row[0].value and row[0].value != 'Date' and row[1].value:
            date = row[0].value
            days[date.date()] = [row[x].value for x in range(1, 6)
                                 if row[x].value]

    quote_sheet = wb['Quotes & Do Different Ideas']
    for i, row in enumerate(quote_sheet.rows):
        if row[0].value and i > 0:
            quotes.append(row[0].value)

        if row[2].value and i > 0:
            ideas.append(row[2].value)

    return {'quotes': quotes,
            'ideas': ideas,
            'days': days}


def _single_day(data, date):
    table_data = [[Paragraph(date.strftime('%A, %B %-d, %Y'),
                             DayHeaderStyle)]]
    events = data['days'].get(date, [])

    for event in events:
        if event:
            table_data.append([Paragraph(event, EventStyle)])

    return Table(table_data,
                 rowHeights=([0.3*inch] +
                             [0.3 * inch for x in range(len(table_data) - 1)]),
                 style=[('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('VALIGN', (0, 0), (0, 0), "TOP")])


def _merge_elements(elements, existing_page):
    buff = BytesIO()
    side_margin = (letter[0] - FRAME_WIDTH) / 2.
    doc = SimpleDocTemplate(buff, pagesize=letter)
    doc.leftMargin = side_margin
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

    elements = [Paragraph(f"{monday.strftime('%B %-d').upper()} - "
                          f"{friday.strftime('%B %-d').upper()}", HeaderStyle),
                Spacer(width=60, height=0.4*inch),
                Table([[_single_day(data, monday)],
                       [_single_day(data, tuesday)],
                       [_single_day(data, wednesday)]],
                      rowHeights=3.18*inch,
                      style=[
                          ("VALIGN", (0, 0), (-1, -1), "TOP")])]

    return _merge_elements(elements, left_page)


def render_right_page(data, monday, right_page, week_num):
    quote = data['quotes'][week_num % len(data['quotes'])]
    wrapped = textwrap.wrap(quote)
    if len(wrapped) > 1 and ' ' in wrapped[-1]:
        quote = '<br/>'.join(wrapped)

    idea = data['ideas'][week_num % len(data['ideas'])]
    thursday = monday + datetime.timedelta(days=3)
    friday = monday + datetime.timedelta(days=4)

    elements = [Table([[Paragraph(quote, QuoteStyle)]],
                      rowHeights=0.6*inch,
                      style=[("TOPPADDING", (0, 0), (-1, -1), 0),
                             ("VALIGN", (0, 0), (-1, -1), "TOP")]),
                Table([[_single_day(data, thursday)],
                       [_single_day(data, friday)]],
                      rowHeights=3.18*inch,
                      style=[
                          ("VALIGN", (0, 0), (-1, -1), "TOP")]),
                Spacer(width=60, height=0.1 * inch),
                Table([['', Paragraph(idea, IdeaStyle)]],
                      rowHeights=0.8*inch,
                      colWidths=[0.9*inch, 6*inch],
                      style=[("TOPPADDING", (0, 0), (-1, -1), 10),
                             ("VALIGN", (0, 0), (-1, -1), "TOP")])]

    return _merge_elements(elements, right_page)


def generate_calendar():
    parser = argparse.ArgumentParser(
        description='Generate a pdf of agenda calendar days')

    parser.add_argument('--first', dest='first', required=True,
                        help='The first day of the calendar (mm/dd/yyyy)')
    parser.add_argument('--last', dest='last', required=True,
                        help='The last day of the calendar (mm/dd/yyyy)')
    parser.add_argument('--source', dest='source', required=True,
                        help='The source file for generating the calendar')

    args = parser.parse_args()

    if 'xlsx' not in args.source:
        print("source file must be xlsx file type")
        return

    first_date = datetime.datetime.strptime(args.first, '%m/%d/%Y').date()
    last_date = datetime.datetime.strptime(args.last, '%m/%d/%Y').date()

    if last_date <= first_date:
        print("First date must be before last date")
        return

    data = parse_excel_file(args.source)

    register_font("Carlito-Regular")
    register_font("Carlito-Bold")
    register_font("Carlito-BoldItalic")

    current_date = monday_of_week(first_date)
    pages = []
    week_num = 0
    left_page = PdfFileReader("left_page.pdf").pages[0]
    right_page = PdfFileReader("right_page.pdf").pages[0]
    while current_date <= last_date:
        pages.extend(render_left_page(data, current_date, left_page))
        pages.extend(render_right_page(data,
                                       current_date,
                                       right_page,
                                       week_num))
        current_date = (current_date + datetime.timedelta(days=7))
        week_num += 1

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
