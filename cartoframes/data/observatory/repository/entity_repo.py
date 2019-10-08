from cartoframes.exceptions import DiscoveryException
from cartoframes.data.observatory.entity import CatalogList
from .repo_client import RepoClient

try:
    from abc import ABC, abstractmethod
except ImportError:
    from abc import ABCMeta, abstractmethod
    ABC = ABCMeta('ABC', (object,), {'__slots__': ()})


class EntityRepository(ABC):

    def __init__(self, id_field, filters):
        self.client = RepoClient()

        self.id_field = id_field
        self.allowed_filters = filters + [id_field]

    def get_all(self, filters=None):
        return self._get_filtered_entities(filters)

    def get_by_id(self, id_):
        result = self._get_rows({self.id_field: id_})

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing entity in the catalog. '
                                     'You can check the full list of available values with get_all() method')

        data = self._map_row(result[0])
        return self._to_catalog_entity(data)

    def _get_filtered_entities(self, filters=None):
        cleaned_filters = self._get_filters(filters)
        rows = self._get_rows(cleaned_filters)

        if len(rows) == 0:
            return None

        normalized_data = [self._get_entity_class()(self._map_row(row)) for row in rows]
        return CatalogList(normalized_data)

    def _get_filters(self, filters):
        if filters is not None:
            cleaned_filters = {field: value for field, value in filters.items() if field in self.allowed_filters}
            return cleaned_filters

    @classmethod
    def _to_catalog_entity(cls, result):
        return cls._get_entity_class()(result)

    @classmethod
    def _normalize_field(cls, row, field):
        if field in row:
            return row[field]

        return None

    @classmethod
    @abstractmethod
    def _get_entity_class(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _map_row(cls, row):
        raise NotImplementedError

    @abstractmethod
    def _get_rows(self, filters=None):
        raise NotImplementedError
