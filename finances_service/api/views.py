from marshmallow import ValidationError
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Transaction, UserProfile
from .serializers import TransactionSerializer
from .services import (
    BudgetService,
    TransactionService,
    ExpensesByCategoriesService,
    TransactionsByWeekService,
)


class BudgetView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        budget_service = BudgetService()
        try:
            data = budget_service.get_user_budget(user_id)
            return Response(data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "UserProfile does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )


class TransactionsView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        name = request.query_params.get("name")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction_service = TransactionService()
        transactions = transaction_service.get_user_transactions(
            user_id, name, start_date, end_date
        )
        serializer = TransactionSerializer(transactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ExpensesByCategoriesView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        service = ExpensesByCategoriesService()
        try:
            expenses_data = service.get_expenses_by_categories(user_id)
        except UserProfile.DoesNotExist:  # Теперь мы ловим исключение здесь
            return Response(
                {"error": "UserProfile does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(expenses_data, status=status.HTTP_200_OK)


class TransactionsByWeekView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        transactions_by_week_service = TransactionsByWeekService()
        try:
            data = transactions_by_week_service.get_transactions_by_week(user_id)
            return Response(data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "UserProfile does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )


class AddTransactionView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction_service = TransactionService()

        try:
            transaction = transaction_service.add_transaction(user_id, request.data)
            return Response(
                TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "UserProfile does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            # Если данные не прошли валидацию в сериализаторе
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Обработка других неожиданных исключений
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteTransactionView(APIView):
    def delete(self, request, id, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction_service = TransactionService()
        try:
            transaction_service.delete_transaction(user_id, id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": " User profile does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "Transaction deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class CategoriesView(APIView):
    def get(self, request, *args, **kwargs):
        categories_service = CategoriesService()
        categories = categories_service.get_all_categories()
        return Response(categories, status=status.HTTP_200_OK)
