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


from twisted.trial import unittest
from pixelated.support.markov import MarkovGenerator
import random


SAMPLE_TEXT = 'One two three four'


class MarkovGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.random = random.Random(0)

    def test_starts_with_capital_case_workd(self):
        gen = MarkovGenerator(['lower Upper smaller Capital'], random=self.random)

        result = gen.generate(1)

        self.assertTrue(result.startswith('Upper'))

    def test_aborts_if_no_upper_letter_word_found(self):
        gen = MarkovGenerator(['all lower case'], random=self.random)

        self.assertRaises(ValueError, gen.generate, 1)

    def test_generate(self):
        gen = MarkovGenerator([SAMPLE_TEXT], random=self.random)

        result = gen.generate(3)

        self.assertEqual('One two three', result)

    def test_minimum_three_words(self):
        self.assertRaises(ValueError, MarkovGenerator([]).generate, 1)
        self.assertRaises(ValueError, MarkovGenerator, ['1'])
        self.assertRaises(ValueError, MarkovGenerator, ['1', '2'])
        self.assertRaises(ValueError, MarkovGenerator, ['1', '2', '3'])

    def test_add_paragraph_on_empty_chain(self):
        gen = MarkovGenerator([SAMPLE_TEXT], random=self.random, add_paragraph_on_empty_chain=True)

        result = gen.generate(5)

        self.assertEqual('One two three four \n\n One', result)

    def test_multiple_inputs(self):
        gen = MarkovGenerator([SAMPLE_TEXT, 'Five Six seven eight'], random=self.random)

        result = gen.generate(3)

        self.assertEqual('Five Six seven', result)

    def test_add(self):
        gen = MarkovGenerator([], random=self.random)

        gen.add(SAMPLE_TEXT)
        result = gen.generate(3)

        self.assertEqual('One two three', result)

    def test_multiple_word_occurences(self):
        gen = MarkovGenerator(['One Two One Three One Two One Four'], random=self.random)

        result = gen.generate(2)

        self.assertEqual('Two One', result)
