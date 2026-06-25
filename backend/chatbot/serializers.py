from rest_framework import serializers


class ChatbotMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000, trim_whitespace=True)
    contextType = serializers.CharField(max_length=40, required=False, allow_blank=True)

    def validate_message(self, value):
        if not value:
            raise serializers.ValidationError("질문을 입력해주세요.")
        if len(value) > 1000:
            raise serializers.ValidationError("질문은 1000자 이내로 입력해주세요.")
        return value
