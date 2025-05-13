from rest_framework import serializers


class PaginatorSerializer(serializers.Serializer):
    objects_count = serializers.IntegerField(source='count')
    pages_count = serializers.IntegerField(source='num_page')

    
class ListSerializer(serializers.Serializer):
    paginator = PaginatorSerializer()


class ListParamsSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1, required=False)


class FilterByDateSerializer(serializers.Serializer):
    fb_dc_start_from = serializers.DateTimeField(required=False)
    fb_dc_end_to = serializers.DateTimeField(required=False)