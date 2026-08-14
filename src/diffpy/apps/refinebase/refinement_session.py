import uuid
from collections import OrderedDict

import numpy
from diffpy.srfit.fitbase import FitRecipe
from scipy.optimize import leastsq


class RefinementSession:
    def __init__(self):
        self.recipes = OrderedDict()

    def solve(
        self,
        profiles,
        models,
        variables,
        id=uuid.uuid4(),
        weights=None,
        initial_values=None,
    ):
        recipe = FitRecipe()
        self.recipes[id] = recipe
        if weights is None:
            weights = numpy.ones(len(profiles)) / len(profiles)
        for i in range(len(models)):
            models[i].set_profile(profiles[i])
            recipe.addContribution(models[i]._contribution, weight=weights[i])
        # Add variables
        if initial_values is not None:
            for var, val in zip(variables, initial_values):
                var.value = val
        for var in variables:
            recipe.addVar(var)
        # Refine the recipe
        recipe.fix("all")
        recipe.residual()
        for i in range(len(variables)):
            recipe.free(variables[i].name)
            leastsq(recipe.residual, recipe.getValues())
