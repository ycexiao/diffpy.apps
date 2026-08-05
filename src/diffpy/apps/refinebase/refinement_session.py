from diffpy.srfit.fitbase.parameter import ParameterSet


class RefinementSession(ParameterSet):
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
        self.loss_functions = []
        self.loss_function = None

    def _prepare_variables(self):
        """Prepare variables for refinement.

        Convert the literals into builders before make the equation"""
        pass

    def register_loss_function(self):
        """Register the loss function for refinement."""
        pass

    def set_master_loss_function(self, name):
        """set the master loss function for refinement."""
        self.master_loss_function = name

    def refine(self):
        """Perform the refinement."""
        pass
