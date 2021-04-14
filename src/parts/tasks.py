from celery import shared_task

from parts.models import Part
from utils.parts_import import get_data_from_csv

# from celery.exceptions import SoftTimeLimitExceeded
# from celery_progress.backend import ProgressRecorder
# from time import sleep

@shared_task(bind=True, soft_time_limit=100, time_limit=120)
def import_parts(self, filename):
    '''
    Create part instances from local csv file with bulk_create
    '''
    parts = []
    dif = []
    existing_parts = set(Part.objects.values_list('vin', 'code', 'name'))
    data = get_data_from_csv(filename)
    dif = set(data) - existing_parts
    for row in dif:
        part = Part(
            vin=row[0],
            code=row[1],
            name=row[2]
        )
        parts.append(part)
    try:
        Part.objects.bulk_create(parts)
    except Exception as e:
        return f"Error! {e}"
    return len(parts)

@shared_task(bind=True, soft_time_limit=100, time_limit=120)
def compare_data(self, filename):
    dif = []
    existing_parts = set(Part.objects.values_list('vin', 'code', 'name'))
    data = get_data_from_csv(filename)
    dif = set(data) - existing_parts
    return list(dif)

# @shared_task(bind=True, soft_time_limit=100, time_limit=120)
# def go_to_sleep(self, duration):
#     progress_recorder = ProgressRecorder(self)
#     try:
#         for i in range(100):
#             sleep(duration)
#             progress_recorder.set_progress(i+1, 100, f'Шаг {i+1} из 100')
#         return i
#     except SoftTimeLimitExceeded:
#         return "Bzzzzz!"
