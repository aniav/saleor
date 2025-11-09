import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ....page import models as page_models
from ....page.error_codes import PageErrorCode
from ....permission.enums import PagePermissions
from ...attribute.mutations import BaseReorderAttributeValuesMutation
from ...attribute.types import Attribute
from ...core import ResolveInfo
from ...core.context import ChannelContext
from ...core.doc_category import DOC_CATEGORY_PAGES
from ...core.inputs import ReorderInput
from ...core.types import NonNullList, PageError
from ...page.types import Page


class PageReorderAttributeValues(BaseReorderAttributeValuesMutation):
    page = graphene.Field(
        Page, description="Page from which attribute values are reordered."
    )

    class Meta:
        description = "Reorder page attribute values."
        doc_category = DOC_CATEGORY_PAGES
        permissions = (PagePermissions.MANAGE_PAGES,)
        error_type_class = PageError
        error_type_field = "page_errors"

    class Arguments:
        page_id = graphene.Argument(
            graphene.ID, required=True, description="ID of a page."
        )
        attribute_id = graphene.Argument(
            graphene.ID, required=True, description="ID of an attribute."
        )
        moves = NonNullList(
            ReorderInput,
            required=True,
            description="The list of reordering operations for given attribute values.",
        )

    @classmethod
    def perform_mutation(cls, _root, _info: ResolveInfo, /, **data):
        page_id = data["page_id"]
        page = cls.perform(page_id, "page", data, "attributevalues", PageErrorCode)
        return PageReorderAttributeValues(page=ChannelContext(page, channel_slug=None))

    @classmethod
    def get_instance(cls, instance_id: str):
        pk = cls.get_global_id_or_error(instance_id, only_type=Page, field="page_id")

        try:
            page = page_models.Page.objects.get(pk=pk)
        except ObjectDoesNotExist as e:
            raise ValidationError(
                {
                    "page_id": ValidationError(
                        (f"Couldn't resolve to a page: {instance_id}"),
                        code=PageErrorCode.NOT_FOUND.value,
                    )
                }
            ) from e
        return page

    @classmethod
    def validate_attribute_assignment(
        cls, instance, instance_type, attribute_id: str, error_code_enum
    ):
        """Validate if this attribute_id is assigned to this page."""
        attribute_pk = cls.get_global_id_or_error(
            attribute_id, only_type=Attribute, field="attribute_id"
        )

        attribute_assignment = instance.page_type.attributepage.filter(
            attribute_id=attribute_pk
        ).exists()

        if not attribute_assignment:
            raise ValidationError(
                {
                    "attribute_id": ValidationError(
                        f"Couldn't resolve to a {instance_type} "
                        f"attribute: {attribute_id}.",
                        code=error_code_enum.NOT_FOUND.value,
                    )
                }
            )
        return attribute_assignment
