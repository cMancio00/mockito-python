from abc import ABC
import unittest

from mockito import mock, when
from mockito.inorder import InOrder


class Cat(ABC):
    def meow(self) -> str:
        pass

class Dog(ABC):
    def bark(self) -> str:
        pass

class Friends:
    def __init__(self, cat: Cat, dog: Dog):
        self.cat = cat
        self.dog = dog

    def cat_and_dog_sound(self) -> str:
        cat_sound: str = self.cat.meow()
        dog_sound: str = self.dog.bark()
        return f"{cat_sound}, {dog_sound}"



class InOrderTest(unittest.TestCase):

    def setUp(self):
        self.cat: Cat = mock(spec=Cat, strict=True)
        self.dog: Dog = mock(spec=Dog, strict=True)
        self.friends: Friends = Friends(self.cat, self.dog)

    def test_correct_order_declaration_should_pass(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        self.friends.cat_and_dog_sound()

        in_order.verify(self.cat).meow()
        in_order.verify(self.dog).bark()

    def test_incorrect_order_declaration_should_fail(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        self.friends.cat_and_dog_sound()

        with self.assertRaises(Exception):
            in_order.verify(self.dog).bark()
            in_order.verify(self.cat).meow()


if __name__ == '__main__':
    unittest.main()
