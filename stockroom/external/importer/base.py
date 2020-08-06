import abc


class BaseImporter(abc.ABC):
    name = None

    @abc.abstractmethod
    def column_names(self):
        """
        Return the names for each data entitiy. For instance, if each data sample returns
        an image and a label, this function could return `(image, label)` so that
        stockroom creates an image column for image data and label column for label data
        """

    @abc.abstractmethod
    def shapes(self):
        """
        Return the shape of the data sample(s). Return a tuple of shapes if one data
        sample has more than one data entity. For instance, if the data sample is
        image and label, this function need to return `(shape of image, shape of label)`.
        If the shape is variable, return the maximum value of shape in each dimension.
        """
        pass

    @abc.abstractmethod
    def dtypes(self):
        """
        Return the datatype of the data sample. The data must be homogenous across
        dataset. If one data sample has more than one data entity, return a tuple
        of dtypes. For instance, if the data sample is image and label, then this
        function should return `(dtype of image, dtype of label)`.
        """
        pass

    @abc.abstractmethod
    def variability_status(self):
        """
        Return True/False depending on the shape of the data sample across the
        dataset is variable or not. If the data sample contains more than one data
        entity, this function should return tuple of boolean values. For instance,
        if the data sample is image and label, then this function should return
        `(is_variable(image), is_variable(label))` where `is_variable` is a custom
        function to check the variability across the dataset.
        """
        pass

    @abc.abstractmethod
    def __iter__(self):
        """
        Yield data sample from the dataset. If the data sample contains more than one
        data entity, this function should return a tuple. For instance, if the data
        sample is image and label, then this function should return `(image, label)`.

        Note that the keys for each data sample would be integers incrementing by one
        from zero to len(dataset). In the current implementation, setting custom keys
        is not allowed but might enable in the future releases
        """
        pass

    @abc.abstractmethod
    def __len__(self):
        """
        Return the length of the dataset. Simlar to `len(pytorch_dataset)`
        """
        pass
