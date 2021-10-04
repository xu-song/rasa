from typing import List, Dict, Text, Text

import numpy as np
import scipy.sparse

from rasa.shared.nlu.constants import FEATURE_TYPE_SENTENCE
from rasa.shared.nlu.training_data.features import Features


class MultiHotEncoder:
    def __init__(self, dimension_names: List[Text]):
        """

        Every ordering of dimension names will yield the same encoding.

        Args:
           dimension_names: unique dimension names in arbitrary order
        """
        if len(set(dimension_names)) != len(dimension_names):
            raise ValueError("Expected the dimension names to be unique.")
        self.dimension_name_to_index: Dict[Text, int] = {
            name: idx for idx, name in enumerate(sorted(dimension_names))
        }

    def encode_as_sparse_sentence_feature(
        self, dimension_names_to_values: Dict[Text, int],
    ) -> Features:
        dim = len(self.dimension_name_to_index)
        row = np.zeros(dim, dtype=int)
        col = np.zeros(dim, dtype=int)
        data = np.zeros(dim, dtype=float)
        for dim_name, value in dimension_names_to_values.items():
            index = self.dimension_name_to_index.get(dim_name)
            if index:
                col.append(index)
                data.append(value)
        features = scipy.sparse.coo_matrix((data, (row, col)))
        return Features(
            features,
            FEATURE_TYPE_SENTENCE,
            self.attribute,
            origin=self.__class__.__name__,
        )

    def encode_as_index(self, dimension_name: Text,) -> int:
        """
        Raises:
           `RuntimeError` if one of the given dimension names is unknown
        """
        index = self.dimension_name_to_index.get(dimension_name, None)
        if index is None:
            raise RuntimeError(
                f"Expected given `dimension_name` to be one of "
                f"{sorted(self.dimension_name_to_index.keys())} but was "
                f"given {dimension_name}."
            )
        return index

    def encode_as_index_array(self, dimension_names: List[Text],) -> np.ndarray:
        """
        Returns:
           an array of shape `[len(dimension_names)]` filled with the indices
        Raises:
           `RuntimeError` if one of the given dimension names is unknown
        """
        return np.array(
            [self.encode_as_index(name) for name in dimension_names], dtype=int
        )

    def encode_as_array_of_index_arrays(
        self, dimension_names: List[List[Text]],
    ) -> np.ndarray:
        """

        Returns:
           array filled with objects that are arrays containing the indices
           for the corresponding inner list of the given `dimension_names`
        Raises:
           `RuntimeError` if one of the given dimension names is unknown
        """
        return np.array(
            [self.encode_as_index_array(inner_list) for inner_list in dimension_names],
            dtype=int,
        )
