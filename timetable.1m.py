#!/usr/bin/python3

# xbar meta
# <xbar.title>Timetable</xbar.title>
# <xbar.version>v1.1</xbar.version>
# <xbar.author>Cabin Zhu</xbar.author>
# <xbar.author.github>cabinz</xbar.author.github>
# <xbar.desc>Display the current event from a given daily timetable. To make it work, make sure to configure the path to your CSV timetable file. More about the user manual, see project page https://github.com/cabinz/xbar-timetable.</xbar.desc>
# <xbar.image>https://raw.githubusercontent.com/cabinz/xbar-timetable/main/docs/timetable.png</xbar.image>
# <xbar.abouturl>https://github.com/cabinz/xbar-timetable</xbar.abouturl>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.var>string(VAR_TIMETABLE_FILE="/path/to/your/timetable.csv"): An absolute path to a CSV file of the timetable to be displayed.</xbar.var>

import datetime
import csv
import os
from typing import List


CSV_TIMETAB = os.environ.get("VAR_TIMETABLE_FILE")


def to_m_time(time: str):
    """Convert HH:MM time to minutes since 00:00."""
    hour, minute = map(int, time.split(':'))
    return hour * 60 + minute


def to_timestamp(m_time: int):
    assert 0 <= m_time <= to_m_time("24:00") 
    hr, minute = m_time // 60, m_time % 60
    return f"{hr:02d}:{minute:02d}"


class Event:
    def __init__(self, start_timestamp: str, end_timestamp: str, name: str) -> None:
        self.start_time = start_timestamp
        self.end_time = end_timestamp
        self.m_start_time = to_m_time(start_timestamp)
        self.m_end_time = to_m_time(end_timestamp)
        self.name = name
    
    def __repr__(self) -> str:
        return self.name
    
    def spans_midnight(self) -> bool:
        return self.m_start_time > self.m_end_time
    
    def minutes_left(self, m_time: int) -> int:
        if self.spans_midnight():
            if m_time >= self.m_start_time:
                return to_m_time("24:00") - m_time + self.m_end_time
            else:
                return self.m_end_time - m_time
        else:
            return self.m_end_time - m_time
        
    def is_ongoing(self, m_time: int) -> bool:
        if self.spans_midnight():
            if m_time >= self.m_start_time or m_time < self.m_end_time:
                return True
        elif self.m_start_time <= m_time < self.m_end_time:
            return True
        return False
        
    def time_left(self, m_time: int) -> str:
        m_left = self.minutes_left(m_time)
        hr_left = m_left / 60
        if hr_left >= 1:
            return f"{hr_left:.1f}h"
        else:
            return f"{m_left}m"


def load_timetable(csv_file) -> List[Event]:
    if csv_file is None or not os.path.exists(csv_file):
        raise ValueError(
            f'The current timetable file path "{csv_file}" is invalid. Please re-configure the path to your CSV file in xbar. If you are a user from SwiftBar or other plug-in software that does not support user-configurable variables, you could modify the script to hard-code the path yourself as the CSV_TIMETAB variable.')
    
    tab = []
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        for idx, (start_time, end_time, event_name) in enumerate(reader):
            tab.append(Event(start_time, end_time, event_name))
    return tab


def locate_event(cur_m_time: int, timetable: List[Event]) -> int:
    """Locate the current event.
    
    Returns:
        int: The index of current event. Return -1 if it's not found.
    """
    for idx, event in enumerate(table):
        if event.is_ongoing(cur_m_time):
            return idx
    return -1


if __name__ == "__main__":
    table = load_timetable(CSV_TIMETAB)
    cur_time = datetime.datetime.now().strftime("%H:%M")
    cur_m_time = to_m_time(cur_time)
    
    idx_found = locate_event(cur_m_time, table)
    if idx_found != -1: # display the first-hit ongoing event as title
        event = table[idx_found]
        print(f'{event} ({event.time_left(cur_m_time)} left)')
        # print(f'{event} | dropdown=False')
        # print(f'{event.time_left(cur_m_time)} left')
    else:
        print("no event")
    
    print("---")
    RGB_LIGHT_GREY = "#848481" 
    for cur_idx, event in enumerate(table):
        is_ongoing = event.is_ongoing(cur_m_time) # allows multiple ongoing events
        print("{}-{} {}{} | font=Monaco size=15 color={}".format(
            event.start_time, event.end_time, event.name,
            " ⬅" if is_ongoing else "",
            "orange" if is_ongoing else RGB_LIGHT_GREY
        ))
