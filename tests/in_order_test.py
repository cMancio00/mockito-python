import pytest

from mockito import (mock, when, VerificationError,
                     verifyZeroInteractions, ensureNoUnverifiedInteractions)
from mockito.inorder import InOrder
from mockito.mock_registry import mock_registry

def test_observing_the_same_mock_twice_should_raise():
    a = mock()
    with pytest.raises(ValueError) as e:
        InOrder([a, a])
    assert str(e.value) == f"The following Mocks are duplicated: {[a]}"

def test_correct_order_declaration_should_pass():
    cat = mock()
    dog = mock()

    in_order: InOrder = InOrder([cat, dog])
    cat.meow()
    dog.bark()

    in_order.verify(cat).meow()
    in_order.verify(dog).bark()


def test_incorrect_order_declaration_should_fail():
    dog = mock()
    cat = mock()

    in_order: InOrder = InOrder([cat, dog])
    dog.bark()
    cat.meow()

    with pytest.raises(VerificationError) as e:
        in_order.verify(cat).meow()
    assert str(e.value) == (f"Not the wanted mock! "
                            f"Called {mock_registry.mock_for(dog)}, "
                            f"but expected {mock_registry.mock_for(cat)}!")

def test_verifing_not_observed_mocks_should_raise():
    a = mock()
    b = mock()

    when(a).method().thenReturn("Calling a")
    when(b).other_method().thenReturn("Calling b")

    in_order: InOrder = InOrder([a])
    a.method()
    b.other_method()

    with pytest.raises(VerificationError) as e:
        in_order.verify(a).method()
        in_order.verify(b).other_method()
    assert str(e.value) == (f"Trying to verify ordered invocation "
                            f"of {b}, "
                            f"but no other invocations have been recorded.")

def test_can_use_other_verifications():
    a = mock()
    b = mock()
    to_ignore = mock()

    when(a).method().thenReturn("Calling a")
    when(b).other_method().thenReturn("Calling b")
    when(to_ignore).ignore().thenReturn("I must be ignored!")

    in_order: InOrder = InOrder([a, b])
    a.method()
    b.other_method()

    in_order.verify(a).method()
    in_order.verify(b).other_method()

    ensureNoUnverifiedInteractions(a)
    verifyZeroInteractions(to_ignore)

def test_can_verify_multiple_orders():
    a = mock()
    b = mock()

    when(a).method().thenReturn("Calling a")
    when(b).other_method().thenReturn("Calling b")

    in_order: InOrder = InOrder([a, b])
    a.method()
    b.other_method()
    a.method()

    in_order.verify(a).method()
    in_order.verify(b).other_method()
    in_order.verify(a).method()

def test_in_order_context_manager():
    a = mock()
    b = mock()

    when(a).method().thenReturn("Calling a")
    when(b).other_method().thenReturn("Calling b")

    with InOrder([a, b]) as in_order:
        a.method()
        b.other_method()

        in_order.verify(a)
        in_order.verify(b)


def test_in_order_context_manager_raises_if_mocks_are_not_verified():
    a = mock()
    b = mock()

    when(a).method().thenReturn("Calling a")
    when(b).other_method().thenReturn("Calling b")

    with pytest.raises(VerificationError) as e:
        with InOrder([a, b]) as in_order:
            a.method()
            b.other_method()

            in_order.verify(a)
    assert str(e.value) == (f"Some mocks have not been verified: "
                            f"{in_order.ordered_invocations}")
