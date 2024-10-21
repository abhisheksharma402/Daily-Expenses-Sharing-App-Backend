from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import User, Expense, ExpenseSplit, Balance
from .serializers import UserSerializer, ExpenseSerializer, BalanceSerializer

class UserViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', email='test@example.com', mobile_number='1234567890')
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        url = reverse('user-list')
        data = {'username': 'newuser', 'email': 'newuser@example.com', 'mobile_number': '9876543210'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_get_user_details(self):
        url = reverse('user-details', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['mobile_number'], '1234567890')

class ExpenseViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(username='user1', email='user1@example.com', mobile_number='1111111111')
        self.user2 = User.objects.create(username='user2', email='user2@example.com', mobile_number='2222222222')
        self.client.force_authenticate(user=self.user1)

    def test_create_expense(self):
        url = reverse('expense-list')
        data = {
            'creator': self.user1.id,
            'paid_by': self.user1.id,
            'participants': [self.user1.id, self.user2.id],
            'total_amount': '100.00',
            'description': 'Test Expense',
            'split_method': 'equal',
            'splits': [
                {'user': self.user2.id, 'amount_owed': '50.00'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpenseSplit.objects.count(), 1)

    def test_get_user_expenses(self):
        expense = Expense.objects.create(
            creator=self.user1,
            paid_by=self.user1,
            total_amount=Decimal('100.00'),
            description='Test Expense',
            split_method='equal'
        )
        expense.participants.add(self.user1, self.user2)
        ExpenseSplit.objects.create(expense=expense, user=self.user2, amount_owed=Decimal('50.00'))

        url = reverse('expense-user-expenses', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount_owed'], 50.00)

class BalanceViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', email='test@example.com', mobile_number='1234567890')
        self.balance = Balance.objects.create(user=self.user, balance=100.00)
        self.client.force_authenticate(user=self.user)

    def test_get_balance(self):
        url = reverse('balance-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['balance'], 100.0)

    def test_download_balance_sheet(self):
        url = reverse('balance-download')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="balance_sheet.pdf"'))

class SerializerTestCase(TestCase):
    def test_user_serializer(self):
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'mobile_number': '1234567890'
        }
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())

    def test_expense_serializer(self):
        user1 = User.objects.create(username='user1', email='user1@example.com', mobile_number='1111111111')
        user2 = User.objects.create(username='user2', email='user2@example.com', mobile_number='2222222222')
        
        expense_data = {
            'creator': user1.id,
            'paid_by': user1.id,
            'participants': [user1.id, user2.id],
            'total_amount': '100.00',
            'description': 'Test Expense',
            'split_method': 'equal',
            'splits': [
                {'user': user2.id, 'amount_owed': '50.00'}
            ]
        }
        serializer = ExpenseSerializer(data=expense_data)
        self.assertTrue(serializer.is_valid())
