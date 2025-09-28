# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import annotations

from collections import Counter
from typing import List, Any

from .mocking import Mock
from .mockito import verify as verify_main
from .mock_registry import mock_registry
from .observer import Observer


def verify(object, *args, **kwargs):
    kwargs['inorder'] = True
    return verify_main(object, *args, **kwargs)


class InOrder(Observer[Mock]):

    def __init__(self, mocks: List[Any]):
        counter = Counter(mocks)
        duplicates = [fruit for fruit, freq in counter.items() if freq > 1]
        if duplicates:
            raise ValueError(f"The following Mocks are duplicated: {duplicates}")
        self._mocks = mocks

        for mock in self._mocks:
            mock_registry.mock_for(mock).attach(self)

        self.ordered_invocations = []

    @property
    def mocks(self):
        return self._mocks

    def update(self, subject: Mock) -> None:
        self.ordered_invocations.append(
            {"mock": subject, "invocation": subject.invocations[-1]})

    def verify(self, mock, *args, **kwargs):
        ordered_invocation = self.ordered_invocations.pop(0)
        actual_mock = ordered_invocation['mock']
        wanted_mock = mock_registry.mock_for(mock)
        if actual_mock != wanted_mock:
            raise Exception(
                f"Not the wanted mock! Got {actual_mock}, wanted {wanted_mock}"
            )
        return verify_main(obj=mock, *args, **kwargs)

