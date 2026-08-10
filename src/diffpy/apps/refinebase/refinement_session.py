import uuid
from collections import OrderedDict

from scipy.optimize import leastsq

from diffpy.apps.refinebase.refinable_model import ParameterSetTree
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
        self.main_parameter_set = ParameterSet(name="main")
        self.calculators = OrderedDict()
        self.contributions = OrderedDict()
        self.recipes = OrderedDict()

    def add_parameterSet(self, parset):
        """Add a ParameterSet to the refinement session."""
        self.main_parameter_set.addParameterSet(parset)

    def add_parameter(self, parameter=None, name=None, delegates_to=None):
        """Add a Parameter to the refinement session."""
        self.main_parameter_set.addParameterSet(parameter)

    def add_function(self, name, expression=None, ns={}):
        pass

    def add_calculator(self, calculator):
        pass

    def add_case(
        self,
        name=None,
        profile=None,
        x=None,
        y=None,
        dy=None,
        expression=None,
        xname=None,
    ):
        if profile is None:
            profile = Profile()
            profile.x = x
            profile.y = y
            if dy is not None:
                profile.dy = dy
        contribution = FitContribution(name=name)
        contribution.setProfile(profile, xname=xname)
        contribution.setEquation(expression)
        self.main_parameter_set.addParameterSet(contribution)
        self.contributions[name] = contribution

    def refine(
        self,
        case_names,
        case_weights,
        var_names,
        initial_values,
        id=uuid.uuid4(),
    ):
        # Initialize the recipe
        recipe = FitRecipe()
        self.recipes[id] = recipe
        for name, weight in zip(case_names, case_weights):
            recipe.addContribution(self.contributions[name], weight=weight)
        # Add variables
        temp_parameter_tree = ParameterSetTree(self.main_parameter_set)
        for i, name in enumerate(var_names):
            recipe.addVar(
                temp_parameter_tree.graph.nodes[name]["parameter"],
                value=initial_values[i],
                name=name,
            )
        # Refine the recipe
        recipe.fix("all")
        for name in var_names:
            recipe.free(name)
            leastsq(recipe.residual, recipe.values)

    def clear(self, level=None):
        if level is None:
            level = 1

        if level <= 1:
            self.main_parameter_set = ParameterSet(name="main")
        if level <= 2:
            self.contributions = OrderedDict()
        if level <= 3:
            self.recipe = OrderedDict()
