from typing import List, Type, Set, Callable, Any, Collection, Tuple, Optional, Union, Iterable, Mapping, Dict
from interfaces import FacetFilter, FacetFilterConstraint, Faceted

def __raise(
        arg: Any,
        err_cond: Callable[[Any], bool],
        err_type: Type[BaseException],
        err_msg: str,
        ) -> None:
    if err_cond(arg):
        raise err_type(err_msg)
    else:
        pass
    
def __raise_type_error_if_arg_not_string(arg: Any, err_msg: str) -> None:
    __raise(
        arg,
        lambda a: not isinstance(a, str),
        TypeError,
        err_msg
        )
    
def __raise_value_error_if_arg_is_empty_string(arg: Any, err_msg: str) -> None:
    __raise(
        arg,
        lambda a: a == "",
        ValueError,
        err_msg
    )

class FacetFilterDerivedFromDataset(FacetFilter):
    # mypy requires this, don't know why, must figure out
    def __init__(self, key: str):
        pass

    def add_option(self, option: Optional[Union[str, Collection[str], int]]) -> None:
        pass

class FacetFilterConstraintCreatedFromConstraint(FacetFilterConstraint):
    @classmethod
    def from_constraint(cls, constraint: Tuple[str, Any]):
        pass

class FacetFilterWithStrOptions:

    def __init__(self, key: str) -> None:
        if not isinstance(key, str):
            raise TypeError("Facet key must be of type 'str'")
        if not key:
            raise ValueError("Facet key cannot be an empty string")
        self.__key = key
        self.__options: Set[str] = set()

    def add_option(self, option: Optional[Union[str, Collection[str], int]]) -> None:
        if not isinstance(option, str):
            raise TypeError("option must be of type 'str'")
        if not option:
            raise ValueError("option cannot be an empty string")
        self.__options.add(option)

    def key(self) -> str:
        return self.__key
    
    def options(self) -> Collection[str]:
        return list(self.__options)
    
class SingleSelectionFacetFilterConstraint:

    def __init__(self, key: str, selected_option: str) -> None:
        __raise_type_error_if_arg_not_string(
            key,
            "Facet constraint key must be of type 'str'"
            )
        __raise_type_error_if_arg_not_string(
            selected_option,
            "Facet constraint selected option must be of type 'str'"
        )
        __raise_value_error_if_arg_is_empty_string(
            key,
            "Facet constraint key cannot be an empty string"
        )
        __raise_value_error_if_arg_is_empty_string(
            selected_option,
            "Facet constraint selected option cannot be an empty string"
        )
        self.__key = key
        self.__selected = selected_option

    def key(self) -> str:
        return self.__key
    
    def is_satisfied_by(self, datum: Faceted) -> bool:
        return datum.facet_view_value(self.key()) == self.__selected
    
    @classmethod
    def from_constraint(cls, constraint: Tuple[str, Any]):
        def _two_tuple_of_strings(c: Any) -> bool:
            if not isinstance(c, tuple):
                return True
            if not len(c) == 2:
                return True
            if not all([isinstance(el, str) for el in c]):
                return True
            return False
        __raise(
            constraint,
            _two_tuple_of_strings,
            TypeError,
            "constraint must be a two-tuple of 'str' type"
        )
        key, selected_option = constraint
        return cls(key, selected_option)

class FacetFilterComponentImpl:

    def __self__(
            self,
            facet_filter_types: List[Type[FacetFilterDerivedFromDataset]],
            facet_filter_constraint_types: List[Type[FacetFilterConstraintCreatedFromConstraint]]
            ) -> None:
        self.__facet_filter_types = facet_filter_types
        self.__facet_filter_constraint_types = facet_filter_constraint_types

    def __derive_facet_filter_from_key_and_option(self, key: str, option: Optional[Union[str, Collection[str], int]]) -> FacetFilterDerivedFromDataset:
        for facet_filter_type in self.__facet_filter_types:
            try:
                possible_facet_filter_obj = facet_filter_type(key)
                possible_facet_filter_obj.add_option(option)
                return possible_facet_filter_obj
            except:
                continue
        raise ValueError()
    
    def __derive(self, dataset: Iterable[Faceted]) -> Collection[FacetFilter]:
        facet_filter_for_view: Dict[str, FacetFilterDerivedFromDataset] = dict()
        for datum in dataset:
            for facet_view in datum.facet_views():
                facet_view_value = datum.facet_view_value(facet_view)
                if facet_view_value is None:
                    continue
                if facet_view in facet_filter_for_view.keys():
                    facet_filter_for_view[facet_view].add_option(facet_view_value)
                else:
                    facet_filter_for_view[facet_view] = self.__derive_facet_filter_from_key_and_option(facet_view, facet_view_value)
        return facet_filter_for_view.values()


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