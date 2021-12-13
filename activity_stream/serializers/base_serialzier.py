from rest_framework import serializers


class ActivityStreamSerializer(
    serializers.ModelSerializer,
):
    department_prefix = "dit"
    app_name = "ResilienceTool"
    app_key_prefix = f"{department_prefix}:{app_name}"

    def to_representation(self, instance):
        object_representation = super().to_representation(instance)
        activity_type = "Announce"
        object_type = type(instance).__name__

        item_id = self._build_item_id(instance.pk, object_type)
        representation = {
            "id": f"{item_id}:{activity_type}",
            "name": f"{object_type} {instance.pk}",
            "type": activity_type,
            "generator": self._get_generator(),
            "object": {
                "id": item_id,
                "type": f"{self.app_key_prefix}:{object_type}",
            },
        }

        if hasattr(instance, "last_modified"):
            representation["published"] = instance.last_modified

        representation["object"].update(object_representation)

        return representation

    def _build_item_id(self, instance_id, object_type):
        item_id = f"{self.app_key_prefix}:{object_type}:{instance_id}"
        return item_id

    def _get_generator(self):
        """
        Get a serialized representation of the generator.
        """
        return {
            "name": self.app_key_prefix,
            "type": "Application",
            "id": f"{self.app_key_prefix}:ActivityStreamGenerator",
        }
