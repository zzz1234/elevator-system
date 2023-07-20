import datetime


def get_now(format='%Y-%m-%d %H:%M:%S'):
    """Returns the current datetime in desired format"""
    return datetime.datetime.now().strftime(format)


def delete_all_objects(model):
    model.objects.all().delete()


def fetch_all_objects(model, serializer):
    data = model.objects.all()
    serialized_data = serializer(data, many=True)
    return serialized_data.data
