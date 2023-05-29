import math


class Vec2i:
    """
    Class representing any 2D vector with integer components (x and y).

    For specific types of vectors, see e.g. TilePos and AbsPos.
    """

    def __init__(self, x: int = 0, y: int = 0):
        """
        :param x: x component of the vector
        :param y: y component of the vector
        """
        self.x: int = x
        self.y: int = y

    def __add__(self, other: 'Vec2i') -> 'Vec2i':
        """
        Returns the result of adding this vector to another vector.

        :param other: the other vector to add to this vector
        :return: the sum of the two vectors
        """
        return Vec2i(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vec2i') -> 'Vec2i':
        """
        Returns the result of subtracting another vector from this vector.

        :param other: the other vector to subtract from this vector
        :return: the difference between the two vectors
        """
        return Vec2i(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int) -> 'Vec2i':
        """
        Returns the result of multiplying this vector by a scalar.

        :param scalar: the scalar to multiply this vector by
        :return: the product of the vector and the scalar
        """
        return Vec2i(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: int) -> 'Vec2i':
        """
        Returns the result of multiplying this vector by a scalar.

        :param scalar: the scalar to multiply this vector by
        :return: the product of the vector and the scalar
        """
        return Vec2i(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: int) -> 'Vec2i':
        """
        Returns the result of dividing this vector by a scalar.

        :param scalar: the scalar to divide this vector by
        :return: the quotient of the vector and the scalar
        """
        return Vec2i(self.x // scalar, self.y // scalar)

    def __eq__(self, other: 'Vec2i') -> bool:
        """
        Returns True if this vector is equal to another vector.

        :param other: the other vector to compare to this vector
        :return: True if the vectors are equal, False otherwise
        """
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: 'Vec2i') -> bool:
        """
        Returns True if this vector is not equal to another vector.

        :param other: the other vector to compare to this vector
        :return: True if the vectors are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        Returns a string representation of this vector.

        :return: a string representation of the vector
        """
        return f"Vec2i({self.x}, {self.y})"

    def __getitem__(self, index: int) -> int:
        """
        Returns the component of the vector at the given index.

        :param index: the index of the component to retrieve (0 for x, 1 for y)
        :return: the component of the vector at the given index
        """
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vec2i index out of range")

    def length(self) -> float:
        """
        Returns the length of this vector.

        :return: the length of the vector
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __neg__(self) -> 'Vec2i':
        """
        Returns the negation of this vector.

        :return: the negation of the vector
        """
        return Vec2i(-self.x, -self.y)
