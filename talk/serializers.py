from rest_framework import serializers
from .models import TalkModel, TalkCommentModel


class TalkSerializers(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = TalkModel
        fields = '__all__'
        depth = 1


class TalkCommentSerializers(serializers.ModelSerializer):
    pub_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = TalkCommentModel
        fields = '__all__'
        depth = 1
