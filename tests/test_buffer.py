import pytest

from shared_cbuff import buffer
from shared_cbuff import errors


@pytest.fixture()
def SCB_1():
    scb_a = buffer.SharedCircularBuffer("test_buffer_1", create=True)
    scb_b = buffer.SharedCircularBuffer("test_buffer_1")
    yield (scb_a, scb_b)
    scb_b.cleanup()
    scb_a.cleanup()


@pytest.fixture()
def SCB_2():
    scb_a = buffer.SharedCircularBuffer("test_buffer_1", create=True, item_size=3)
    scb_b = buffer.SharedCircularBuffer("test_buffer_1", item_size=3)
    yield (scb_a, scb_b)
    scb_b.cleanup()
    scb_a.cleanup()


@pytest.fixture()
def SCB_3():
    scb_a = buffer.SharedCircularBuffer("test_buffer_1", create=True, item_size=4, length=128)
    scb_b = buffer.SharedCircularBuffer("test_buffer_1", item_size=4, length=128)
    yield (scb_a, scb_b)
    scb_b.cleanup()
    scb_a.cleanup()


def test_push_raises_when_write_not_permitted(SCB_1):
    scb_a, scb_b = SCB_1
    with pytest.raises(errors.WriteOperationsForbidden) as exc_info:
        scb_b.push(10)
    assert exc_info.type is errors.WriteOperationsForbidden


def test_popitem_raises_when_read_not_permitted(SCB_1):
    scb_a, scb_b = SCB_1
    with pytest.raises(errors.ReadOperationsForbidden) as exc_info:
        scb_a.popitem()
    assert exc_info.type is errors.ReadOperationsForbidden


def test_popmany_raises_when_read_not_permitted(SCB_1):
    scb_a, scb_b = SCB_1
    with pytest.raises(errors.ReadOperationsForbidden) as exc_info:
        scb_a.popmany(2)
    assert exc_info.type is errors.ReadOperationsForbidden


def test_push_adds_to_buffer(SCB_1):
    scb_a, scb_b = SCB_1
    scb_a.push(10)
    assert scb_b.popitem() == 10


def test_more_than_length_items_can_be_pushed_to_buffer(SCB_1):
    scb_a, scb_b = SCB_1
    scb_a.push(10)
    scb_a.push(10)
    scb_a.push(10)
    scb_b.popmany(3)


def test_popmany_returns_list_of_integers(SCB_1):
    scb_a, scb_b = SCB_1
    scb_a.push(10)
    out = scb_b.popmany(2)
    assert isinstance(out, list)
    assert out[0] == 10


def test_pushing_more_than_length_overwrites_previous_value(SCB_1):
    scb_a, scb_b = SCB_1
    scb_a.push(10)
    scb_a.push(10)
    scb_a.push(50)
    assert scb_b.popitem() == 50
    scb_b.popmany(3)


def test_item_size_greater_than_1_can_be_pushed_and_popped(SCB_2):
    scb_a, scb_b = SCB_2
    scb_a.push(10)
    assert scb_b.popitem() == 10
    scb_a.push(500)
    assert scb_b.popitem() == 500


def test_read_works_for_write_addresses_longer_than_1_byte(SCB_3):
    scb_a, scb_b = SCB_3
    for i in range(127):
        scb_a.push(i)
    assert len(scb_b.popmany(127)) == 127


def test_error_raised_when_buffer_attempted_to_be_created_but_already_exists(SCB_1):
    with pytest.raises(errors.BufferAlreadyCreated) as exc_info:
        _scb = buffer.SharedCircularBuffer("test_buffer_1", create=True)
    assert exc_info.type is errors.BufferAlreadyCreated
