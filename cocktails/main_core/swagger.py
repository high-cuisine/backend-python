from drf_yasg.inspectors import SwaggerAutoSchema


class CompoundTagsSchema(SwaggerAutoSchema):

    def get_tags(self, operation_keys=None):
        tags = super().get_tags(operation_keys=operation_keys)
        tags_string = ' > '.join(tags)

        # Legacy
        if tags and tags[0] in ['backoffice', 'request']:
            tags_string = f'Legacy > {tags_string}'

        return [tags_string]
