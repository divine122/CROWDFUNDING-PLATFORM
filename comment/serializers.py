from rest_framework import serializers
from . models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id','is_approved','created_at','updated_at']


        def validate_text(self,value):
            if not value.strip():
                raise serializers.ValidationError('Comment cannot be empty')
            return value