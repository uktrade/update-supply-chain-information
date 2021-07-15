from rest_framework import serializers


class ActivityStreamSerializer(serializers.ModelSerializer):
    department_prefix = "dit"
    app_name = "UpdateSupplyChainInformation"
    app_key_prefix = f"{department_prefix}:{app_name}"

    def _get_generator(self):
        """
        Get a serialized representation of the generator.
        """
        return {
            "name": self.app_key_prefix,
            "type": "Application",
            "id": f"{self.app_key_prefix}:ActivityStreamGenerator",
        }

    def to_representation(self, instance):
        activity_type = "Announce"
        object_type = instance["object_type"]
        object_representation = instance["json"]
        foreign_keys = instance["foreign_keys"]["keys"]
        # for some reason, the keys JSON object turns into the string "{}" if empty
        # so check that it really is a list
        if isinstance(foreign_keys, list):
            self._update_foreign_keys(foreign_keys, object_representation)
        instance_id = object_representation.pop("id")
        item_id = self._build_item_id(instance_id, object_type)
        representation = {
            "id": f"{item_id}:{activity_type}",
            "name": f"{object_type} {instance_id}",
            "type": activity_type,
            "published": instance["last_modified"],
            "generator": self._get_generator(),
            "object": {
                "id": item_id,
                "type": f"{self.app_key_prefix}:{object_type}",
            },
        }
        representation["object"].update(object_representation)
        return representation

    def _update_foreign_keys(self, foreign_keys, object_representation):
        # As the Activity Stream format uses a specific format for ID fields
        # we duplicate foreign keys in that format
        # to make searching for related itewms in ElasticSearch easier
        for foreign_key, related_object_type in foreign_keys:
            related_item = object_representation[foreign_key]
            if related_item:
                # there is one, or more
                if isinstance(related_item, str):
                    # ForeignKey and OneToOne relationships just have a single key
                    object_representation[f"es_{foreign_key}"] = self._build_item_id(
                        related_item, related_object_type
                    )
                else:
                    # reverse ForeignKey and ManyToMany relationships have multiple keys
                    object_representation[f"es_{foreign_key}"] = [
                        self._build_item_id(related_item_key, related_object_type)
                        for related_item_key in related_item
                    ]

    def _build_item_id(self, instance_id, object_type):
        item_id = f"{self.app_key_prefix}:{object_type}:{instance_id}"
        return item_id

    class Meta:
        model = None
