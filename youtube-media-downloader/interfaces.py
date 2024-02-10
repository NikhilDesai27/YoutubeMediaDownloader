from typing import Protocol, Optional, Iterable, Mapping, Any, Union, List, Collection
from pathlib import Path

class YoutubeMedia(Protocol):
    """
    `YoutubeMedia` represents the idea of a Youtube content object.
    Youtube stores content in various formats(file_types)
    and qualities(resolution, audio bit rate, codecs, etc...).
    This concept will be common knowledge for
    both the `core` and the `controller` components.
    """
    def id(self) -> str:
        pass

    def media_type(self) -> str:
        pass

    def file_type(self) -> str:
        pass

    def resolution(self) -> Optional[str]:
        pass

    def audio_bit_rate(self) -> Optional[str]:
        pass

    def download(self, filename_to_save_as: str) -> str:
        pass

class CoreComponent(Protocol):
    """
    `CoreComponent` represents the Youtube API.
    It can tell us if a given URL points to a valid Youtube content,
    and the various media options that Youtube has stored the content in.
    """
    def media_options_for(self, content_url: str) -> Collection[YoutubeMedia]:
        pass

class Faceted(Protocol):
    """
    `Faceted` represents any object that has Facet views associated with it.
    It tells us about the different facet views an object supports.
    """
    def facet_views(self) -> Collection[str]:
        pass

    def facet_view_value(self, facet_key: str) -> Optional[Union[str, int]]:
        pass

class FacetFilter(Protocol):
    """
    `DerivedFacet` represents the idea of a facet view
    derived from a dataset(collection of `FacetViews`).
    """
    def key(self) -> str:
        pass

    def options(self) -> Collection[str]:
        pass

class FacetFilterConstraint(Protocol):
    """
    `FacetConstraint` represents the idea of a facet value selection
    as made by a user. The application of a filter if you will.
    """
    def key(self) -> str:
        pass

    def is_satisfied_by(self, datum: Faceted) -> bool:
        pass

class FacetFilterComponent(Protocol):
    """
    `FacetComponent` handles Facet derivation and filteration by Facet constraints for a collection of `Faceted` objects.
    
    Given an Iterable of `Faceted` objects and facet constraints/filters,
    it can return us an Iterable of `Faceted` objects that satisfy those constraints.
    """
    def derive_facet_filters(self, dataset: Iterable[Faceted]) -> Collection[FacetFilter]:
        """
        Given an Iterable of `Faceted` objects,
        it returns an Iterable of `DerivedFacet`s,
        wherein every `DerivedFacet` has several values.

        :param dataset: An iterable of `Faceted` objects
        :type dataset: Iterable[Faceted]
        :return: A collection of facets(name and values) derived from the dataset
        :rtype: Iterable[DerivedFacet]
        """
        pass

    def filter_by_facet_constraints(self, dataset: Iterable[Faceted], constraints: Mapping[str, Any]) -> Iterable[Faceted]:
        pass
