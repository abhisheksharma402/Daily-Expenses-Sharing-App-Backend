from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from .models import User, Expense, ExpenseSplit, Balance
from .serializers import UserSerializer, ExpenseSerializer, BalanceSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_expenses(self, request, user_id=None):
        """
        Retrieve all expenses from ExpenseSplit where the specified user is involved.
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        splits = ExpenseSplit.objects.filter(user=user)

        response_data = [
            {
                "amount_owed": split.amount_owed,
                "expense_id": split.expense.id,
                "date_of_expense_creation": split.expense.created_at,
                "expense_description": split.expense.description
            }
            for split in splits
        ]

        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/overall')
    def user_overall_expenses(self, request, user_id=None):
        """
        Retrieve overall expenses for a specific user.
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        expense_splits = ExpenseSplit.objects.filter(user=user)
        amount_owed = expense_splits.aggregate(total=Sum('amount_owed'))['total'] or 0

        response_data = {
            'user_id': user.id,
            'username': user.username,
            # 'total_expenses': total_amount,
            'total_amount_owed': amount_owed,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    

class BalanceView(viewsets.ReadOnlyModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer

    @action(detail=False, methods=['get'])
    def download(self, request):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, "Balance Sheet")
        
        y = 700
        for balance in Balance.objects.all().select_related('user'):
            line = f"{balance.user.username}: ${balance.balance}"
            p.drawString(100, y, line)
            y -= 20
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.pdf"'
        
        return response
class DownloadBalanceSheetView(APIView):
    def get(self, request):
        response_content = "download balance sheet view"
        return HttpResponse(response_content, content_type='application/pdf')


class CustomLoginView(LoginView):
    template_name = '/home/abhisheksharma/abhishek/DJANGo/expenses_project/expenses/templates/resgistration/login.html'  # Path to your login template
    success_url = reverse_lazy('expenses-list')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)