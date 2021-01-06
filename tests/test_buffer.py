import pytest

from shared_cbuff import buffer
from shared_cbuff import errors


SCB_1_A = buffer.SharedCircularBuffer("test_buffer_1", create=True)
SCB_1_B = buffer.SharedCircularBuffer("test_buffer_1")


def test_push_raises_when_write_not_permitted():
    with pytest.raises(errors.WriteOperationsForbidden) as exc_info:
        SCB_1_B.push(10)
    assert exc_info.type is errors.WriteOperationsForbidden


def test_popitem_raises_when_read_not_permitted():
    with pytest.raises(errors.ReadOperationsForbidden) as exc_info:
        SCB_1_A.popitem()
    assert exc_info.type is errors.ReadOperationsForbidden


def test_popmany_raises_when_read_not_permitted():
    with pytest.raises(errors.ReadOperationsForbidden) as exc_info:
        SCB_1_A.popmany(2)
    assert exc_info.type is errors.ReadOperationsForbidden


def test_push_adds_to_buffer():
    SCB_1_A.push(10)
    assert SCB_1_B.popitem() == 10


def test_more_than_length_items_can_be_pushed_to_buffer():
    SCB_1_A.push(10)
    SCB_1_A.push(10)
    SCB_1_A.push(10)


def test_popmany_returns_list_of_integers():
    out = SCB_1_B.popmany(2)
    assert isinstance(out, list)
    assert out[0] == 10


def test_pushing_more_than_length_overwrites_previous_value():
    SCB_1_A.push(10)
    SCB_1_A.push(10)
    SCB_1_A.push(50)
    assert SCB_1_B.popitem() == 50
    SCB_1_B.popmany(2)
