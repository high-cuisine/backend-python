from api.v1.admin.statistics.serializers import AdminStatisticsSerializer

tags = ['admin']

statistics = {
    'operation_description': '## Статистика',
    'operation_summary': 'Статистика',
    'responses': {'200': AdminStatisticsSerializer(many=False)},
    'tags': tags,
}
