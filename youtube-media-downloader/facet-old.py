from interfaces import Faceted, FacetFilter, FacetFilterConstraint
from typing import Iterable, Optional, Mapping, Any, Collection

class MultiValuedDerivedFacet:

    def __init__(self, name: str, values: Optional[Collection[str]] = None) -> None:
        self.__name = name
        if not values:
            self.__values = set()
        else:
            values_set = set(values)
            for value in values_set:
                self.__add_value(value)

    def __add_value(self, value: str):
        if isinstance(value, str):
            if not value:
                raise ValueError()
            self.__values.add(value)
        else:
            raise TypeError()
        
    def add_value(self, value: str):
        self.__add_value(value)
        
    def view_name(self) -> str:
        return self.__name
    
    def view_values(self) -> Collection[str]:
        return list(self.__values)
    
class SingleSelectionFacetConstraint:

    def __init__(self, name: str, selection: str):
        self.__name = name
        self.__selection = selection

    def view_name(self) -> str:
        return self.__name
    
    def is_satisfied_by(self, datum: Faceted) -> bool:
        value = datum.facet_value(self.__name)
        return value == self.__selection

class FacetComponentImpl:

    def __init__(self):
        pass

    def __derive_facet_views_and_values_from(self, dataset: Iterable[Faceted]) -> Mapping[str, Collection[str]]:
        facets_encountered = dict()
        for datum in dataset:
            for facet_view in datum.facet_views():
                facet_value = datum.facet_view_value(facet_view)
                if not facet_value:
                    continue
                if facet_view in facets_encountered.keys():
                    facets_encountered[facet_view].append(facet_value)
                else:
                    facets_encountered[facet_view] = [facet_value]
        return facets_encountered
    
    def __derive_facet_constraints_from(self, constraints: Optional[Mapping[str, str]]) -> Collection[FacetConstraint]:
        facet_constraints: Collection[FacetConstraint] = []
        for facet_view, selected_facet_value in constraints.items():
            facet_constraint = SingleSelectionFacetConstraint(facet_view, selected_facet_value)
            facet_constraints.append(facet_constraint)
        return facet_constraints
    
    def derive_facets(self, dataset: Iterable[Faceted]) -> Collection[DerivedFacet]:
        # derive a collection of all facet views
        # initialize a Facet object for every facet view from the above collection
        # create a mapping between the name of the facet view and the corresponding Facet object
        # for every datum in dataset,
        # for every facet view that the datum supports
        # try to access the value of that facet view as held by that datum
        # and add it to the corresponding Facet object's values.
        # return all the Facet objects that have more than one value
        facets_data = self.__derive_facet_views_and_values_from(dataset)
        facets: Collection[DerivedFacet] = []
        for facet_view, facet_view_values in facets_data.items():
            if len(facet_view_values) > 1:
                facets.append(MultiValuedDerivedFacet(facet_view, facet_view_values))
        return facets

    def filter_by_facet_constraints(self, dataset: Iterable[Faceted], constraints: Optional[Mapping[str, str]]) -> Iterable[Faceted]:
        # TIP: let a FacetConstraint object be made responsible
        # of telling whether a given datum satisfies
        # the constraint it represents
        # All we need to do then is to create FacetConstraint objects
        # from the given facet constraints(the second argument)
        # Should we then use some common, well-known datastructure to represent constraints,
        # like Mapping or **constraints(inspired by **kwargs)
        # Should we do the same for derive_facets too,
        # represent derived Facets using some well-known datastructure
        facet_constraints = self.__derive_facet_constraints_from(constraints)
        # create a list of FacetConstraint objects
        # for every datum in dataset,
        # check if the datum satisfies all the FacetConstraints
        # if yes, add it to the list of objects you want to return
        filtered_dataset: Iterable[Faceted] = []
        for datum in dataset:
            if all([facet_constraint.is_satisfied_by(datum) for facet_constraint in facet_constraints]):
                filtered_dataset.append(datum)
        return filtered_dataset
