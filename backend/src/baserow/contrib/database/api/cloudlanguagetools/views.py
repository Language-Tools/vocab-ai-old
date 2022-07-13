
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from baserow.contrib.database.api.tokens.authentications import TokenAuthentication
from rest_framework.decorators import permission_classes as method_permission_classes

class CloudLanguageToolsLanguageDataView(APIView):
    authentication_classes = APIView.authentication_classes + [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return super().get_permissions()

    @extend_schema(
        tags=["cloudlanguagetools language data"],
        operation_id="language_data",
        description=(
            "Retrieve all languages, translation and transliteration options"
        ),
    )
    @method_permission_classes([AllowAny])
    def get(self, request):

        data = {'yo 1': 'yo 2'}
        return Response(data)
