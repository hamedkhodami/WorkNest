from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status


class ViewMixin:
    serializer = None
    serializer_response = None

    def get_serializer(self):
        return self.serializer

    def get_serializer_response(self):
        if self.serializer_response:
            return self.serializer_response
        return self.serializer


class CreateViewMixin(ViewMixin):
    validated_data = None
    obj = None

    def create(self, request, response=True, *args, **kwargs):
        data = request.data.copy()
        # add request to serializer data
        self.data = data
        data['request'] = request
        additional_data = self.additional_data()
        if additional_data:
            data.update(additional_data)
        serializer = self.get_serializer()(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        self.before_save()
        self.obj = serializer.save()
        self.do_success()
        ser_resp = self.get_serializer_response()(self.obj, context={'request': request})
        if response:
            return Response(ser_resp.data, status=status.HTTP_201_CREATED)
        return ser_resp.data

    def additional_data(self):
        pass

    def before_save(self):
        pass

    def do_success(self):
        pass

    def get_serializer(self):
        return self.serializer

    def get_serializer_response(self):
        return self.serializer_response


class UpdateViewMixin(ViewMixin):
    validated_data = None
    obj = None

    def update(self, request, response=True, *args, **kwargs):
        data = request.data.copy()
        # add request to serializer data
        self.data = data
        data['request'] = request
        instance = self.get_instance()
        additional_data = self.additional_data()
        if additional_data:
            data.update(additional_data)
        serializer = self.get_serializer()(data=data, instance=instance)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        self.obj = serializer.save()
        self.do_success()
        ser_resp = self.get_serializer_response()(self.obj)
        if response:
            return Response(ser_resp.data, status=status.HTTP_200_OK)
        return ser_resp.data

    def get_instance(self):
        return None

    def additional_data(self):
        return None

    def do_success(self):
        pass


class ListViewMixin(ViewMixin):
    page_size = 20
    query_params = None

    def list(self, request, response=True, *args, **kwargs):
        serializer = self.get_serializer()
        if serializer:
            serializer = serializer(data=self.get_data_params())
            serializer.is_valid(raise_exception=True)
            self.query_params = serializer.validated_data
        else:
            self.query_params = request.data
        query_set = self.get_queryset() or []
        paginator = Paginator(query_set, self.page_size)
        page = self.get_page(paginator)
        serializer_resp_data = {
            'paginator': paginator,
            'data': page.object_list
        }
        ser_resp = self.get_serializer_response()(serializer_resp_data)
        if response:
            return Response(ser_resp.data, status=status.HTTP_200_OK)
        return ser_resp.data

    def get_page(self, paginator):
        return paginator.get_page(self.query_params.get('page', 1))

    def get_queryset(self):
        return None

    def get_data_params(self):
        return self.request.GET


class DeleteViewMixin(ViewMixin):
    validated_data = None

    def delete_instance(self, request, response=True, *args, **kwargs):
        instance = self.get_instance()
        ser_resp_data = self.get_serializer_response()(instance).data
        # delete obj
        instance.delete()
        if response:
            return Response(ser_resp_data, status=status.HTTP_200_OK)
        return ser_resp_data

    def get_instance(self):
        pass


class DetailViewMixin(ViewMixin):
    validated_data = None

    def detail(self, request, response=True, *args, **kwargs):
        serializer = self.get_serializer()
        if serializer:
            serializer = serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.validated_data = serializer.validated_data
        instance = self.get_instance()
        ser_resp_data = self.get_serializer_response()(instance).data
        if response:
            return Response(ser_resp_data, status=status.HTTP_200_OK)
        return ser_resp_data

    def get_instance(self):
        pass


class CreateOrUpdateViewMixin(CreateViewMixin, UpdateViewMixin):
    pass


class FilterByDateViewMixin:
    query_params = None

    def filter(self, qs):
        query_params = self.query_params or {}

        fb_dc_start_from = query_params.get('fb_dc_start_from')
        fb_dc_end_to = query_params.get('fb_dc_end_to')

        if fb_dc_start_from:
            qs = qs.filter(created_at__gte=fb_dc_start_from)

        if fb_dc_end_to:
            qs = qs.filter(created_at__lte=fb_dc_end_to)

        return qs