from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ContractSerializer
from .models import CustomUser, Contract, RiskAnalysis
from .services import ContractAnalyzer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class ContractUploadView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ContractSerializer

    def perform_create(self, serializer):
        contract = serializer.save(user=self.request.user)
        analyzer = ContractAnalyzer()
        risk_analysis = analyzer.analyze_contract(contract)
        return Response({
            'contract': ContractSerializer(contract).data,
            'risk_analysis': {
                'risk_score': risk_analysis.risk_score,
                'summary': risk_analysis.summary,
                'risky_clauses': risk_analysis.risky_clauses
            }
        }, status=status.HTTP_201_CREATED)

class ContractListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ContractSerializer

    def get_queryset(self):
        return Contract.objects.filter(user=self.request.user)

class ContractDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ContractSerializer

    def get_queryset(self):
        return Contract.objects.filter(user=self.request.user)

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
