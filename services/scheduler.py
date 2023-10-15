from datetime import datetime
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from itertools import cycle
import math


def _dt_to_float(_date: datetime) -> float:
    return (_date.day - 1) * 24 + _date.hour + _date.minute / 60.0


def get_plan(workers: list,
             start: str, end: str, shift: str,
             start_date: str, end_date: str,
             max_hours_per_month: int):
    start_wd = datetime.strptime(start, '%H:%M')
    end_wd = datetime.strptime(end, '%H:%M')
    shift_duration = datetime.strptime(shift, '%H:%M')

    if end_wd <= start_wd:
        end_wd += relativedelta(days=+1)

    shift_starts_num = math.ceil((_dt_to_float(end_wd) - _dt_to_float(start_wd)) / _dt_to_float(shift_duration))

    shift_starts_arr = []
    for i in range(shift_starts_num):
        shift_start = _dt_to_float(start_wd) + i * math.ceil(
            ((_dt_to_float(end_wd) - _dt_to_float(start_wd)) / shift_starts_num) * 2) / 2
        shift_end = shift_start + _dt_to_float(shift_duration)
        if shift_end > _dt_to_float(end_wd):
            shift_start = _dt_to_float(end_wd) - _dt_to_float(shift_duration)
            shift_end = _dt_to_float(end_wd)
        shift_starts_arr.append(
            f"{int(shift_start):02d}:{int(shift_start % 1 * 60):02d} - {int(shift_end):02d}:{int(shift_end % 1 * 60):02d}")

    cycled_db = cycle(workers)
    cycled_shift_starts = cycle(shift_starts_arr)

    workers_plan = {}

    for dt in rrule.rrule(rrule.DAILY,
                          dtstart=datetime.strptime(start_date, '%Y/%m/%d') + relativedelta(days=-1),
                          until=datetime.strptime(end_date, '%Y/%m/%d')):
        workers_plan.setdefault(dt.strftime('%Y/%m'), {}).update({dt.day: []})
        days_in_month = monthrange(dt.year, dt.month)[1]
        workers_per_day_num = int(max_hours_per_month / _dt_to_float(shift_duration) / days_in_month * len(workers))
        for _ in range(workers_per_day_num):
            workers_plan[dt.strftime('%Y/%m')].setdefault(dt.day, []).append(next(cycled_db))
        for _ in range(len(workers) - workers_per_day_num + 1):
            next(cycled_db)

    for dt in rrule.rrule(rrule.DAILY,
                          dtstart=datetime.strptime(start_date, '%Y/%m/%d') + relativedelta(days=-1),
                          until=datetime.strptime(end_date, '%Y/%m/%d'),
                          byweekday=rrule.SU):
        next_day = dt + relativedelta(days=+1)
        if next_day.strftime('%Y/%m') in workers_plan and next_day.day in workers_plan[next_day.strftime('%Y/%m')]:
            sunday_workers = set()
            for worker in workers_plan[dt.strftime('%Y/%m')][dt.day]:
                sunday_workers.add(worker['id'])
            monday_workers = set()
            for worker in workers_plan[next_day.strftime('%Y/%m')][next_day.day]:
                monday_workers.add(worker['id'])
            worker_id = (sunday_workers - monday_workers).pop()
            for worker in workers_plan[dt.strftime('%Y/%m')][dt.day]:
                if worker['id'] == worker_id:
                    workers_plan[dt.strftime('%Y/%m')][dt.day].remove(worker)
                    workers_plan[next_day.strftime('%Y/%m')][next_day.day].append(worker)
        else:
            workers_plan[dt.strftime('%Y/%m')][dt.day].pop()

    dt_start = datetime.strptime(start_date, '%Y/%m/%d') + relativedelta(days=-1)
    del workers_plan[dt_start.strftime('%Y/%m')][dt_start.day]
    if not workers_plan[dt_start.strftime('%Y/%m')]:
        del workers_plan[dt_start.strftime('%Y/%m')]

    plan = {}
    for date, value in workers_plan.items():
        plan.setdefault(date, {})
        for day, workers in value.items():
            for _ in range(len(shift_starts_arr)):
                plan[date].setdefault(day, {}).update({next(cycled_shift_starts): []})
            for worker in workers:
                plan[date][day][next(cycled_shift_starts)].append(worker)

    for date, value in plan.items():
        for day, worker in value.items():
            plan[date][day] = dict(sorted(plan[date][day].items()))

    return plan
