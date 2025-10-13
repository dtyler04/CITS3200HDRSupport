from datetime import datetime, timedelta
import pytz

def calendar_range(date):
    awst = pytz.timezone('Australia/Perth')
    # Get first of the month
    first = awst.localize(date.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    # Calculate next month for days in current month
    month = first.month
    year = first.year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    next_first = first.replace(month=next_month, year=next_year)
    last = next_first - timedelta(days=1)
    num_days = last.day
    days = [first + timedelta(days=i) for i in range(num_days)]
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    return weeks

app.jinja_env.globals['calendar_range'] = calendar_range