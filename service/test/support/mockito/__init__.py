#
# Copyright (c) 2015 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
from mockito.invocation import AnswerSelector as OriginalAnswerSelector, CompositeAnswer


class FunctionReturn(object):
    """
    Instead of returning a constant value a function is called
    """
    def __init__(self, function_answer):
        self.function_answer = function_answer

    def answer(self):
        return self.function_answer()


class AnswerSelector(OriginalAnswerSelector):

    def thenAnswer(self, answer_function):
        """mockito does not support the thenAnswer style. This method monkey patches it into the library"""
        if not self.answer:
            self.answer = CompositeAnswer(FunctionReturn(answer_function))
            self.invocation.stub_with(self.answer)
        else:
            self.answer.add(FunctionReturn(answer_function))

        return self
