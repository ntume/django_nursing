from datetime import datetime, timedelta

def sunday_year_weeks(year):
    """Yield week number and start/end dates for a given year starting on Sunday."""
    # Find the first Sunday on or before January 1st
    jan_1 = datetime(year, 1, 1)
    start_date = jan_1 - timedelta(days=jan_1.weekday() + 1) if jan_1.weekday() != 6 else jan_1

    week_num = 1
    while True:
        end_date = start_date + timedelta(days=6)

        # Yield only if the week includes at least one day in the target year
        if end_date.year < year:
            start_date = end_date + timedelta(days=1)
            continue

        if start_date.year > year:
            break

        yield week_num, start_date.date(), end_date.date()
        week_num += 1
        start_date = end_date + timedelta(days=1)
     
def number_of_days(start, end):
    #check which date is greater to avoid days output in -ve number
    
    if end > start:
        all_days = (start + timedelta(x + 1) for x in range((end - start).days))
    else:
        all_days = (end + timedelta(x + 1) for x in range((start - end).days))

    # filter business days
    # weekday from 0 to 4. 0 is monday adn 4 is friday
    # increase counter in each iteration if it is a weekday
    count = sum(1 for day in all_days if day.weekday() < 5)
    
    return count