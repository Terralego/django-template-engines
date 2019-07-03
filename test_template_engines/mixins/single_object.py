from django.http import Http404
from django.utils.translation import gettext as _
from django.views.generic.detail import \
    SingleObjectMixin as DjangoSingleObjectMixin


class SingleObjectMixin(DjangoSingleObjectMixin):
    lookup_field = 'pk'
    lookup_field_url_kwargs = 'pk'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        content_field = self.kwargs.get(self.lookup_field_url_kwargs)
        if content_field is not None:
            queryset = queryset.filter(**{self.lookup_field: content_field})
        else:
            raise AttributeError(
                "Generic detail view %s must be called with an object." % self.__class__.__name__
            )

        if queryset.count() > 1:
            raise AttributeError(
                "The field must be a primary key. Multiple objects are prohibited."
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
