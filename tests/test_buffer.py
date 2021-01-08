# -*- coding: utf-8 -*-
# Copyright (c) 2021 tandemdude
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
    _, scb_b = SCB_1
    with pytest.raises(errors.WriteOperationsForbidden) as exc_info:
        scb_b.push(10)
    assert exc_info.type is errors.WriteOperationsForbidden


def test_popitem_raises_when_read_not_permitted(SCB_1):
    scb_a, _ = SCB_1
    with pytest.raises(errors.ReadOperationsForbidden) as exc_info:
        scb_a.popitem()
    assert exc_info.type is errors.ReadOperationsForbidden


def test_popmany_raises_when_read_not_permitted(SCB_1):
    scb_a, _ = SCB_1
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


def test_SharedCircularBuffer_str_operator(SCB_1):
    scb_a, scb_b = SCB_1
    assert str(scb_a) == f"SharedCircularBuffer ({scb_a.name})"
    assert str(scb_b) == f"SharedCircularBuffer ({scb_a.name}) (0.00% full)"


def test_usage_returns_0_when_empty(SCB_1):
    _, scb_b = SCB_1
    assert scb_b.usage == 0


def test_usage_returns_1_when_item_present(SCB_1):
    scb_a, scb_b = SCB_1
    scb_a.push(10)
    assert scb_b.usage == 1


def test_raises_ValueError_when_length_less_than_2():
    with pytest.raises(ValueError) as exc_info:
        _scb = buffer.SharedCircularBuffer("test_buffer_1", length=1)
    assert exc_info.type is ValueError


def test_usage_returns_correct_number_when_write_pointer_behind_read_pointer(SCB_3):
    scb_a, scb_b = SCB_3
    for _ in range(127):
        scb_a.push(10)
    for _ in range(10):
        scb_b.popitem()
    for _ in range(5):
        scb_a.push(10)
    assert scb_b.usage == 122
