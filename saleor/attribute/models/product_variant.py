from django.db import models

from ...core.models import SortableModel
from ...product.models import ProductType, ProductVariant
from .base import AssociatedAttributeManager


class AssignedVariantAttributeValue(SortableModel):
    value = models.ForeignKey(
        "AttributeValue",
        on_delete=models.CASCADE,
        related_name="variantvalueassignment",
    )
    variant = models.ForeignKey(
        ProductVariant,
        related_name="attributevalues",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    class Meta:
        unique_together = (("value", "variant"),)
        ordering = ("sort_order", "pk")

    def get_ordering_queryset(self):
        return self.variant.attributevalues.all()


# class AssignedVariantAttribute(BaseAssignedAttribute):
#     """Associate a product type attribute and selected values to a given variant."""

#     variant = models.ForeignKey(
#         ProductVariant, related_name="attributes", on_delete=models.CASCADE
#     )
#     assignment = models.ForeignKey(
#         "AttributeVariant", on_delete=models.CASCADE, related_name="variantassignments"
#     )
#     values = models.ManyToManyField(
#         AttributeValue,
#         blank=True,
#         related_name="variantassignments",
#         through=AssignedVariantAttributeValue,
#     )


class AttributeVariant(SortableModel):
    attribute = models.ForeignKey(
        "Attribute", related_name="attributevariant", on_delete=models.CASCADE
    )
    product_type = models.ForeignKey(
        ProductType, related_name="attributevariant", on_delete=models.CASCADE
    )
    variant_selection = models.BooleanField(default=False)

    objects = AssociatedAttributeManager()

    class Meta:
        unique_together = (("attribute", "product_type"),)
        ordering = ("sort_order", "pk")

    def get_ordering_queryset(self):
        return self.product_type.attributevariant.all()
