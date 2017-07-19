from django.db import transaction
from pyfcm import FCMNotification

class ProcedurePusher:
	@staticmethod
	def push_procedure_to_devices(owner, procedure_id):
		# api_key from https://console.firebase.google.com/project/sanamobile-1f7b1/settings/general/
		push_service = FCMNotification(api_key="AAAAJCZMnrI:APA91bFf-aYOjlH3LeQIi0W9vNZBJay5V9t7zuFiZMKGQNDddj7nSwbVTD2iTPE73AdI8zcKA-K88cJX4coGLYuJTHpb5gImAHg2Szu8bbTUdnoiTQg6mms0BN6WgZ-oa6N4avqhEUyj")

		# create a data message
		data_message = {
			"type": "newProcedure",
			"procedureId": procedure_id,
			"fetchUrl": "placeholder lol",
		}

		registration_ids = ["f9wG7RTPY5k:APA91bEn1VI8LGoAGtHJVrQ5Ui-cMsHkTogVdFmTwiG-7p7PYwmAp9iiFwRDHVSJsv4zsEeoDu31HQEd9gUXuaVvs5Vt39LdMpfE4dOzxXXznk3ppkAc207TcIKTHmf5WmKhws7hFYks"]

		result = push_service.notify_multiple_devices(registration_ids=registration_ids, data_message=data_message)




