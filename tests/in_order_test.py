import pytest

from mockito import mock, when, VerificationError
from mockito.inorder import InOrder

def test_observing_the_same_mock_twice_should_raise():
    a = mock()
    with pytest.raises(ValueError) as e:
        InOrder(a, a)
    assert str(e.value) == ("The following Mocks are duplicated: "
                            "['Mock<Dummy>']")

def test_correct_order_declaration_should_pass():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    dog.bark()

    in_order.verify(cat).meow()
    in_order.verify(dog).bark()


def test_incorrect_order_declaration_should_fail():
    dog = mock()
    cat = mock()

    in_order: InOrder = InOrder(cat, dog)
    dog.bark()
    cat.meow()

    with pytest.raises(VerificationError) as e:
        in_order.verify(cat).meow()
    assert str(e.value) == (
        "InOrder verification error! "
        "Wanted a call from Mock<Dummy>, but got "
        "bark() from Mock<Dummy> instead!"
    )


def test_verifing_not_observed_mocks_should_raise():
    cat = mock()
    to_ignore = mock()

    in_order: InOrder = InOrder(cat)
    to_ignore.bark()

    with pytest.raises(VerificationError) as e:
        in_order.verify(to_ignore).bark()
    assert str(e.value) == (
        f"InOrder Verification Error! "
        f"Unexpected call from not observed {to_ignore}."
    )

def test_can_verify_multiple_orders():
    cat = mock()
    dog = mock()


    in_order: InOrder = InOrder(cat, dog)
    cat.meow()
    dog.bark()
    cat.meow()

    in_order.verify(cat).meow()
    in_order.verify(dog).bark()
    in_order.verify(cat).meow()

def test_in_order_context_manager():
    a = mock()
    b = mock()

    when(a).method().thenReturn("Calling a")
    when(b).other_method().thenReturn("Calling b")

    with InOrder(a, b) as in_order:
        a.method()
        b.other_method()

        in_order.verify(a)
        in_order.verify(b)


def test_exiting_context_manager_should_detatch_mocks():
    cat = mock()
    dog = mock()

    with InOrder(cat, dog) as in_order:
        cat.meow()
        dog.bark()

        in_order.verify(cat).meow()
        in_order.verify(dog).bark()
