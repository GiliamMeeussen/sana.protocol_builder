from django.db import transaction
from pyfcm import FCMNotification

from api.models import Device

def push_procedure_to_devices(owner, procedure_id):
    # api_key from https://console.firebase.google.com/project/sanamobile-1f7b1/settings/general/
    push_service = FCMNotification(api_key="AAAAJCZMnrI:APA91bFf-aYOjlH3LeQIi0W9vNZBJay5V9t7zuFiZMKGQNDddj7nSwbVTD2iTPE73AdI8zcKA-K88cJX4coGLYuJTHpb5gImAHg2Szu8bbTUdnoiTQg6mms0BN6WgZ-oa6N4avqhEUyj")

    # create a data message
    data_message = {
        "type": "newProcedure",
        "procedureId": procedure_id,
        "fetchUrl": "http://192.168.43.158:8000/api/procedures",
    }

    registration_ids = Device.objects.all().values_list('registration_id', flat=True)
    registration_ids = [i.encode('ascii','ignore') for i in registration_ids]

    result = push_service.notify_multiple_devices(registration_ids=registration_ids, data_message=data_message)




