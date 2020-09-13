#!/usr/bin/env python3

import json
import locale
import sys
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph,  Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from email.message import EmailMessage
import smtplib
import getpass
import os.path
import mimetypes
from operator import itemgetter

def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(
      car["car_make"], car["car_model"], car["car_year"])
def process_data(data):
  """Analyzes the data, looking for maximums.
  Returns a list of lines that summarize the information.
  """
  locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
  max_revenue = {"revenue": 0}
  max_sales = {"sales": 0}
  max_year = {"0": 0}
  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item

    # TODO: also handle max sales
    if item["total_sales"] > max_sales["sales"]:
      item["sales"] = item["total_sales"]
      max_sales = item


    # TODO: also handle most popular car_year
    # Create a sumary dictionary named max_year
    this_car_year=item["car"]["car_year"]
    max_year[this_car_year]=max_year.get(this_car_year, 0)+ item["total_sales"]

#looks for the max sales year
  max_year_val=""
  max_year_sal=0
  for key in max_year:
    if max_year[key]>max_year_sal:
      max_year_val=key
      max_year_sal=max_year[key]


  summary = [
    "The {} generated the most revenue: ${}".format(
      format_car(max_revenue["car"]), max_revenue["revenue"]),
    "The {} had the most sales: {}".format(
      format_car(max_sales["car"]), max_sales["sales"]),
    "The most popular year was {} with {} sales".format(
      max_year_val, max_year_sal),
     ]

  return summary


def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
  return table_data


def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("car_sales.json")
  summary = process_data(data)
  #print(summary)
  # TODO: turn this into a PDF report
  # Pdf file created
  #report = SimpleDocTemplate("cars.pdf")
  report = SimpleDocTemplate("/tmp/cars.pdf")
  styles = getSampleStyleSheet()
  #Title
  report_title = Paragraph("Sales summary for last month", styles["h1"])
  report_summary = Paragraph(summary[0]+"<br/>"+summary[1]+"<br/>"+summary[2]+"<br/> "+"<br/> ")
  #Table
  #Table formatting
  ordered_cars= cars_dict_to_table(data)
  #1.	Sort the list of cars in the PDF by total sales.
  ordered_cars[1:]=sorted(ordered_cars[1:],key=itemgetter(3))
  #report_table = Table(data=cars_dict_to_table(data))
  table_style = [('GRID', (0,0), (-1,-1), 1, colors.green)]
  report_table = Table(data=ordered_cars, style=table_style, hAlign="LEFT")
  #Build the PDF
  report.build([report_title, report_summary, report_table])
  # TODO: send the PDF report as an email attachment
  #attachment_path = "cars.pdf"
  attachment_path = "/tmp/cars.pdf"
  attachment_filename = os.path.basename(attachment_path)

  mime_type, _ = mimetypes.guess_type(attachment_path)
  message = EmailMessage()

  sender = "automation@example.com"
  receiver = "{}@example.com".format(os.environ.get('USER'))

  message['From'] = sender
  message['To'] = receiver

  message['Subject'] = 'Sales summary for last month'


  body = summary[0]+"\n"+summary[1]+"\n"+summary[2]+"\n "
  message.set_content(body)

  # Process the attachment and add it to the email
  attachment_filename = os.path.basename(attachment_path)
  mime_type, _ = mimetypes.guess_type(attachment_path)
  mime_type, mime_subtype = mime_type.split('/', 1)

  with open(attachment_path, 'rb') as ap:
    message.add_attachment(ap.read(),
                          maintype=mime_type,
                          subtype=mime_subtype,
                          filename=attachment_filename)


  """Sends the message to the configured SMTP server."""
  mail_server = smtplib.SMTP('localhost')
  mail_server.send_message(message)
  mail_server.quit()


if __name__ == "__main__":
  main(sys.argv)