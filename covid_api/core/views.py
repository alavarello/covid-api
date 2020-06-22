from django.shortcuts import render
from rest_framework.generics import GenericAPIView

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class DataView(APIView):

    def get(self, request):
        """
        Return a list of all users.
        """

        response = {'hello_world': 'hello_world'}
        return Response(response)
