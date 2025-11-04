from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import ToggleController, IsPressedController


def get_post_processing_params():
    """
    Get the list of post-processing parameters
    
    Returns:
        List of Param objects for post-processing effects
    """
    post_params = []
    
    # Color inversion parameter
    invert_param = Param(
        name='uInvertColors',
        button=Button.LEFT_CUE_1,
        controller=ToggleController()
    )
    post_params.append(invert_param)
    
    # Wave effect parameter
    waves_x_param = Param(
        name='uWavesX',
        button=Button.LEFT_MINUS,
        controller=IsPressedController()
    )
    post_params.append(waves_x_param)

    wave_y_param = Param(
        name='uWavesY',
        button=Button.LEFT_PLUS,
        controller=IsPressedController()
    )
    post_params.append(wave_y_param)
    
    return post_params

