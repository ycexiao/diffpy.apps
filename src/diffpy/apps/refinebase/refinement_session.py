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
        self.recipes_dict = OrderedDict()
        self.profiles_dict = OrderedDict()
        self.models_dict = OrderedDict()

    def add_profile(self, profile: Profile, profile_name: str = None):
        if profile in self.profiles_dict.values():
            raise ValueError("Profile already exists in the session.")
        if profile_name is None:
            profile_name = str(uuid.uuid4())
        self.profiles_dict[profile_name] = profile

    def add_model(self, model: ParametricModel):
        if model in self.models_dict.values():
            raise ValueError("Model already exists in the session.")
        self.models_dict[model.name] = model

    def remove_profile(self, profile_name: str):
        if profile_name not in self.profiles_dict:
            raise ValueError(f"Profile with ID {profile_name} does not exist.")
        del self.profiles_dict[profile_name]

    def remove_model(self, model_name: str):
        if model_name not in self.models_dict:
            raise ValueError(f"Model with ID {model_name} does not exist.")
        del self.models_dict[model_name]

    def get_variable(self, variable_name):
        objs = variable_name.split(".")
        if objs[0] not in self.models_dict:
            raise ValueError(f"Model '{objs[0]}' not found in the session.")
        if variable_name not in self.models_dict[objs[0]].parameters:
            raise ValueError(
                f"Variable '{variable_name}' not found in the model '{objs[0]}'."
            )
        return self.models_dict[objs[0]].parameters[variable_name]

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
        self.recipes_dict[id] = recipe
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
            recipe.add_variable(var)
        # Refine the recipe
        recipe.fix("all")
        recipe.residual()
        for i in range(len(variables)):
            recipe.free(variables[i].name)
            leastsq(recipe.residual, recipe.getValues())
