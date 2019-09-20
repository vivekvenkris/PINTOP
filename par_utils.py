from orbit_utils import Orbit
from utils import *
import numpy as np


class ParFile(object):
    def __init__(self, file_name):

        self.parameters = []

        self.file_name = file_name
        par_file = open(file_name)

        lines = par_file.readlines()

        for line in lines:

            parameter = Parameter(line)

            if parameter.is_valid():
                self.parameters.append(parameter)

        self.parameters = np.array(self.parameters)
        self.orbit = Orbit(self)

    def __str__(self):
        return str(self.parameters)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return next((i.value for i in self.parameters if i == item), None)


class Parameter(object):

    def get_value(self, chunk):
        try:
            self.value = float(chunk)
        except:
            self.value = str(chunk)

    @classmethod
    def create_instance(cls, name, value, error):
        parameter = Parameter(name + " " + str(value) + " " + str(error))

    def __init__(self, line):
        self.line = line
        chunks = line.split()
        self.name = chunks[0]
        self.value = None
        self.error = None
        self.valid = True
        length = len(chunks)

        if length == 0:
            self.valid = False

        if length == 2:  # can only be name and value
            self.get_value(chunks[1])

        elif length == 3:  # can be name value fit or name value error

            if chunks[2] == 1:  # name value fit
                log_str(
                    "ignoring fit flag column for " + self.name +
                    ". Provide 1.0 if this is the error on the parameter.")
            else:
                self.error = float(chunks[2])

        elif length == 4:  # name value fit error
            self.get_value(chunks[1])
            self.error = float(chunks[3])
        else:
            # log_str("Ignoring parameter because there are way too many columns, "
            #         "possibly irrelevant for this software:" + line)
            self.valid = False

    def is_valid(self):
        return self.valid

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Parameter):
            return other.name == self.name
        elif isinstance(other, str):
            return self.name == other
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.name)
