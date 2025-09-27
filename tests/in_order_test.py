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

def greet(cat: Cat, dog: Dog) -> str:
    return f"{cat.meow()}, {dog.bark()}"

class InOrderTest(unittest.TestCase):

    def setUp(self):
        self.cat: Cat = mock(spec=Cat, strict=True)
        self.dog: Dog = mock(spec=Dog, strict=True)

    def test_inOrder_should_observe_single_mock(self):

        in_order: InOrder = InOrder([self.cat])
        self.assertIn(self.cat, in_order.mocks)

    def test_inOrder_should_observe_several_mocks(self):

        in_order: InOrder = InOrder([self.cat, self.dog])
        self.assertIn(self.cat, in_order.mocks)
        self.assertIn(self.dog, in_order.mocks)

    def test_observing_the_same_mock_twice_should_not_be_added(self):

        in_order: InOrder = InOrder([self.cat, self.cat])
        self.assertEqual(len(in_order.mocks), 1)
        self.assertIn(self.cat, in_order.mocks)


    def test_correct_order_declaration_should_pass(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        greet(self.cat, self.dog)

        in_order.verify(self.cat).meow()
        in_order.verify(self.dog).bark()

    def test_incorrect_order_declaration_should_fail(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        greet(self.cat, self.dog)

        with self.assertRaises(Exception):
            in_order.verify(self.dog).bark()
            in_order.verify(self.cat).meow()


if __name__ == '__main__':
    unittest.main()
