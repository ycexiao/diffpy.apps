from collections import OrderedDict

from scipy.optimize import leastsq

from diffpy.srfit.fitbase import FitContribution, FitRecipe, Profile
from diffpy.srfit.fitbase.parameterset import ParameterSet


class RefinementSession:
    """
    A refinement session class that manages the refinement process.

    Attributes
    ----------
    variables : list of Variable
        The list of variables in the refinement session.
    loss_functions : list of callable
        The list of loss functions in the refinement session.
    loss_function : callable
        The loss function for the refinement session.

    Methods
    -------
    register_loss_function()
        Register the loss function for refinement.
    register_master_loss_function()
        Register the master loss function for refinement.
    refine()
        Perform the refinement.
    """

    def __init__(self):
        self.main_parameter_set = ParameterSet(name="main_parameter_set")
        self.calculators = []
        self.contributions = OrderedDict()

    def add_parameterSet(self, parset):
        """Add a ParameterSet to the refinement session."""
        self.main_parameter_set.addParameterSet(parset)

    def add_parameter(self, parameter):
        """Add a Parameter to the refinement session."""
        self.main_parameter_set.addParameter(parameter)

    def add_function(self, name, expression=None, ns={}):
        pass

    def add_calculator(self, calculator):
        pass

    def add_profile(self, name=None, profile=None, x=None, y=None, dy=None):
        if profile is None:
            profile = Profile()
            profile.x = x
            profile.y = y
            if dy is not None:
                profile.dy = dy
        contribution = FitContribution(name=name)
        contribution.setProfile(profile, xname=profile.x.name)
        self.contributions[name] = contribution

    def set_profile_equation(self, profile_name, expression):
        self.contributions[profile_name].setEquation(expression)

    def set_profile_weights(self, names, weights):
        self.recipe = FitRecipe()
        for name, weight in zip(names, weights):
            self.recipe.addContribution(
                self.contributions[name], weight=weight
            )

    def refine(self, var_names, initial_values):
        for name, value in zip(var_names, initial_values):
            self.main_parameter_set.parameters[name].setValue(value)
        for name in var_names:
            self.recipe.addVar(self.main_parameter_set.parameters[name])
        self.recipe.fix("all")
        for name in var_names:
            self.recipe.free(name)
            leastsq(self.recipe.residual, self.recipe.values)
