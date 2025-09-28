from abc import ABC
import unittest

from assertpy import assert_that

from mockito import mock, when
from mockito.inorder import InOrder


class Cat(ABC):
    def meow(self) -> str:
        pass

class Dog(ABC):
    def bark(self) -> str:
        pass


class InOrderTest(unittest.TestCase):

    def setUp(self):
        self.cat: Cat = mock(spec=Cat, strict=True)
        self.dog: Dog = mock(spec=Dog, strict=True)

        self.greet = lambda cat, dog: f"{cat.meow()}, {dog.bark()}"

    def test_inOrder_should_observe_single_mock(self):

        in_order: InOrder = InOrder([self.cat])
        self.assertIn(self.cat, in_order.mocks)

    def test_inOrder_should_observe_several_mocks(self):

        in_order: InOrder = InOrder([self.cat, self.dog])
        assert_that(in_order.mocks).contains_only(self.cat, self.dog)

    def test_observing_the_same_mock_twice_should_raise(self):
        with self.assertRaises(ValueError) as e:
            InOrder([self.cat, self.cat])
        assert_that(str(e.exception)).is_equal_to(f"The following Mocks are duplicated: {[self.cat]}")

    def test_calling_a_function_should_just_record_the_mocks_call(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        to_ignore = mock()
        when(to_ignore).meow().thenReturn("I must be ignored!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        self.greet(self.cat, self.dog)
        to_ignore.meow()

        assert_that(in_order.ordered_invocations).is_length(2)
        assert_that(in_order.ordered_invocations).does_not_contain(to_ignore)


    def test_correct_order_declaration_should_pass(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        self.greet(self.cat, self.dog)

        in_order.verify(self.cat).meow()
        in_order.verify(self.dog).bark()

    def test_incorrect_order_declaration_should_fail(self):
        when(self.cat).meow().thenReturn("Meow!")
        when(self.dog).bark().thenReturn("Bark!")

        in_order: InOrder = InOrder([self.cat, self.dog])
        self.greet(self.cat, self.dog)

        with self.assertRaises(Exception):
            in_order.verify(self.dog).bark()
            in_order.verify(self.cat).meow()


if __name__ == '__main__':
    unittest.main()
