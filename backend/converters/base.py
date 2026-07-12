from abc import ABC, abstractmethod

class BaseConverter(ABC):
    @abstractmethod
    def can_convert(self, from_ext: str, to_ext: str) -> bool:
        """Returns True if this converter supports converting from_ext to to_ext."""
        pass

    @abstractmethod
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        """Converts input_path to output_path. Returns True on success, raises exception on error."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the engines or dependencies needed for this converter are available."""
        pass
