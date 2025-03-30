class MasterDep:

    def hasIndex(self, data, index):
        # Check if the data is a list, tuple, or string (indexable types)
        if isinstance(data, (list, tuple, str)):
            try:
                # Try accessing the element at the given index
                _ = data[index]  # This will raise an IndexError if the index is out of range
                return True  # If no error, index is valid
            except IndexError:
                return False  # If an IndexError occurs, the index is out of range
        # Check if the data is a dictionary (keys are index-like for lookup)
        elif isinstance(data, dict):
            return index in data  # For dictionaries, check if index is a key
        return False  # Ret

    def indexOf(self, data, value):
        # Check if the data is a list or tuple, and safely find the index
        if isinstance(data, (list, tuple, object)):
            try:
                return data.index(value)  # If the value is in the list/tuple, return its index
            except ValueError:
                return -1  # Return -1 if the value is not found
        else:
            return -1