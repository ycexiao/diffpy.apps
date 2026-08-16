import uuid
from collections import OrderedDict

import numpy
from diffpy.srfit.fitbase import (
    FitRecipe,
    Profile,
)
from scipy.optimize import leastsq

from diffpy.apps.refinebase.parametric_model import (
    ParametricModel,
)


class RefinementSession:
    def __init__(self):
        self.recipes = OrderedDict()
        self.profiles = OrderedDict()
        self.models = OrderedDict()

    def add_profile(self, profile: Profile, profile_name: str = None):
        if profile in self.profiles.values():
            raise ValueError("Profile already exists in the session.")
        if profile_name is None:
            profile_name = str(uuid.uuid4())
        self.profiles[profile_name] = profile

    def add_model(self, model: ParametricModel):
        if model in self.models.values():
            raise ValueError("Model already exists in the session.")
        self.models[model.name] = model

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
