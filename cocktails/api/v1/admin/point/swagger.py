from api.v1.admin.point.serializers import AdminCreatePointUserSerializer

tags = ['admin']

points_create = {
    'operation_description': '## Создание начисление или списания баллов',
    'operation_summary': 'Создание начисление или списания баллов',
    'request_body': AdminCreatePointUserSerializer(many=False),
    'responses': {'201': AdminCreatePointUserSerializer(many=False)},
    'tags': tags,
}