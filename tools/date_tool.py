from datetime import datetime


def get_current_datetime():

    now = datetime.now()

    return now.strftime("%d-%m-%Y %H:%M:%S")