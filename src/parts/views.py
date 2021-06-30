from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, NotAcceptable
from django.contrib.auth.decorators import permission_required
from rest_framework.decorators import permission_classes
from parts.serializers import PartSerializer
from .models import Part
from .forms import UploadCSVFileForm
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from utils.parts_import import handle_uploaded_csv_file, get_data_from_csv, take_files_form_csv_folder, file_remove
from celery import current_app
from parts.tasks import compare_data, import_parts

class SmallPagesPagination(PageNumberPagination):
    page_size = 40


class PartViewset(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PartSerializer
    # pagination_class = SmallPagesPagination

    def get_queryset(self):
        vin = self.request.query_params.get('vin', None)
        if vin is not None:
            parts = Part.objects.filter(vin=vin)
            if parts:
                return parts
            else:
                raise NotFound()
        else:
            raise NotAcceptable()
        # return parts


@permission_classes([IsAuthenticated])
@permission_required('admin.can_add_log_entry')
def upload_csv(request):
    # template = 'parts/progress.html'
    template = 'parts/upload_csv.html'
    parts = Part.objects.all()
    task_id = ''
    message = ''
    info = ''
    data = []
    context = {}

    if request.method == 'POST':
        form = UploadCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['csv_file'].name
            saved_file = handle_uploaded_csv_file(request.FILES['csv_file'])
            # data = get_data_from_csv(uploaded_filename)
            context = {'uploaded_file': uploaded_file, 'saved_file': saved_file, 'form': form, 'data': data}

        else:
            message = 'Not valid file!'
    else:
        filename_from_get = request.GET.get('file')
        action = request.GET.get('action')

        if action == 'cleardb':
            parts.delete()

        if filename_from_get and action == 'show':
            data = get_data_from_csv(filename_from_get)
            info = f'В файле {len(data)} строки'

        if filename_from_get and action == 'compare':
            data = compare_data(filename_from_get)
            info = f'В файле {len(data)} новых позиции'

        if filename_from_get and action == 'import':
            # result = import_parts.delay(filename_from_get)
            result = import_parts.delay(filename_from_get)
            task_id = result.task_id

        if filename_from_get and action == 'remove':
            message = file_remove(filename_from_get)

        form = UploadCSVFileForm()
        context = {'file': filename_from_get, 'form': form, 'message': message, 'data': data[:20], 'task_id': task_id, 'info': info}

    context['files_name'] = take_files_form_csv_folder()
    context['parts_count'] = len(parts)
    return render(request, template, context)


class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}
        if task.status == 'SUCCESS':
            response_data['results'] = task.get()
        return JsonResponse(response_data)
