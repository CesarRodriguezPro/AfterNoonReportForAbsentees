import pandas as pd
import os
import datetime
from Email_send import email_send

'''
this programs is intended to be run in the afternoon and compare the list of employees.
we use this program to find out who didn't clock in after lunch.
to do this we download 2 sets of data.

    1 - the employees activity to determent time they start working.  code = 34
    2 - current employee status to the determent.                     code = 37

after that we compare the names and prepare a report to be send to the foreman's email.
'''

#########################################################################################
#  API information, TIMESTATION.COM
key_api = os.environ.get('TimeStation_key')
dir_path = os.path.abspath(os.path.dirname(__file__))
limit_time_morning = '10:30'
white_list = ['RCS', 'Yard', 'Office']  # department that will be ignore by the programs.
#########################################################################################


class ReportEmployeesMissingAfterLunch:

    def __init__(self):

        self.current_date = datetime.date.today().strftime('%Y-%m-%d')

        self.url_morning = f"https://api.mytimestation.com/v0.1/reports/?api_key={key_api}&id=34&Report_StartDate={self.current_date}&Report_EndDate={self.current_date}&exportformat=csv"
        self.url_current = f"https://api.mytimestation.com/v0.1/reports/?api_key={key_api}&id=37&exportformat=csv"

        self.raw_data = pd.read_csv(self.url_morning)
        self.for_morning = self.raw_data[self.raw_data['Activity'].str.contains('Punch In')]

        self.current_data = pd.read_csv(self.url_current)
        self.current = self.current_data[self.current_data['Status'].str.contains('In')]

    def get_morning_list(self):
        filtered_list = self.for_morning[~self.for_morning['Department'].isin(white_list)]
        return filtered_list[filtered_list['Time'] < limit_time_morning][['Name', 'Department']]

    def get_after_lunch(self):
        filtered_list = self.current[~self.current['Current Department'].isin(white_list)]
        return filtered_list[['Name', 'Current Department']]

    def compare_list(self):

        morning_list = self.get_morning_list()
        afternoon_list = self.get_after_lunch()
        missing_afternoon = morning_list[~morning_list['Name'].isin(afternoon_list['Name'])].sort_values(by=['Department','Name'])
        missing_morning = afternoon_list[~afternoon_list['Name'].isin(morning_list['Name'])].sort_values(by=['Current Department','Name'])
        return missing_morning, missing_afternoon

    def display_report(self):

        missing_morning_raw, missing_afternoon_raw = self.compare_list()
        missing_morning = missing_morning_raw.to_dict('index')
        missing_afternoon = missing_afternoon_raw.to_dict('index')

        print('\n\n')
        print('[+] - Employees Missing after Lunch')
        print('-'*75)
        for number, data in enumerate(missing_afternoon.values(), 1):
            print(f"{number:5}|{data['Name']:^25}|{data['Department']}")

        print('\n\n')
        print('-'*75)
        print('[+] - Employees didn\'t work in the morning')
        for number, x in enumerate(missing_morning.values(), 1):
            print(f"{number:5}|{x['Name']:^25}|{x['Current Department']}")
        
        print('\n\n')
        print('-'*75)
        answer = input('if you would like to send the report \n')
        if answer.lower()[0] == 'y':
            self.send_report()

    def send_report(self):

        missing_morning_raw, missing_afternoon_raw = self.compare_list()
        missing_morning = missing_morning_raw.to_dict('index')
        missing_afternoon = missing_afternoon_raw.to_dict('index')

        with open('message.txt', "w") as text_save:

            text_save.write('IBK Team, \n\n')

            if not missing_afternoon_raw.empty:
                text_save.write('The following employees did not clock in back from lunch \n \n')
                for number, item in enumerate(missing_afternoon.values(), 1):
                    text_save.writelines('{:5}. {:30} {} \n'.format(number, item['Name'], item['Department']))

            text_save.write('\n')

            if not missing_morning_raw.empty:
                text_save.write('The following employees started working After Lunch (Not Morning).\n\n')
                for number, items in enumerate(missing_morning.values(), 1):
                    text_save.writelines('{:5}. {:30} {}\n'.format(number, items['Name'], items['Current Department']))

            text_save.write("\nCesar Rodriguez \nIT Administrator - Automatic System  \nIBK Construction group")
        email_send()

    def __safe_sheet_for_testing(self):
        ''' to save data in from timestation for testing purposes, please ignore.'''
        self.for_morning.to_csv('Morning.csv')
        self.current.to_csv('current.csv')


if __name__ == '__main__':

    active = ReportEmployeesMissingAfterLunch()
    active.display_report()
