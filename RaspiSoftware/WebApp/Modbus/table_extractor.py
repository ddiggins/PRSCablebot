import sys
# sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages') # in order to import cv2 under python3
# sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages') # append back in order to import rospy

import camelot
import pandas as pd

def table_extractor():

    # PDF file to extract tables from
    file = "Appendixes.pdf"

    # extract all the tables in the PDF file
    tables = camelot.read_pdf(file, pages='5', spreadsheet = True)

    # camelot.plot(tables, kind='grid')
    # plt.show()

    # number of tables extracted
    print("Total tables extracted:", tables.n)

    # print the first table as Pandas DataFrame
    # print(tables[0].df)

    # export individually
    # tables[0].to_csv("extracted_appendix.csv")

    # or export all in a zip
    # tables.export("all_tables.csv", f="csv", compress=True)

def csv_to_dictionary(csvFile):
    '''
    Takes a csv file and converts it into a dictionary with the following format:
    {1: {'Parameter Name': 'Temperature', 'Holding Register Number': 5451, 'Holding Register Address': 5450, 'Default Unit ID': 1, 'Default Unit Abbreviation': '°C'}, 
     2: {'Parameter Name': 'Pressure', 'Holding Register Number': 5458, 'Holding Register Address': 5457, 'Default Unit ID': 17, 'Default Unit Abbreviation': 'PSI'},
     ...
    }
    '''
    df = pd.read_csv(csvFile)
    df = df.set_index('ID')
    data_dict = df.to_dict('index')

    return data_dict

# print(csv_to_dictionary('AppendixB_paramNumsAndLocations.csv'))
# print("\n")
# print(csv_to_dictionary('AppendixC_unitIDs.csv'))


