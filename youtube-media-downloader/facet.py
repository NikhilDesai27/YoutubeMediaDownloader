from typing import List, Type, Set, Callable, Any, Collection, Tuple, Optional, Union, Iterable, Mapping, Dict
from interfaces import FacetFilter, FacetFilterConstraint, Faceted

class DerivedFacetFilter(FacetFilter):

    @classmethod
    def from_view_name_and_options(cls, name: str, options: List[Optional[Union[str, int]]]):
        pass

class DerivedFacetFilterConstraint(FacetFilterConstraint):
    
    @classmethod
    def from_constraint(cls, constraint: Tuple[str, Any]):
        pass

class FacetFilterWithStrOptions:

    def __init__(self, key: str) -> None:
        self.__key = key
        self.__options: Set[str] = set()

    def __add_option(self, option: Optional[Union[str, int]]) -> None:
        if not isinstance(option, str):
            raise TypeError("option must be of type 'str'")
        if not option:
            raise ValueError("option cannot be an empty string")
        self.__options.add(option)

    def key(self) -> str:
        return self.__key
    
    def options(self) -> Collection[str]:
        return list(self.__options)
    
    @classmethod
    def from_view_name_and_options(cls, name: str, options: List[Optional[Union[str, int]]]):
        facet_filter_obj = cls(name)
        for option in options:
            facet_filter_obj.__add_option(option)
        return facet_filter_obj
    
class FacetFilterConstraintWithSingleStrSelection:

    def __init__(self, key: str) -> None:
        self.__key = key

    def __set_selected_option(self, selected_option: Any):
        if not isinstance(selected_option, str):
            raise TypeError("Facet constraint selected option must be of type 'str'")
        if not selected_option:
            raise ValueError("Facet constraint selected option cannot be an empty string")
        self.__selected = selected_option

    def key(self) -> str:
        return self.__key
    
    def is_satisfied_by(self, datum: Faceted) -> bool:
        return datum.facet_view_value(self.key()) == self.__selected
    
    @classmethod
    def from_constraint(cls, constraint: Tuple[str, Any]):
        key, selected_option = constraint
        facet_filter_constraint_obj = cls(key)
        facet_filter_constraint_obj.__set_selected_option(selected_option)
        return facet_filter_constraint_obj

class FacetFilterComponentImpl:

    def __self__(
            self,
            facet_filter_types: List[Type[DerivedFacetFilter]],
            facet_filter_constraint_types: List[Type[DerivedFacetFilterConstraint]]
            ) -> None:
        self.__facet_filter_types = facet_filter_types
        self.__facet_filter_constraint_types = facet_filter_constraint_types
    
    def derive_facet_filters(self, dataset: Iterable[Faceted]) -> Collection[FacetFilter]:
        facet_filters = self.__derive(dataset)
        return [facet_filter for facet_filter in facet_filters if len(facet_filter.options()) > 1]
    
    def __facet_filter_constraints_from_constraints(self, constraints: Mapping[str, Any]) -> Collection[FacetFilterConstraint]:
        facet_filter_constraints: List[FacetFilterConstraint] = []
        for constraint in constraints.items():
            for facet_filter_constraint_type in self.__facet_filter_constraint_types:
                try:
                    facet_filter_constraint = facet_filter_constraint_type.from_constraint(constraint)
                    facet_filter_constraints.append(facet_filter_constraint)
                    break
                except:
                    continue
        return facet_filter_constraints
    
    def __filter(self, dataset: Iterable[Faceted], constraints: Mapping[str, Any]) -> Iterable[Faceted]:
        facet_filter_constraints = self.__facet_filter_constraints_from_constraints(constraints)
        class FilteredDataset:
            def __init__(self) -> None:
                self.__exhausted = False
                self.__dataset_iter = iter(dataset)

            def __iter__(self):
                return self
            
            def __next__(self):
                if self.__exhausted:
                    raise StopIteration
                while True:
                    try:
                        datum = next(self.__dataset_iter)
                        passes_filter = all([facet_filter_constraint.is_satisfied_by(datum) for facet_filter_constraint in facet_filter_constraints])
                        if passes_filter:
                            return datum
                    except StopIteration:
                        self.__exhausted = True
                        raise StopIteration
        
        return FilteredDataset()

    def filter_by_facet_constraints(self, dataset: Iterable[Faceted], constraints: Mapping[str, Any]) -> Iterable[Faceted]:
        return self.__filter(dataset, constraints)