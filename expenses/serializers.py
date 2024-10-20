from rest_framework import serializers
from .models import User, Expense, ExpenseSplit, Balance
from django.db import transaction
import pdb

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'mobile_number']

class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['user', 'amount_owed']

class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'creator', 'paid_by', 'participants', 'total_amount', 'description', 'split_method', 'created_at', 'splits']

    @transaction.atomic
    def create(self, validated_data):
        split_data = self.context['request'].data.get('splits', [])
        total_amount = validated_data['total_amount']
        participants = validated_data['participants']
        paid_by = validated_data['paid_by']
        user_ids = [participant.id for participant in participants]
        
        validated_data['participants'] = set(validated_data['participants'])
        participants = validated_data.pop('participants', [])
        
        expense = Expense.objects.create(**validated_data)
        expense.participants.set(participants)

        split_method = validated_data.get('split_method')

        # pdb.set_trace()
        total_owed_amount=0
        if split_method == 'equal':
            num_participants = len(participants)
            amount_per_participant = total_amount / num_participants
            for participant in participants:
                if participant != paid_by:
                    ExpenseSplit.objects.create(expense=expense, user=participant, amount_owed=amount_per_participant)
                    
                    # Update participant's balance
                    total_owed_amount += amount_per_participant
                    participant_balance, _ = Balance.objects.get_or_create(user=participant)
                    participant_balance.balance -= float(amount_per_participant)
                    participant_balance.save()
        
        elif split_method == 'exact':
            total_split_amount = 0
            for split in split_data:
                user_id = split['user']
                amount_owed = split['amount_owed']
                
                if user_id not in user_ids:
                    raise serializers.ValidationError(f"User with ID {user_id} is not a participant of this expense.")

                total_split_amount += amount_owed
                if user_id != paid_by.id:
                    ExpenseSplit.objects.create(expense=expense, user_id=user_id, amount_owed=amount_owed)
                    total_owed_amount += amount_owed

                    # Update participant's balance
                    participant_balance, _ = Balance.objects.get_or_create(user_id=user_id)
                    participant_balance.balance -= float(amount_owed)
                    participant_balance.save()

            if total_split_amount != total_amount:
                raise serializers.ValidationError("The sum of exact amounts does not equal the total amount.")

        elif split_method == 'percentage':
            total_percentage = 0
            for split in split_data:
                user_id = split['user']
                percentage = split['percentage']

                if user_id not in user_ids:
                    raise serializers.ValidationError(f"User with ID {user_id} is not a participant of this expense.")

                amount_owed = (percentage / 100) * float(total_amount)
                
                total_percentage += percentage
                if user_id != paid_by.id:
                    ExpenseSplit.objects.create(expense=expense, user_id=user_id, amount_owed=amount_owed)
                    total_owed_amount += amount_owed

                    # Update participant's balance
                    participant_balance, _ = Balance.objects.get_or_create(user_id=user_id)
                    participant_balance.balance -= float(amount_owed)
                    participant_balance.save()
            
            
            if total_percentage != 100:
                raise serializers.ValidationError("The total of all percentages must equal 100%.")

        else:
            raise serializers.ValidationError("Invalid split method specified.")
        
        #update payer's balance
        participant_balance, _ = Balance.objects.get_or_create(user=paid_by)
        participant_balance.balance += float(total_amount) - float(total_owed_amount)
        participant_balance.save()
        
        return expense

class BalanceSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Balance
        fields = ['user', 'balance']