from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import ToggleController, IsPressedController, NormalizedController


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
    
    # Individual channel inversion parameters
    invert_red_param = Param(
        name='uInvertRed',
        button=Button.LEFT_CUE_2,
        controller=ToggleController()
    )
    post_params.append(invert_red_param)
    
    invert_green_param = Param(
        name='uInvertGreen',
        button=Button.LEFT_CUE_3,
        controller=ToggleController()
    )
    post_params.append(invert_green_param)
    
    invert_blue_param = Param(
        name='uInvertBlue',
        button=Button.LEFT_CUE_4,
        controller=ToggleController()
    )
    post_params.append(invert_blue_param)
    
    # HSV space inversion parameters
    invert_hue_param = Param(
        name='uInvertHue',
        button=Button.RIGHT_CUE_1,
        controller=ToggleController()
    )
    post_params.append(invert_hue_param)
    
    invert_saturation_param = Param(
        name='uInvertSaturation',
        button=Button.RIGHT_CUE_2,
        controller=ToggleController()
    )
    post_params.append(invert_saturation_param)
    
    invert_value_param = Param(
        name='uInvertValue',
        button=Button.RIGHT_CUE_3,
        controller=ToggleController()
    )
    post_params.append(invert_value_param)
    
    # Wave effect parameter
    waves_x_param = Param(
        name='uWavesX',
        button=Button.LEFT_PITCH,
        controller=NormalizedController(min_value =-50.0, max_value=50.0, is_pitch=True)
    )
    post_params.append(waves_x_param)

    wave_y_param = Param(
        name='uWavesY',
        button=Button.RIGHT_PITCH,
        controller=NormalizedController(min_value =-50.0, max_value=50.0, is_pitch=True)
    )
    post_params.append(wave_y_param)
    
    return post_params

