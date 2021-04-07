from time import sleep

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery_progress.backend import ProgressRecorder

from parts.models import Part
from utils.parts_import import get_data_from_csv


@shared_task(bind=True, soft_time_limit=100, time_limit=120)
def go_to_sleep(self, duration):
    progress_recorder = ProgressRecorder(self)
    try:
        for i in range(100):
            sleep(duration)
            progress_recorder.set_progress(i+1, 100, f'Шаг {i+1} из 100')
        return i
    except SoftTimeLimitExceeded:
        return "Bzzzzz!"

@shared_task(bind=True, soft_time_limit=100, time_limit=120)
def import_parts(self, filename):
    '''
    Create part instances from local csv file
    '''
    progress_recorder = ProgressRecorder(self)
    count = 0
    try:
        data = get_data_from_csv(filename)
        for row in data:
            if row[0] and row[1] and row[2]:
                count += 1
                _, created = Part.objects.get_or_create(
                    vin=row[0],
                    code=row[1],
                    name=row[2],
                    # unit = row[3],
                    # count = row[4],
                )
                progress_recorder.set_progress(count, len(data), f'Запчасть {row[0]} сохранена: {count} из {len(data)}')
        return count
    except SoftTimeLimitExceeded:
        return "Bzzzzz!"
